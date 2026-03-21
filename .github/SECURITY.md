# Security Policy

## Supported Versions

Only the latest version on the `main` branch receives security fixes.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities privately via [GitHub Security Advisories](https://github.com/schmenniooo/DataLens/security/advisories/new). Include as much detail as possible:

- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- Affected component (API, authentication middleware, Helm chart, Docker image, etc.)
- Any suggested mitigations

## Security Considerations

### Authentication

- All endpoints except `/health` require an API key passed via the `X-API-Key` header (configurable via `API_KEY_FIELD_NAME`)
- `DEBUG=true` disables authentication entirely — **never enable this in production**
- Rotate `API_KEY` regularly and avoid reusing default values

### LLM Provider Credentials

- `LLM_PROVIDER_API_TOKEN` holds the secret key for the configured LLM provider — **never commit it to version control**
- Store it in a `.env` file (already in `.gitignore`) or inject it via Kubernetes Secrets / CI variables
- Rotate the token periodically and restrict its scope to the minimum required permissions on the provider side

### Deployment

- The Helm chart ships with default credentials (`changeme`) for the Traefik dashboard and Redis — **always override these** before deploying to any shared or production environment:
  ```yaml
  dashboard:
    auth:
      password: <strong-password>
  redis:
    auth:
      password: <strong-password>
  ```
- Restrict access to the Traefik dashboard (`dashboard.host`) to trusted networks only
- Use TLS for the dashboard in production (`dashboard.tls.enabled: true`)

### Docker

- The Docker image is published to GHCR. Pin to a specific digest or tag rather than `latest` in production manifests
- Run the container as a non-root user where possible

### Dependency Security

- Dependencies are scanned automatically via [CodeQL](../.github/workflows/codeql.yml) on every push and pull request
- Keep `uv.lock` committed and up to date to ensure reproducible builds

## Disclosure Policy

Once a fix is available, the vulnerability will be disclosed publicly via a GitHub Security Advisory. Credit will be given to the reporter unless anonymity is requested.
