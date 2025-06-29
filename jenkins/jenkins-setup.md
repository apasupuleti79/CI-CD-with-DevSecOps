# Jenkins Configuration for DevSecOps Pipeline

## Required Jenkins Plugins

The following plugins are required for the DevSecOps pipeline:

### Core Plugins
- Pipeline
- Pipeline: Stage View
- Blue Ocean
- Git
- GitHub
- Credentials Binding

### Security Plugins
- OWASP Dependency-Check
- SonarQube Scanner
- HTML Publisher (for security reports)

### Build & Deploy Plugins
- Docker Pipeline
- Kubernetes
- Kubernetes CLI
- Amazon ECR (if using AWS)

### Notification Plugins
- Email Extension
- Slack Notification
- Build Monitor View

## Jenkins System Configuration

### Global Tool Configuration

#### SonarQube Scanner
- Name: `SonarQube`
- Installation: Automatic from Maven Central
- Version: Latest

#### OWASP Dependency Check
- Name: `OWASP-Dependency-Check`
- Installation: Automatic
- Version: Latest

#### Docker
- Name: `docker`
- Installation: Automatic
- Version: Latest

### Manage Jenkins > Configure System

#### SonarQube Servers
- Name: `SonarQube`
- Server URL: `http://sonarqube:9000` (adjust for your environment)
- Server authentication token: Add credential for SonarQube token

#### Email Configuration
- SMTP server: `smtp.company.com`
- Use SMTP Authentication: Yes
- Username: `jenkins@company.com`
- Password: [Add as credential]
- SMTP port: `587`
- Reply-To Address: `noreply@company.com`

#### Slack Configuration
- Workspace: `company-workspace`
- Credential: [Add Slack token]
- Default channel: `#devsecops-alerts`

## Required Credentials

Add the following credentials in Jenkins:

### Docker Registry
- Type: Username with password
- ID: `docker-registry-credentials`
- Username: [Registry username]
- Password: [Registry password/token]

### Kubernetes
- Type: Secret file
- ID: `kubernetes-credentials`
- File: Upload kubeconfig file

### SonarQube
- Type: Secret text
- ID: `sonarqube-token`
- Secret: [SonarQube authentication token]

### GitHub
- Type: Username with password (or Personal Access Token)
- ID: `github-credentials`
- Username: [GitHub username]
- Password: [GitHub token]

### Slack
- Type: Secret text
- ID: `slack-token`
- Secret: [Slack Bot User OAuth Token]

## Environment Variables

Set the following global environment variables:

```
DOCKER_REGISTRY=your-registry.com
SONARQUBE_URL=http://sonarqube:9000
KUBERNETES_NAMESPACE_STAGING=staging
KUBERNETES_NAMESPACE_PRODUCTION=production
SECURITY_EMAIL=security@company.com
DEVOPS_EMAIL=devops@company.com
```

## Pipeline Configuration

### Multibranch Pipeline Setup

1. Create new item > Multibranch Pipeline
2. Branch Sources: Git/GitHub
3. Repository URL: `https://github.com/company/my-devsecops-project.git`
4. Credentials: Select GitHub credentials
5. Build Configuration: by Jenkinsfile
6. Script Path: `Jenkinsfile`

### Branch Strategy

- `main` branch: Full pipeline with production deployment
- `develop` branch: Full pipeline without production deployment
- Feature branches: Build and test only (no deployment)

### Webhook Configuration

Configure GitHub webhook:
- Payload URL: `https://jenkins.company.com/github-webhook/`
- Content type: `application/json`
- Events: Push, Pull requests

## Security Hardening

### Jenkins Security Configuration

1. **Enable CSRF Protection**
   - Manage Jenkins > Configure Global Security
   - Enable "Prevent Cross Site Request Forgery exploits"

2. **Setup Authorization Strategy**
   - Use "Matrix-based security" or "Role-based Authorization Strategy"
   - Grant appropriate permissions to users/groups

3. **Secure Agent Communication**
   - Use JNLP4 protocol
   - Enable agent-to-master security

4. **Script Security**
   - Enable "In-process Script Approval"
   - Review and approve all scripts

### Pipeline Security

1. **Credential Management**
   - Never hardcode secrets in Jenkinsfile
   - Use Jenkins credential store
   - Rotate credentials regularly

2. **Container Security**
   - Use non-root users in build containers
   - Scan container images for vulnerabilities
   - Use minimal base images

3. **Network Security**
   - Restrict network access from build agents
   - Use VPN or private networks for sensitive operations

## Monitoring and Logging

### Build Monitoring
- Install "Build Monitor View" plugin
- Create dashboard for pipeline status
- Set up email notifications for build failures

### Log Management
- Configure log rotation
- Archive important build artifacts
- Set up centralized logging (ELK stack)

### Metrics Collection
- Enable Jenkins metrics plugin
- Monitor build times and success rates
- Track security scan results over time

## Backup and Recovery

### Backup Strategy
- Backup Jenkins home directory daily
- Include job configurations and credentials
- Test restore procedures regularly

### High Availability
- Consider Jenkins cluster setup for production
- Use shared storage for Jenkins home
- Implement load balancing

## Compliance and Auditing

### Audit Trail
- Enable Jenkins audit log plugin
- Track all configuration changes
- Monitor user access and actions

### Compliance Reporting
- Generate compliance reports from security scans
- Maintain evidence of security testing
- Document approval processes for production deployments

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Check Jenkins user permissions
   - Verify credential configuration
   - Review file system permissions

2. **Plugin Conflicts**
   - Update plugins regularly
   - Test plugin updates in staging
   - Maintain plugin compatibility matrix

3. **Resource Issues**
   - Monitor Jenkins memory usage
   - Configure appropriate heap sizes
   - Use build agents for heavy workloads

### Performance Optimization

1. **Build Performance**
   - Use parallel pipeline stages
   - Cache dependencies between builds
   - Use lightweight Docker images

2. **Agent Management**
   - Use ephemeral build agents
   - Configure agent templates
   - Monitor agent resource usage
