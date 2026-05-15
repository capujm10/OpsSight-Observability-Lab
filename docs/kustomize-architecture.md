# Kustomize Architecture

OpsSight uses Kustomize to keep Kubernetes manifests reviewable while still supporting environment-specific promotion. Docker Compose remains the full local runtime for Prometheus, Grafana, Loki, Tempo, Alloy, and smoke testing. Kustomize covers application and Kubernetes monitoring readiness manifests only.

## Layout

```text
k8s/
  base/                Namespace, ConfigMaps, and Secret placeholder
  api/                 API, payment-gateway, AI RCA, ingress, HPA, NetworkPolicy
  monitoring/          Alloy config placeholder, kube-state-metrics, Prometheus PVC
  overlays/local/      Local Kubernetes render target
  overlays/dev/        Development GitOps target
  overlays/staging/    Pre-production GitOps target
  overlays/prod/       Production-style GitOps target
```

## Overlay Strategy

All overlays reference the same reusable resources:

```yaml
resources:
  - ../../base
  - ../../api
  - ../../monitoring
```

The overlays apply environment-specific namespaces, image tags, replicas, ingress hostnames, and resource requests/limits.

| Overlay | Namespace | Image tag | API replicas | Dependency replicas | AI RCA replicas | Ingress host |
| --- | --- | --- | ---: | ---: | ---: | --- |
| local | `opsight` | `local` | 1 | 1 | 1 | `opsight-api.local` |
| dev | `opsight-dev` | `dev` | 1 | 1 | 1 | `dev.api.opsight.local` |
| staging | `opsight-staging` | `staging` | 2 | 2 | 1 | `staging.api.opsight.local` |
| prod | `opsight-prod` | `v1.0.0` | 3 | 3 | 2 | `api.opsight.local` |

## Namespace Isolation

Each overlay renders all namespaced resources into its own namespace. This keeps application resources, placeholder secrets, ingress, NetworkPolicy, kube-state-metrics workload resources, Alloy config, and Prometheus PVC isolated per environment.

Cluster-scoped kube-state-metrics RBAC is patched per overlay so local, dev, staging, and prod render distinct `ClusterRole` and `ClusterRoleBinding` names. A real shared cluster should still decide whether kube-state-metrics is environment-local or shared platform monitoring before deployment.

## Environment Promotion

Promotion should be GitOps-driven:

1. Build and publish versioned images outside these manifests.
2. Update the target overlay image tag.
3. Run Kustomize render and dry-run validation.
4. Open a pull request with validation evidence.
5. Let the GitOps controller reconcile the approved overlay.

The current `prod` overlay uses `v1.0.0` as a portfolio-ready example tag. Replace it with the released image tag during a real promotion.

## Validation

Run all overlays:

```bash
bash scripts/validate-kustomize.sh
```

Run one overlay:

```bash
kubectl kustomize k8s/overlays/local
kubectl apply --dry-run=client --validate=false -k k8s/overlays/local
```

CI runs the same overlay validation after the existing explicit manifest dry-run. `scripts/validate-all.sh` also calls the Kustomize validation script so local all-in-one checks match CI.

## Helm Compatibility

The Kustomize foundation is intentionally not a Helm implementation. It keeps manifests explicit so future Helm work can template the same deployment boundaries: base config, service deployments, ingress, HPA, NetworkPolicy, and monitoring readiness resources.
