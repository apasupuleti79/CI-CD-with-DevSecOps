
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
