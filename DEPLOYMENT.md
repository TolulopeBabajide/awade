# Deployment Guide for Awade

## 🐳 Docker Deployment

Awade is containerized using Docker. To deploy in production:

1.  **Build Images**:
    ```bash
    docker-compose build
    ```

2.  **Start Services**:
    ```bash
    docker-compose up -d
    ```

## 📊 Monitoring & Observability

Awade exposes operational metrics via the standard Prometheus format at `/metrics`.

### Prometheus Scrape Config
Add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'awade_backend'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['backend:8000']
```

### Grafana Dashboards
You can visualize these metrics in Grafana. Recommended panels:
- **Request Rate**: `rate(http_requests_total[1m])`
- **Error Rate**: `rate(http_requests_total{status=~"5.."}[1m])`
- **Latency**: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`

### Logging
Structured JSON logs are output to stdout. Ensure your container logging driver is configured to capture these (e.g., `json-file`, `awslogs`, `fluentd`).

## 🛡️ Security Headers
The application enforces strict security headers:
- `Strict-Transport-Security` (HSTS)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

Ensure your reverse proxy (Nginx, Traefik) does not strip these headers.
