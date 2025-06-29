#!/usr/bin/env python3
"""
DevSecOps Pipeline Verification Script
This script performs comprehensive testing of the DevSecOps pipeline components.
"""

import subprocess
import sys
import os
import json
import time
import requests
from pathlib import Path

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestRunner:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }
        
    def log(self, message, level='INFO'):
        colors = {
            'INFO': Colors.CYAN,
            'SUCCESS': Colors.GREEN,
            'WARNING': Colors.YELLOW,
            'ERROR': Colors.RED,
            'HEADER': Colors.PURPLE + Colors.BOLD
        }
        color = colors.get(level, Colors.WHITE)
        print(f"{color}[{level}]{Colors.END} {message}")
    
    def run_command(self, command, description, timeout=300):
        """Run a command and return success status"""
        self.log(f"Running: {description}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                self.log(f"✅ {description} - PASSED", 'SUCCESS')
                self.results['passed'] += 1
                self.results['tests'].append({
                    'name': description,
                    'status': 'PASSED',
                    'output': result.stdout[:500] if result.stdout else 'No output'
                })
                return True
            else:
                self.log(f"❌ {description} - FAILED", 'ERROR')
                self.log(f"Error: {result.stderr}", 'ERROR')
                self.results['failed'] += 1
                self.results['tests'].append({
                    'name': description,
                    'status': 'FAILED',
                    'error': result.stderr,
                    'output': result.stdout
                })
                return False
        except subprocess.TimeoutExpired:
            self.log(f"⏰ {description} - TIMEOUT", 'WARNING')
            self.results['warnings'] += 1
            return False
        except Exception as e:
            self.log(f"💥 {description} - EXCEPTION: {str(e)}", 'ERROR')
            self.results['failed'] += 1
            return False
    
    def check_file_exists(self, file_path, description):
        """Check if a file exists"""
        if Path(file_path).exists():
            self.log(f"✅ {description} - File exists", 'SUCCESS')
            self.results['passed'] += 1
            return True
        else:
            self.log(f"❌ {description} - File missing: {file_path}", 'ERROR')
            self.results['failed'] += 1
            return False
    
    def test_http_endpoint(self, url, description, expected_status=200):
        """Test HTTP endpoint"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == expected_status:
                self.log(f"✅ {description} - HTTP {response.status_code}", 'SUCCESS')
                self.results['passed'] += 1
                return True
            else:
                self.log(f"❌ {description} - HTTP {response.status_code} (expected {expected_status})", 'ERROR')
                self.results['failed'] += 1
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ {description} - Connection failed: {str(e)}", 'ERROR')
            self.results['failed'] += 1
            return False

def test_prerequisites(runner):
    """Test system prerequisites"""
    runner.log("Testing Prerequisites", 'HEADER')
    
    # Test Python
    runner.run_command("python --version", "Python installation")
    
    # Test pip
    runner.run_command("pip --version", "Pip package manager")
    
    # Test Git (optional)
    runner.run_command("git --version", "Git version control")
    
    # Test Docker (optional)
    runner.run_command("docker --version", "Docker installation")

def test_python_environment(runner):
    """Test Python virtual environment and dependencies"""
    runner.log("Testing Python Environment", 'HEADER')
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        runner.log("Creating virtual environment...", 'INFO')
        runner.run_command("python -m venv venv", "Virtual environment creation")
    
    # Activate and install dependencies
    if sys.platform.startswith('win'):
        activate_cmd = "venv\\Scripts\\activate && "
    else:
        activate_cmd = "source venv/bin/activate && "
    
    runner.run_command(f"{activate_cmd}pip install -r requirements.txt", "Install dependencies")
    
    # Test imports
    runner.run_command(f"{activate_cmd}python -c \"import flask; print('Flask version:', flask.__version__)\"", "Flask import test")
    runner.run_command(f"{activate_cmd}python -c \"import pytest; print('Pytest version:', pytest.__version__)\"", "Pytest import test")

def test_application(runner):
    """Test the application functionality"""
    runner.log("Testing Application", 'HEADER')
    
    # Check source files exist
    runner.check_file_exists("src/app.py", "Main application file")
    runner.check_file_exists("tests/test_app.py", "Test file")
    
    # Run unit tests
    if sys.platform.startswith('win'):
        activate_cmd = "venv\\Scripts\\activate && "
    else:
        activate_cmd = "source venv/bin/activate && "
    
    runner.run_command(
        f"{activate_cmd}python -m pytest tests/ --cov=src --cov-report=xml --junitxml=test-results.xml -v",
        "Unit tests with coverage"
    )
    
    # Check test artifacts
    runner.check_file_exists("test-results.xml", "Test results XML")
    runner.check_file_exists("coverage.xml", "Coverage report XML")

def test_security_scans(runner):
    """Test security scanning tools"""
    runner.log("Testing Security Scans", 'HEADER')
    
    if sys.platform.startswith('win'):
        activate_cmd = "venv\\Scripts\\activate && "
    else:
        activate_cmd = "source venv/bin/activate && "
    
    # Install security tools if not available
    runner.run_command(f"{activate_cmd}pip install bandit safety", "Install security tools")
    
    # Run Bandit scan
    runner.run_command(
        f"{activate_cmd}bandit -r src/ -f json -o bandit-report.json",
        "Bandit security scan (JSON)"
    )
    
    runner.run_command(
        f"{activate_cmd}bandit -r src/ -f txt -o bandit-report.txt",
        "Bandit security scan (TXT)"
    )
    
    # Run Safety check
    runner.run_command(
        f"{activate_cmd}safety check --json --output safety-report.json",
        "Safety dependency check (JSON)"
    )
    
    runner.run_command(
        f"{activate_cmd}safety check --output safety-report.txt",
        "Safety dependency check (TXT)"
    )
    
    # Check security reports
    runner.check_file_exists("bandit-report.json", "Bandit JSON report")
    runner.check_file_exists("safety-report.json", "Safety JSON report")

def test_security_report_generation(runner):
    """Test security report generation"""
    runner.log("Testing Security Report Generation", 'HEADER')
    
    if sys.platform.startswith('win'):
        activate_cmd = "venv\\Scripts\\activate && "
    else:
        activate_cmd = "source venv/bin/activate && "
    
    # Generate security report
    runner.run_command(
        f"{activate_cmd}python security/generate_security_report.py",
        "Generate consolidated security report"
    )
    
    # Check generated reports
    runner.check_file_exists("security-reports/security-summary.html", "Security HTML report")
    runner.check_file_exists("security-reports/security-summary.json", "Security JSON report")

def test_docker_functionality(runner):
    """Test Docker functionality"""
    runner.log("Testing Docker Functionality", 'HEADER')
    
    # Check Dockerfile exists
    runner.check_file_exists("docker/Dockerfile", "Production Dockerfile")
    runner.check_file_exists("docker/docker-compose.yml", "Docker Compose file")
    
    # Test Docker build
    runner.run_command(
        "docker build -t my-devsecops-app:test -f docker/Dockerfile .",
        "Docker image build",
        timeout=600
    )
    
    # Test if image was created
    runner.run_command(
        "docker images my-devsecops-app:test",
        "Check Docker image exists"
    )

def test_application_endpoints(runner):
    """Test application endpoints (if running)"""
    runner.log("Testing Application Endpoints", 'HEADER')
    
    # Try to start application in background for testing
    if sys.platform.startswith('win'):
        activate_cmd = "venv\\Scripts\\activate && "
    else:
        activate_cmd = "source venv/bin/activate && "
    
    # Start application in background
    runner.log("Starting application for endpoint testing...", 'INFO')
    try:
        import threading
        import time
        
        # Start app in thread
        def start_app():
            subprocess.run(f"{activate_cmd}python src/app.py", shell=True, capture_output=True)
        
        app_thread = threading.Thread(target=start_app, daemon=True)
        app_thread.start()
        
        # Wait for app to start
        time.sleep(3)
        
        # Test endpoints
        runner.test_http_endpoint("http://localhost:5000/health", "Health endpoint")
        runner.test_http_endpoint("http://localhost:5000/api/info", "API info endpoint")
        runner.test_http_endpoint("http://localhost:5000/api/secure-data?user_id=123", "Secure data endpoint")
        runner.test_http_endpoint("http://localhost:5000/nonexistent", "404 error handling", 404)
        
    except Exception as e:
        runner.log(f"Could not test endpoints: {str(e)}", 'WARNING')
        runner.results['warnings'] += 1

def test_monitoring_scripts(runner):
    """Test monitoring and alerting scripts"""
    runner.log("Testing Monitoring Scripts", 'HEADER')
    
    # Check monitoring files exist
    runner.check_file_exists("monitoring/health_check.py", "Health check script")
    runner.check_file_exists("monitoring/setup_alerts.py", "Alert setup script")
    
    if sys.platform.startswith('win'):
        activate_cmd = "venv\\Scripts\\activate && "
    else:
        activate_cmd = "source venv/bin/activate && "
    
    # Test alert setup script
    runner.run_command(
        f"{activate_cmd}python monitoring/setup_alerts.py --deployment test-v1.0",
        "Alert configuration generation"
    )
    
    # Check generated monitoring files
    runner.check_file_exists("prometheus-alerts.yml", "Prometheus alerts configuration")
    runner.check_file_exists("grafana-dashboard.json", "Grafana dashboard configuration")

def test_kubernetes_manifests(runner):
    """Test Kubernetes manifest files"""
    runner.log("Testing Kubernetes Manifests", 'HEADER')
    
    # Check K8s files exist
    runner.check_file_exists("k8s/staging/deployment.yaml", "Staging deployment manifest")
    runner.check_file_exists("k8s/staging/service.yaml", "Staging service manifest")
    runner.check_file_exists("k8s/production/deployment.yaml", "Production deployment manifest")
    runner.check_file_exists("k8s/production/service.yaml", "Production service manifest")
    
    # Validate YAML syntax (if kubectl available)
    runner.run_command(
        "kubectl --dry-run=client apply -f k8s/staging/",
        "Validate staging manifests (dry-run)"
    )

def generate_test_report(runner):
    """Generate final test report"""
    runner.log("Generating Test Report", 'HEADER')
    
    total_tests = runner.results['passed'] + runner.results['failed'] + runner.results['warnings']
    success_rate = (runner.results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_tests': total_tests,
            'passed': runner.results['passed'],
            'failed': runner.results['failed'],
            'warnings': runner.results['warnings'],
            'success_rate': round(success_rate, 2)
        },
        'tests': runner.results['tests']
    }
    
    # Save report
    with open('test-verification-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    runner.log("TEST VERIFICATION SUMMARY", 'HEADER')
    print("="*60)
    runner.log(f"Total Tests: {total_tests}", 'INFO')
    runner.log(f"✅ Passed: {runner.results['passed']}", 'SUCCESS')
    runner.log(f"❌ Failed: {runner.results['failed']}", 'ERROR' if runner.results['failed'] > 0 else 'INFO')
    runner.log(f"⚠️  Warnings: {runner.results['warnings']}", 'WARNING' if runner.results['warnings'] > 0 else 'INFO')
    runner.log(f"📊 Success Rate: {success_rate:.1f}%", 'SUCCESS' if success_rate >= 90 else 'WARNING' if success_rate >= 70 else 'ERROR')
    
    if runner.results['failed'] == 0:
        runner.log("🎉 All critical tests passed! Pipeline is ready.", 'SUCCESS')
    else:
        runner.log("🔧 Some tests failed. Please review and fix issues before proceeding.", 'WARNING')
    
    runner.log(f"📄 Detailed report saved to: test-verification-report.json", 'INFO')

def main():
    """Main test execution"""
    print(f"\n{Colors.PURPLE}{Colors.BOLD}🧪 DevSecOps Pipeline Verification{Colors.END}")
    print(f"{Colors.PURPLE}{Colors.BOLD}====================================={Colors.END}\n")
    
    runner = TestRunner()
    
    # Run all test suites
    test_prerequisites(runner)
    print()
    
    test_python_environment(runner)
    print()
    
    test_application(runner)
    print()
    
    test_security_scans(runner)
    print()
    
    test_security_report_generation(runner)
    print()
    
    test_docker_functionality(runner)
    print()
    
    test_application_endpoints(runner)
    print()
    
    test_monitoring_scripts(runner)
    print()
    
    test_kubernetes_manifests(runner)
    print()
    
    # Generate final report
    generate_test_report(runner)
    
    # Exit with appropriate code
    if runner.results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
