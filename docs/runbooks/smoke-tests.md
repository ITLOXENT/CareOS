## Smoke tests

### API

- `GET /healthz/` returns 200.
- `GET /readyz/` returns 200.

### Web-admin

- Login succeeds.
- Load Inbox and Episodes pages.

### Portal

- Login succeeds via invite or email/phone.
- Episodes list loads and detail page opens.
- Notifications list loads and mark read works.

### Commands

- `python3 scripts/smoke_test.py`
- `curl -sSf http://localhost:8000/healthz/`
- `curl -sSf http://localhost:8000/readyz/`
