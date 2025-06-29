#!/usr/bin/env python3
"""
Security Report Generator
Consolidates security scan results from various tools into a unified report.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_json_report(file_path):
    """Load JSON report file if it exists"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def load_text_report(file_path):
    """Load text report file if it exists"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def generate_html_report(security_data):
    """Generate HTML security report"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Report - DevSecOps Pipeline</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .critical {{ background-color: #f8d7da; color: #721c24; }}
            .high {{ background-color: #fff3cd; color: #856404; }}
            .medium {{ background-color: #d4edda; color: #155724; }}
            .low {{ background-color: #cce7ff; color: #004085; }}
            .summary {{ background-color: #e9ecef; padding: 10px; border-radius: 3px; }}
            pre {{ background-color: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
            .timestamp {{ color: #6c757d; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ DevSecOps Security Report</h1>
            <p class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        
        <div class="section summary">
            <h2>📊 Executive Summary</h2>
            <ul>
                <li><strong>Total Vulnerabilities:</strong> {security_data['summary']['total_vulnerabilities']}</li>
                <li><strong>Critical:</strong> {security_data['summary']['critical']}</li>
                <li><strong>High:</strong> {security_data['summary']['high']}</li>
                <li><strong>Medium:</strong> {security_data['summary']['medium']}</li>
                <li><strong>Low:</strong> {security_data['summary']['low']}</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>🔍 Static Application Security Testing (SAST)</h2>
            <h3>Bandit Results</h3>
            {security_data['sast']['bandit_html']}
        </div>
        
        <div class="section">
            <h2>📦 Dependency Security Analysis</h2>
            <h3>Safety Check Results</h3>
            {security_data['dependencies']['safety_html']}
            
            <h3>OWASP Dependency Check</h3>
            {security_data['dependencies']['owasp_html']}
        </div>
        
        <div class="section">
            <h2>🐳 Container Security</h2>
            <h3>Trivy Scan Results</h3>
            {security_data['container']['trivy_html']}
        </div>
        
        <div class="section">
            <h2>🎯 Dynamic Application Security Testing (DAST)</h2>
            <h3>OWASP ZAP Results</h3>
            {security_data['dast']['zap_html']}
        </div>
        
        <div class="section">
            <h2>📋 Recommendations</h2>
            <ul>
                {security_data['recommendations']}
            </ul>
        </div>
    </body>
    </html>
    """
    return html_content

def parse_bandit_report():
    """Parse Bandit security scan results"""
    bandit_json = load_json_report('bandit-report.json')
    bandit_text = load_text_report('bandit-report.txt')
    
    if bandit_json:
        results = bandit_json.get('results', [])
        summary = {
            'total': len(results),
            'high': len([r for r in results if r.get('issue_severity') == 'HIGH']),
            'medium': len([r for r in results if r.get('issue_severity') == 'MEDIUM']),
            'low': len([r for r in results if r.get('issue_severity') == 'LOW'])
        }
        
        html = f"<div class='summary'>Found {summary['total']} issues: "
        html += f"High: {summary['high']}, Medium: {summary['medium']}, Low: {summary['low']}</div>"
        
        if bandit_text:
            html += f"<pre>{bandit_text[:2000]}{'...' if len(bandit_text) > 2000 else ''}</pre>"
        
        return {'summary': summary, 'html': html}
    
    return {'summary': {'total': 0, 'high': 0, 'medium': 0, 'low': 0}, 'html': '<p>No Bandit report found.</p>'}

def parse_safety_report():
    """Parse Safety dependency check results"""
    safety_json = load_json_report('safety-report.json')
    safety_text = load_text_report('safety-report.txt')
    
    if safety_json:
        vulnerabilities = safety_json if isinstance(safety_json, list) else []
        summary = {'total': len(vulnerabilities)}
        
        html = f"<div class='summary'>Found {summary['total']} vulnerable dependencies</div>"
        
        if safety_text:
            html += f"<pre>{safety_text[:1500]}{'...' if len(safety_text) > 1500 else ''}</pre>"
        
        return {'summary': summary, 'html': html}
    
    return {'summary': {'total': 0}, 'html': '<p>No Safety report found.</p>'}

def parse_trivy_report():
    """Parse Trivy container scan results"""
    trivy_json = load_json_report('trivy-report.json')
    trivy_text = load_text_report('trivy-report.txt')
    
    if trivy_json:
        results = trivy_json.get('Results', [])
        total_vulns = 0
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for result in results:
            vulnerabilities = result.get('Vulnerabilities', [])
            total_vulns += len(vulnerabilities)
            
            for vuln in vulnerabilities:
                severity = vuln.get('Severity', 'UNKNOWN')
                if severity in severity_counts:
                    severity_counts[severity] += 1
        
        summary = {
            'total': total_vulns,
            'critical': severity_counts['CRITICAL'],
            'high': severity_counts['HIGH'],
            'medium': severity_counts['MEDIUM'],
            'low': severity_counts['LOW']
        }
        
        html = f"<div class='summary'>Found {summary['total']} vulnerabilities: "
        html += f"Critical: {summary['critical']}, High: {summary['high']}, "
        html += f"Medium: {summary['medium']}, Low: {summary['low']}</div>"
        
        if trivy_text:
            html += f"<pre>{trivy_text[:2000]}{'...' if len(trivy_text) > 2000 else ''}</pre>"
        
        return {'summary': summary, 'html': html}
    
    return {'summary': {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}, 'html': '<p>No Trivy report found.</p>'}

def parse_zap_report():
    """Parse OWASP ZAP DAST results"""
    zap_json = load_json_report('zap-report.json')
    
    if zap_json:
        site = zap_json.get('site', [{}])[0] if zap_json.get('site') else {}
        alerts = site.get('alerts', [])
        
        severity_counts = {'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}
        
        for alert in alerts:
            risk = alert.get('riskdesc', '').split(' ')[0]
            if risk in severity_counts:
                severity_counts[risk] += 1
        
        summary = {
            'total': len(alerts),
            'high': severity_counts['High'],
            'medium': severity_counts['Medium'],
            'low': severity_counts['Low'],
            'info': severity_counts['Informational']
        }
        
        html = f"<div class='summary'>Found {summary['total']} security alerts: "
        html += f"High: {summary['high']}, Medium: {summary['medium']}, "
        html += f"Low: {summary['low']}, Info: {summary['info']}</div>"
        
        return {'summary': summary, 'html': html}
    
    return {'summary': {'total': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}, 'html': '<p>No ZAP report found.</p>'}

def generate_recommendations(security_data):
    """Generate security recommendations based on findings"""
    recommendations = []
    
    # Check for critical issues
    total_critical = (security_data['summary']['critical'] + 
                     security_data['container']['summary']['critical'])
    
    if total_critical > 0:
        recommendations.append("🚨 <strong>URGENT:</strong> Address critical vulnerabilities immediately")
    
    # Check for high severity issues
    total_high = (security_data['summary']['high'] + 
                 security_data['container']['summary']['high'] +
                 security_data['dast']['summary']['high'])
    
    if total_high > 5:
        recommendations.append("⚠️ Consider implementing additional security controls")
    
    # Dependency recommendations
    if security_data['dependencies']['safety']['summary']['total'] > 0:
        recommendations.append("📦 Update vulnerable dependencies to latest secure versions")
    
    # Container security
    if security_data['container']['summary']['total'] > 10:
        recommendations.append("🐳 Review and update base container images")
    
    # General recommendations
    recommendations.extend([
        "🔄 Implement regular security scanning in CI/CD pipeline",
        "📚 Provide security training for development team",
        "🛡️ Enable runtime security monitoring",
        "📋 Establish incident response procedures"
    ])
    
    return '\n'.join([f"<li>{rec}</li>" for rec in recommendations])

def main():
    """Main function to generate security report"""
    # Set UTF-8 encoding for Windows compatibility
    if sys.platform.startswith('win'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("🔍 Generating consolidated security report...")
    
    # Create security reports directory
    os.makedirs('security-reports', exist_ok=True)
    
    # Parse individual security tool reports
    bandit_data = parse_bandit_report()
    safety_data = parse_safety_report()
    trivy_data = parse_trivy_report()
    zap_data = parse_zap_report()
    
    # Calculate overall summary
    total_vulnerabilities = (
        bandit_data['summary']['total'] +
        safety_data['summary']['total'] +
        trivy_data['summary']['total'] +
        zap_data['summary']['total']
    )
    
    total_critical = trivy_data['summary']['critical']
    total_high = (bandit_data['summary']['high'] + 
                 trivy_data['summary']['high'] + 
                 zap_data['summary']['high'])
    total_medium = (bandit_data['summary']['medium'] + 
                   trivy_data['summary']['medium'] + 
                   zap_data['summary']['medium'])
    total_low = (bandit_data['summary']['low'] + 
                trivy_data['summary']['low'] + 
                zap_data['summary']['low'])
    
    # Consolidate security data
    security_data = {
        'summary': {
            'total_vulnerabilities': total_vulnerabilities,
            'critical': total_critical,
            'high': total_high,
            'medium': total_medium,
            'low': total_low
        },
        'sast': {
            'bandit_html': bandit_data['html']
        },
        'dependencies': {
            'safety': safety_data,
            'safety_html': safety_data['html'],
            'owasp_html': '<p>OWASP Dependency Check results integrated in Jenkins.</p>'
        },
        'container': trivy_data,
        'dast': zap_data,
        'recommendations': ''
    }
    
    # Generate recommendations
    security_data['recommendations'] = generate_recommendations(security_data)
    
    # Generate HTML report
    html_report = generate_html_report(security_data)
    
    # Write HTML report
    with open('security-reports/security-summary.html', 'w') as f:
        f.write(html_report)
    
    # Generate JSON summary
    with open('security-reports/security-summary.json', 'w') as f:
        json.dump(security_data, f, indent=2)
    
    print(f"✅ Security report generated successfully!")
    print(f"📊 Total vulnerabilities found: {total_vulnerabilities}")
    print(f"🚨 Critical: {total_critical}, High: {total_high}, Medium: {total_medium}, Low: {total_low}")
    
    # Set exit code based on critical/high vulnerabilities
    if total_critical > 0:
        print("❌ Critical vulnerabilities found - failing build")
        sys.exit(1)
    elif total_high > 10:
        print("⚠️ Too many high severity vulnerabilities - consider failing build")
        sys.exit(1)
    else:
        print("✅ Security scan completed within acceptable limits")
        sys.exit(0)

if __name__ == "__main__":
    main()
