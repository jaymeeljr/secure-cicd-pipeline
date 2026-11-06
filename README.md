# Secure CI/CD Pipeline with Security Gates

![pipeline](https://github.com/jaymeeljr/secure-cicd-pipeline/actions/workflows/security-pipeline.yml/badge.svg)

A DevSecOps reference pipeline for a containerized Python API. Every push and pull request passes through five automated security gates; **nothing is built or pushed unless all of them pass**.

## Pipeline

```
push / PR
   │
   ├── Gate 1  Secret detection      Gitleaks (full git history)
   ├── Gate 2  SAST                  Semgrep registry rules + custom project rules
   ├── Gate 3  SCA                   pip-audit against PyPI advisories
   ├── Gate 4  IaC & policy          Checkov + OPA/Conftest (with policy unit tests)
   ├── Unit tests                    pytest
   │
   └── Gate 5  Build & image scan    Trivy (fails on HIGH/CRITICAL), SARIF → Security tab,
                                     CycloneDX SBOM, push to GHCR (main only),
                                     manifest rendered with immutable commit-SHA tag
```

## What each gate catches

| Gate | Tool | Fails the build when |
| --- | --- | --- |
| Secrets | Gitleaks | API keys, tokens or passwords appear anywhere in git history |
| SAST | Semgrep | Insecure code patterns, e.g. `debug=True`, hardcoded `SECRET_KEY`, `shell=True`, unsafe `yaml.load` |
| SCA | pip-audit | A pinned dependency has a known vulnerability |
| IaC | Checkov | Dockerfile or Kubernetes manifests violate security best practices |
| Policy | Conftest (OPA) | Manifests break org rules: root pods, privileged containers, writable root FS, missing limits, `:latest` tags |
| Image | Trivy | The built image contains fixable HIGH/CRITICAL CVEs |

**Real finding during development:** pip-audit blocked the first build because `flask==3.1.2` had a published advisory (PYSEC-2026-2151). Upgrading to 3.1.3 cleared the gate — exactly the workflow this pipeline is designed to enforce.

**Second finding, on the first GitHub run:** Semgrep's Flask ruleset flagged the local dev server binding to `0.0.0.0`. It was changed to `127.0.0.1`; the container uses gunicorn, so production behavior is unchanged. The fix went in instead of a suppression comment.

**Third finding:** Trivy failed the build on 5 HIGH CVEs in `pip`/`setuptools` and the libraries pip vendors (`urllib3`, `msgpack`) inside the base image. None are needed at runtime, so they were removed from the final image, shrinking the attack surface rather than ignoring the findings.

## Hardening applied

**Container (`Dockerfile`)**
- Multi-stage build: no compilers, build tools, `pip` or `setuptools` in the runtime image
- Runs as dedicated non-root user (UID 10001), production WSGI server (gunicorn)
- Built-in healthcheck; `.dockerignore` keeps tests, git data and `.env` out of the image

**Kubernetes (`k8s/`)**
- Namespace enforces the `restricted` Pod Security Standard
- `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`, all capabilities dropped, `RuntimeDefault` seccomp
- Service account token not mounted; CPU/memory requests and limits set
- Default-deny NetworkPolicy, then only TCP 8080 allowed in

**Application (`app/`)**
- Input validation on all write endpoints; security headers on every response
- Debug mode off unless explicitly enabled via environment

**Pipeline itself**
- Default `GITHUB_TOKEN` scoped to `contents: read`; write scopes granted only to the build job
- Pull requests are scanned but never push images

## Policy-as-Code

Rules live in [`policy/kubernetes.rego`](policy/kubernetes.rego) and are themselves tested in [`policy/kubernetes_test.rego`](policy/kubernetes_test.rego), so a broken policy cannot silently pass everything.

```bash
conftest verify --policy policy/      # policy unit tests
conftest test k8s/ --policy policy/   # enforce on manifests
```

## Run locally

```bash
pip install -r requirements-dev.txt && pytest -q
docker build -t task-api . && docker run -p 8080:8080 task-api
curl localhost:8080/health
```

## Roadmap

- Pin images by digest and sign them with Cosign; verify signatures at admission
- DAST stage with OWASP ZAP against an ephemeral deployment
- Deploy via ArgoCD (see the GitOps project)

## Author

Jamil Qarahmadov — DevSecOps Engineer · [LinkedIn](https://www.linkedin.com/in/cemil-qarahmedov-0507b4211/) · cemil.qarahmedov@gmail.com
