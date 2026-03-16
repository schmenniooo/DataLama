# DataLama

A microservice that takes data in several formats and returns a forecast or a summary of the data.
Runs Python with FastAPI and uses Ollama to analyse the given data through a chosen model.

![logo.png](logo.png)

## API Endpoints

| Method | Path           | Description                    |
| ------ |----------------| ------------------------------ |
| GET    | `/health`      | Health check                   |
| POST   | `/forecasting` | Time series forecasting        |
| POST   | `/summary`     | Generate a summary of the data |
| POST   | `/anomaly`     | Detect anomalies in the data   |
| POST   | `/pattern`     | Recognize patterns in the data |
| POST   | `/comparison`  | Compare datasets               |

All endpoints except `/ping` require an API key passed via the header configured in `API_KEY_FIELD_NAME` (default: `X-API-Key`).

## Configuration

The service is configured via environment variables:

| Variable             | Default                  | Description                                 |
| -------------------- | ------------------------ |---------------------------------------------|
| `OLLAMA_BASE_URL`    | `http://localhost:11434` | Base URL of the Ollama instance             |
| `OLLAMA_MODEL`       | `llama3.2`               | Ollama model to use for analysis            |
| `API_KEY`            | `api-key`                | API key for authenticating requests         |
| `API_KEY_FIELD_NAME` | `X-API-Key`              | Header name used to pass the API key        |
| `HOST`               | `0.0.0.0`                | Host the server binds to                    |
| `PORT`               | `3000`                   | Port the server listens on                  |
| `DEBUG`              | `false`                  | Enable debug mode (no Authentication needed |

## Helm Chart

The chart is published to GHCR and can be used to deploy DataLama to a Kubernetes cluster. It requires an Ollama instance reachable from within the cluster.

The chart includes:
- **Traefik** as a reverse proxy with an optional authenticated dashboard
- **Redis** for rate limiting — `REDIS_HOST`, `REDIS_PORT`, and `REDIS_PASSWORD` are automatically injected into all pods
- **HPA** for autoscaling based on CPU and memory utilization

### Installation

```bash
helm install datalama oci://ghcr.io/schmenniooo/helm/datalama-chart
```

### Configuration

All environment variables can be set via `environmentVariables` in your `values.yaml`:

```yaml
environmentVariables:
  - name: OLLAMA_BASE_URL
    value: "http://ollama.default.svc.cluster.local:11434"
  - name: OLLAMA_MODEL
    value: "llama3.2"
  - name: API_KEY
    value: "your-api-key"
  - name: API_KEY_FIELD_NAME
    value: "X-API-Key"
```

All environment variables can be set directly via `--set` on install:

```bash
helm install datalama oci://ghcr.io/schmenniooo/helm/datalama-chart \
  --set environmentVariables[0].name=OLLAMA_BASE_URL \
  --set environmentVariables[0].value=http://ollama:11434
```

### Values

| Key                                        | Default                        | Description                                              |
| ------------------------------------------ | ------------------------------ | -------------------------------------------------------- |
| `replicaCount`                             | `1`                            | Number of pod replicas (ignored when autoscaling enabled) |
| `service.type`                             | `ClusterIP`                    | Kubernetes service type                                  |
| `service.port`                             | `3000`                         | Service port                                             |
| `resources.requests.cpu`                   | `100m`                         | CPU request                                              |
| `resources.requests.memory`                | `64Mi`                         | Memory request                                           |
| `resources.limits.cpu`                     | `500m`                         | CPU limit                                                |
| `resources.limits.memory`                  | `128Mi`                        | Memory limit                                             |
| `autoscaling.enabled`                      | `true`                         | Enable Horizontal Pod Autoscaler                         |
| `autoscaling.minReplicas`                  | `1`                            | Minimum number of replicas                               |
| `autoscaling.maxReplicas`                  | `10`                           | Maximum number of replicas                               |
| `autoscaling.targetCPUUtilizationPercentage` | `75`                         | Target CPU utilization for scaling                       |
| `autoscaling.targetMemoryUtilizationPercentage` | `75`                      | Target memory utilization for scaling                    |
| `dashboard.enabled`                        | `true`                         | Enable Traefik dashboard                                 |
| `dashboard.host`                           | `dashboard.docker.localhost`   | Hostname for the dashboard IngressRoute                  |
| `dashboard.auth.username`                  | `admin`                        | Dashboard BasicAuth username                             |
| `dashboard.auth.password`                  | `changeme`                     | Dashboard BasicAuth password                             |
| `dashboard.tls.enabled`                    | `false`                        | Enable TLS for the dashboard                             |
| `dashboard.tls.secretName`                 | `""`                           | Name of the k8s Secret containing `tls.crt` and `tls.key` |
| `redis.auth.enabled`                       | `true`                         | Enable Redis authentication                              |
| `redis.auth.password`                      | `changeme`                     | Redis password (also sets `REDIS_PASSWORD` in pods)      |
