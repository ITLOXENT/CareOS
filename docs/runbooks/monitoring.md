## Monitoring runbook

### Key signals

- API error rate (4xx/5xx), latency, and request volume.
- Celery queue depth and task failure rate.
- Database connection errors.
- Audit log throughput.

### Dashboards

- API request logs (JSON with `request_id`).
- Infrastructure metrics (CPU, memory, disk).

### Alerts

- `/readyz/` returns 503.
- High error rate sustained for 5 minutes.
- Celery workers not processing tasks.

### Incident response

- Follow `docs/runbooks/incident-response.md`.
