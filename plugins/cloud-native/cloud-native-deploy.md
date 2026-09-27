# Cloud Native Deployment

## Container Best Practices

- **Multi-stage builds**: Separate build and runtime images
- **Minimal base images**: Use distroless, Alpine, or scratch
- **Non-root user**: Run as unprivileged user in production
- **Single process**: One process per container
- **Signal handling**: Handle SIGTERM for graceful shutdown
- **Layer caching**: Order Dockerfile instructions by change frequency
- **Vulnerability scanning**: Scan images in CI (Trivy, Snyk, Grype)

## CI/CD Pipeline Stages

```
Lint → Test → Build → Scan → Push → Deploy (staging) → Smoke Test → Promote (prod)
```

- **Fast feedback**: Lint and unit tests complete in < 2 minutes
- **Immutable artifacts**: Build once, promote through environments
- **GitOps**: Declarative desired state in git, reconciled by ArgoCD/Flux
- **Canary deploys**: Route 1-5% traffic to new version, monitor errors
- **Automated rollback**: Revert if error rate exceeds threshold

## Infrastructure as Code

- **Terraform**: State management, modules, workspaces
- **Pulumi**: Type-safe IaC in Python/TypeScript/Go
- **Helm charts**: Kubernetes package management with values overlays
- **Kustomize**: Template-free K8s customization via overlays

## Secrets Management

| Approach | Use Case |
|---|---|
| External Secrets Operator | Sync from Vault/AWS SM to K8s Secrets |
| Sealed Secrets | Encrypt secrets for safe git storage |
| SOPS | Encrypt values in YAML/JSON config files |
| Vault Agent | Inject secrets at runtime via sidecar |

## Multi-Region / High Availability

- **Active-active**: Serve traffic from multiple regions simultaneously
- **Data replication**: Async replication with conflict resolution
- **DNS failover**: Route53 health checks, GeoDNS
- **Global load balancing**: Anycast, nearest-region routing
- **Chaos engineering**: Regular failure injection (Chaos Monkey, Litmus)
