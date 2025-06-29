# Monitoring Directory

This directory contains observability tools, health checks, and monitoring configurations for the DevSecOps pipeline.

## Structure

```
📁 monitoring/
├── 📁 configs/                    # Generated monitoring configurations
│   ├── alertmanager-email.yml     # Email notification config
│   ├── alertmanager-slack.yml     # Slack notification config
│   ├── prometheus-alerts.yml      # Prometheus alerting rules
│   └── security-monitoring.yml    # Security monitoring config
├── 📁 dashboards/                 # Visualization dashboards
│   └── grafana-dashboard.json     # Main Grafana dashboard
├── 📄 health_check.py             # Application health monitoring
├── 📄 setup_alerts.py             # Alert configuration generator
└── 📄 incident-response-runbook.md # Emergency procedures
```

## Core Components

| 📂 **Component** | 🎯 **Purpose** |
|------------------|----------------|
| **health_check.py** | Real-time application health monitoring |
| **setup_alerts.py** | Automated alert configuration generation |
| **configs/** | Generated monitoring and alerting configurations |
| **dashboards/** | Grafana visualization configurations |

## Usage

```bash
# Run health check
python monitoring/health_check.py --environment production --url https://your-app.com

# Generate monitoring configs
python monitoring/setup_alerts.py --deployment prod-v1.0

# View incident response procedures
cat monitoring/incident-response-runbook.md
```

## Integration

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards  
- **AlertManager**: Notification routing (email/slack)
- **Health Checks**: Application status monitoring
