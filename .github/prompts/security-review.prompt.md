# Security Review Prompt

Review this repository from a DevSecOps perspective.

Check:

- secrets and sensitive defaults
- dependency scanning coverage
- CodeQL and CI security gates
- Docker runtime restrictions
- Kubernetes secret placeholders and security contexts
- branch protection and PR governance assumptions
- local-only risks such as Docker socket and host filesystem mounts

Use realistic wording. Do not claim enterprise-grade security unless evidence exists.
