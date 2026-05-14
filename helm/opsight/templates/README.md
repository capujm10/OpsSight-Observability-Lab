This chart skeleton documents the intended packaging boundary. The current repository keeps Kubernetes manifests explicit under `k8s/` so they can be reviewed without template rendering.

Environment strategy:

- `values.yaml`: local/default values.
- `values-dev.yaml`: lower resource requests and local ingress hosts.
- `values-prod.yaml`: managed secrets, persistent storage classes, autoscaling, and external telemetry backends.
