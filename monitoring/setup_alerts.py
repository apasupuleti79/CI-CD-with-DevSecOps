#!/usr/bin/env python3
"""
Alert Setup Script for DevSecOps Application
Configures monitoring alerts and notifications.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

def create_prometheus_rules(deployment_version):
    """Create Prometheus alerting rules"""
    rules = {
        'groups': [
            {
                'name': 'devsecops-app-alerts',
                'rules': [
                    {
                        'alert': 'ApplicationDown',
                        'expr': 'up{job="my-devsecops-app"} == 0',
                        'for': '5m',
                        'labels': {
                            'severity': 'critical',
                            'service': 'my-devsecops-app',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'DevSecOps application is down',
                            'description': 'The DevSecOps application has been down for more than 5 minutes.'
                        }
                    },
                    {
                        'alert': 'HighResponseTime',
                        'expr': 'avg(http_request_duration_seconds{job="my-devsecops-app"}) > 2',
                        'for': '10m',
                        'labels': {
                            'severity': 'warning',
                            'service': 'my-devsecops-app',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'High response time detected',
                            'description': 'Average response time is above 2 seconds for 10 minutes.'
                        }
                    },
                    {
                        'alert': 'HighErrorRate',
                        'expr': 'rate(http_requests_total{job="my-devsecops-app",status=~"5.."}[5m]) > 0.1',
                        'for': '5m',
                        'labels': {
                            'severity': 'warning',
                            'service': 'my-devsecops-app',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'High error rate detected',
                            'description': 'Error rate is above 10% for 5 minutes.'
                        }
                    },
                    {
                        'alert': 'SecurityVulnerabilityDetected',
                        'expr': 'security_vulnerabilities_total{severity="critical"} > 0',
                        'for': '0m',
                        'labels': {
                            'severity': 'critical',
                            'service': 'my-devsecops-app',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'Critical security vulnerability detected',
                            'description': 'A critical security vulnerability has been detected in the application.'
                        }
                    },
                    {
                        'alert': 'MemoryUsageHigh',
                        'expr': 'container_memory_usage_bytes{name="my-devsecops-app"} / container_spec_memory_limit_bytes{name="my-devsecops-app"} > 0.8',
                        'for': '10m',
                        'labels': {
                            'severity': 'warning',
                            'service': 'my-devsecops-app',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'High memory usage',
                            'description': 'Container memory usage is above 80% for 10 minutes.'
                        }
                    },
                    {
                        'alert': 'CPUUsageHigh',
                        'expr': 'rate(container_cpu_usage_seconds_total{name="my-devsecops-app"}[5m]) > 0.8',
                        'for': '15m',
                        'labels': {
                            'severity': 'warning',
                            'service': 'my-devsecops-app',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'High CPU usage',
                            'description': 'Container CPU usage is above 80% for 15 minutes.'
                        }
                    }
                ]
            }
        ]
    }
    
    # Save Prometheus rules
    with open('prometheus-alerts.yml', 'w') as f:
        import yaml
        yaml.dump(rules, f, default_flow_style=False)
    
    print(f"✅ Created Prometheus alerting rules for deployment {deployment_version}")
    return rules

def create_grafana_dashboard(deployment_version):
    """Create Grafana dashboard configuration"""
    dashboard = {
        'dashboard': {
            'title': f'DevSecOps Application - {deployment_version}',
            'tags': ['devsecops', 'security', 'monitoring'],
            'timezone': 'browser',
            'refresh': '30s',
            'time': {
                'from': 'now-1h',
                'to': 'now'
            },
            'panels': [
                {
                    'title': 'Application Status',
                    'type': 'stat',
                    'targets': [
                        {
                            'expr': 'up{job="my-devsecops-app"}',
                            'legendFormat': 'Status'
                        }
                    ]
                },
                {
                    'title': 'Response Time',
                    'type': 'graph',
                    'targets': [
                        {
                            'expr': 'avg(http_request_duration_seconds{job="my-devsecops-app"})',
                            'legendFormat': 'Average Response Time'
                        }
                    ]
                },
                {
                    'title': 'Request Rate',
                    'type': 'graph',
                    'targets': [
                        {
                            'expr': 'rate(http_requests_total{job="my-devsecops-app"}[5m])',
                            'legendFormat': 'Requests/sec'
                        }
                    ]
                },
                {
                    'title': 'Error Rate',
                    'type': 'graph',
                    'targets': [
                        {
                            'expr': 'rate(http_requests_total{job="my-devsecops-app",status=~"5.."}[5m])',
                            'legendFormat': 'Error Rate'
                        }
                    ]
                },
                {
                    'title': 'Security Vulnerabilities',
                    'type': 'table',
                    'targets': [
                        {
                            'expr': 'security_vulnerabilities_total',
                            'legendFormat': 'Vulnerabilities by Severity'
                        }
                    ]
                },
                {
                    'title': 'Resource Usage',
                    'type': 'graph',
                    'targets': [
                        {
                            'expr': 'container_memory_usage_bytes{name="my-devsecops-app"} / 1024 / 1024',
                            'legendFormat': 'Memory (MB)'
                        },
                        {
                            'expr': 'rate(container_cpu_usage_seconds_total{name="my-devsecops-app"}[5m]) * 100',
                            'legendFormat': 'CPU (%)'
                        }
                    ]
                }
            ]
        }
    }
    
    # Save Grafana dashboard
    with open('grafana-dashboard.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"✅ Created Grafana dashboard configuration for deployment {deployment_version}")
    return dashboard

def setup_slack_notifications():
    """Setup Slack notification configuration"""
    slack_config = {
        'global': {
            'slack_api_url': os.getenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK')
        },
        'route': {
            'group_by': ['alertname'],
            'group_wait': '10s',
            'group_interval': '10s',
            'repeat_interval': '1h',
            'receiver': 'web.hook'
        },
        'receivers': [
            {
                'name': 'web.hook',
                'slack_configs': [
                    {
                        'api_url': '{{ .SlackAPIURL }}',
                        'channel': '#devsecops-alerts',
                        'title': 'DevSecOps Alert: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}',
                        'text': '''{{ range .Alerts }}
*Alert:* {{ .Annotations.summary }}
*Description:* {{ .Annotations.description }}
*Severity:* {{ .Labels.severity }}
*Service:* {{ .Labels.service }}
*Deployment:* {{ .Labels.deployment }}
{{ end }}''',
                        'send_resolved': True
                    }
                ]
            }
        ]
    }
    
    # Save Slack configuration
    with open('alertmanager-slack.yml', 'w') as f:
        import yaml
        yaml.dump(slack_config, f, default_flow_style=False)
    
    print("✅ Created Slack notification configuration")
    return slack_config

def setup_email_notifications():
    """Setup email notification configuration"""
    email_config = {
        'global': {
            'smtp_smarthost': os.getenv('SMTP_HOST', 'localhost:587'),
            'smtp_from': os.getenv('SMTP_FROM', 'alerts@company.com'),
            'smtp_auth_username': os.getenv('SMTP_USERNAME', ''),
            'smtp_auth_password': os.getenv('SMTP_PASSWORD', '')
        },
        'route': {
            'group_by': ['alertname'],
            'group_wait': '10s',
            'group_interval': '10s',
            'repeat_interval': '1h',
            'receiver': 'email-notifications'
        },
        'receivers': [
            {
                'name': 'email-notifications',
                'email_configs': [
                    {
                        'to': os.getenv('ALERT_EMAIL', 'security@company.com'),
                        'subject': 'DevSecOps Alert: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}',
                        'body': '''DevSecOps Security Alert

{{ range .Alerts }}
Alert: {{ .Annotations.summary }}
Description: {{ .Annotations.description }}
Severity: {{ .Labels.severity }}
Service: {{ .Labels.service }}
Deployment: {{ .Labels.deployment }}
Time: {{ .StartsAt }}

{{ end }}

Please investigate immediately.

Dashboard: https://grafana.company.com/d/devsecops
Runbook: https://wiki.company.com/devops/runbooks/security-alerts
'''
                    }
                ]
            }
        ]
    }
    
    # Save email configuration
    with open('alertmanager-email.yml', 'w') as f:
        import yaml
        yaml.dump(email_config, f, default_flow_style=False)
    
    print("✅ Created email notification configuration")
    return email_config

def create_security_monitors(deployment_version):
    """Create security-specific monitoring rules"""
    security_rules = {
        'groups': [
            {
                'name': 'security-monitoring',
                'rules': [
                    {
                        'alert': 'SuspiciousLoginActivity',
                        'expr': 'increase(failed_login_attempts_total[5m]) > 10',
                        'for': '2m',
                        'labels': {
                            'severity': 'warning',
                            'category': 'security',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'High number of failed login attempts',
                            'description': 'More than 10 failed login attempts in 5 minutes.'
                        }
                    },
                    {
                        'alert': 'UnauthorizedAPIAccess',
                        'expr': 'increase(http_requests_total{status="401"}[5m]) > 20',
                        'for': '5m',
                        'labels': {
                            'severity': 'warning',
                            'category': 'security',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'High number of unauthorized API requests',
                            'description': 'More than 20 401 responses in 5 minutes.'
                        }
                    },
                    {
                        'alert': 'SecurityScanFailure',
                        'expr': 'security_scan_status != 1',
                        'for': '0m',
                        'labels': {
                            'severity': 'critical',
                            'category': 'security',
                            'deployment': deployment_version
                        },
                        'annotations': {
                            'summary': 'Security scan failed',
                            'description': 'Automated security scan has failed or detected critical issues.'
                        }
                    }
                ]
            }
        ]
    }
    
    # Save security monitoring rules
    with open('security-monitoring.yml', 'w') as f:
        import yaml
        yaml.dump(security_rules, f, default_flow_style=False)
    
    print(f"✅ Created security monitoring rules for deployment {deployment_version}")
    return security_rules

def generate_runbook():
    """Generate incident response runbook"""
    runbook = """
# DevSecOps Incident Response Runbook

## Security Alert Response Procedures

### Critical Alerts

#### Application Down
1. Check application logs: `kubectl logs -f deployment/my-devsecops-app -n production`
2. Check pod status: `kubectl get pods -n production`
3. Check service endpoints: `kubectl get endpoints -n production`
4. Restart if necessary: `kubectl rollout restart deployment/my-devsecops-app -n production`

#### Security Vulnerability Detected
1. **IMMEDIATE**: Stop all deployments
2. Review security scan results in Jenkins
3. Contact security team: security@company.com
4. Document findings in incident management system
5. Create hotfix branch if critical vulnerability confirmed
6. Update dependencies or apply patches
7. Re-run security scans before deployment

### Warning Alerts

#### High Response Time
1. Check application metrics in Grafana
2. Review resource usage (CPU, memory)
3. Check database performance
4. Scale horizontally if needed: `kubectl scale deployment my-devsecops-app --replicas=5`

#### High Error Rate
1. Check application logs for errors
2. Review recent deployments
3. Check external service dependencies
4. Consider rollback if recent deployment: `kubectl rollout undo deployment/my-devsecops-app`

#### Resource Usage High
1. Monitor trends in Grafana
2. Check for memory leaks or CPU spikes
3. Scale resources: `kubectl patch deployment my-devsecops-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","resources":{"limits":{"memory":"1Gi","cpu":"1000m"}}}]}}}}'`

### Security Incident Response

#### Failed Login Attempts
1. Review source IPs in logs
2. Check for credential stuffing attacks
3. Implement rate limiting if not already enabled
4. Block suspicious IPs at firewall level

#### Unauthorized API Access
1. Review API access logs
2. Check for API key compromise
3. Rotate API keys if necessary
4. Review access control policies

## Contact Information

- **Security Team**: security@company.com
- **DevOps Team**: devops@company.com
- **On-Call Engineer**: +1-555-ON-CALL
- **Incident Commander**: +1-555-INCIDENT

## Useful Commands

```bash
# Check application status
kubectl get pods -n production -l app=my-devsecops-app

# View application logs
kubectl logs -f deployment/my-devsecops-app -n production

# Scale application
kubectl scale deployment my-devsecops-app --replicas=5 -n production

# Check resource usage
kubectl top pods -n production

# Emergency rollback
kubectl rollout undo deployment/my-devsecops-app -n production

# Force pod restart
kubectl delete pods -l app=my-devsecops-app -n production
```

## Post-Incident Procedures

1. Document incident in post-mortem template
2. Update monitoring thresholds if needed
3. Review and update security policies
4. Conduct team retrospective
5. Update runbook with lessons learned
"""
    
    with open('incident-response-runbook.md', 'w') as f:
        f.write(runbook)
    
    print("✅ Created incident response runbook")

def main():
    parser = argparse.ArgumentParser(description='Setup monitoring alerts for DevSecOps application')
    parser.add_argument('--deployment', required=True, help='Deployment version/tag')
    parser.add_argument('--environment', default='production', choices=['staging', 'production'],
                       help='Environment to setup alerts for')
    parser.add_argument('--notifications', nargs='+', choices=['slack', 'email'], 
                       default=['slack', 'email'], help='Notification channels to configure')
    
    args = parser.parse_args()
    
    # Set UTF-8 encoding for Windows compatibility
    if sys.platform.startswith('win'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print(f"🚨 Setting up monitoring alerts for deployment {args.deployment}")
    
    # Create monitoring configurations
    prometheus_rules = create_prometheus_rules(args.deployment)
    grafana_dashboard = create_grafana_dashboard(args.deployment)
    security_rules = create_security_monitors(args.deployment)
    
    # Setup notifications
    if 'slack' in args.notifications:
        setup_slack_notifications()
    
    if 'email' in args.notifications:
        setup_email_notifications()
    
    # Generate runbook
    generate_runbook()
    
    print(f"\n✅ Monitoring setup complete for {args.environment} environment!")
    print("📄 Files created:")
    print("  - prometheus-alerts.yml")
    print("  - security-monitoring.yml")
    print("  - grafana-dashboard.json")
    
    if 'slack' in args.notifications:
        print("  - alertmanager-slack.yml")
    
    if 'email' in args.notifications:
        print("  - alertmanager-email.yml")
    
    print("  - incident-response-runbook.md")
    
    print("\n🔧 Next steps:")
    print("1. Apply Prometheus rules to your monitoring cluster")
    print("2. Import Grafana dashboard")
    print("3. Configure Alertmanager with notification settings")
    print("4. Test alert notifications")
    print("5. Review and customize runbook for your environment")

if __name__ == "__main__":
    # Install required dependency if not available
    try:
        import yaml
    except ImportError:
        print("Installing PyYAML...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"])
        import yaml
    
    main()
