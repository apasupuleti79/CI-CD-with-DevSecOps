#!/usr/bin/env python3
"""
Health Check Script for DevSecOps Application
Performs comprehensive health checks and reports status.
"""

import argparse
import json
import requests
import sys
import time
from datetime import datetime

def check_application_health(base_url, timeout=30):
    """Check application health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=timeout)
        if response.status_code == 200:
            health_data = response.json()
            return {
                'status': 'healthy',
                'response_time': response.elapsed.total_seconds(),
                'data': health_data
            }
        else:
            return {
                'status': 'unhealthy',
                'error': f"HTTP {response.status_code}",
                'response_time': response.elapsed.total_seconds()
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'error': str(e),
            'response_time': None
        }

def check_api_endpoints(base_url, timeout=30):
    """Check critical API endpoints"""
    endpoints = [
        '/api/info',
        '/api/secure-data?user_id=123'
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=timeout)
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_length': len(response.content)
            }
        except requests.exceptions.RequestException as e:
            results[endpoint] = {
                'error': str(e),
                'status_code': None,
                'response_time': None
            }
    
    return results

def check_security_headers(base_url, timeout=30):
    """Check for security headers"""
    try:
        response = requests.get(base_url, timeout=timeout)
        headers = response.headers
        
        security_headers = {
            'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
            'X-Frame-Options': headers.get('X-Frame-Options'),
            'X-XSS-Protection': headers.get('X-XSS-Protection'),
            'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
            'Content-Security-Policy': headers.get('Content-Security-Policy'),
            'Referrer-Policy': headers.get('Referrer-Policy')
        }
        
        missing_headers = [k for k, v in security_headers.items() if v is None]
        
        return {
            'headers': security_headers,
            'missing_headers': missing_headers,
            'security_score': (6 - len(missing_headers)) / 6 * 100
        }
    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'security_score': 0
        }

def performance_test(base_url, iterations=10, timeout=30):
    """Perform basic performance testing"""
    response_times = []
    errors = 0
    
    for i in range(iterations):
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}/health", timeout=timeout)
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
            else:
                errors += 1
        except requests.exceptions.RequestException:
            errors += 1
    
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        success_rate = (iterations - errors) / iterations * 100
    else:
        avg_response_time = None
        min_response_time = None
        max_response_time = None
        success_rate = 0
    
    return {
        'iterations': iterations,
        'errors': errors,
        'success_rate': success_rate,
        'avg_response_time': avg_response_time,
        'min_response_time': min_response_time,
        'max_response_time': max_response_time
    }

def generate_health_report(environment, base_url):
    """Generate comprehensive health report"""
    print(f"🏥 Running health checks for {environment} environment...")
    
    # Perform health checks
    app_health = check_application_health(base_url)
    api_checks = check_api_endpoints(base_url)
    security_headers = check_security_headers(base_url)
    performance = performance_test(base_url)
    
    # Compile report
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'environment': environment,
        'base_url': base_url,
        'application_health': app_health,
        'api_endpoints': api_checks,
        'security_headers': security_headers,
        'performance': performance,
        'overall_status': 'healthy'  # Will be updated based on checks
    }
    
    # Determine overall status
    issues = []
    
    if app_health['status'] != 'healthy':
        issues.append('Application health check failed')
        report['overall_status'] = 'unhealthy'
    
    # Check API endpoints
    for endpoint, result in api_checks.items():
        if result.get('status_code') != 200:
            issues.append(f"API endpoint {endpoint} is not responding correctly")
    
    # Check security headers
    if security_headers.get('security_score', 0) < 80:
        issues.append('Security headers score is below threshold')
    
    # Check performance
    if performance['success_rate'] < 95:
        issues.append('Success rate is below 95%')
    
    if performance['avg_response_time'] and performance['avg_response_time'] > 2.0:
        issues.append('Average response time is above 2 seconds')
    
    if issues:
        report['overall_status'] = 'degraded' if len(issues) <= 2 else 'unhealthy'
        report['issues'] = issues
    
    # Save report
    report_filename = f"health-report-{environment}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n📊 Health Check Summary for {environment.upper()}")
    print(f"Overall Status: {report['overall_status'].upper()}")
    print(f"Application Health: {app_health['status'].upper()}")
    print(f"Security Score: {security_headers.get('security_score', 0):.1f}%")
    print(f"Performance Success Rate: {performance['success_rate']:.1f}%")
    
    if 'avg_response_time' in performance and performance['avg_response_time']:
        print(f"Average Response Time: {performance['avg_response_time']:.3f}s")
    
    if issues:
        print(f"\n⚠️ Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
    
    print(f"\n📄 Full report saved to: {report_filename}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Health check script for DevSecOps application')
    parser.add_argument('--environment', required=True, choices=['staging', 'production'], 
                       help='Environment to check')
    parser.add_argument('--url', help='Base URL of the application')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    # Determine base URL
    if args.url:
        base_url = args.url
    else:
        # Default URLs based on environment
        if args.environment == 'staging':
            base_url = 'http://staging.company.com'  # Update with actual staging URL
        else:
            base_url = 'https://production.company.com'  # Update with actual production URL
    
    # Generate health report
    report = generate_health_report(args.environment, base_url)
    
    # Exit with appropriate code
    if report['overall_status'] == 'healthy':
        print("\n✅ All health checks passed!")
        sys.exit(0)
    elif report['overall_status'] == 'degraded':
        print("\n⚠️ Some issues detected but service is functional")
        sys.exit(1)
    else:
        print("\n❌ Critical health check failures detected!")
        sys.exit(2)

if __name__ == "__main__":
    main()
