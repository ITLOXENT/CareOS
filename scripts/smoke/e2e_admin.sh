#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
ORG_SLUG="${ORG_SLUG:-smoke-org}"
ORG_NAME="${ORG_NAME:-Smoke Org}"
USERNAME="${ADMIN_USERNAME:-smoke-admin}"
PASSWORD="${ADMIN_PASSWORD:-smoke-pass}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bootstrap_output="$(
  cd "$ROOT_DIR/apps/api" && \
  uv run python manage.py bootstrap_smoke_admin \
    --org-slug "$ORG_SLUG" \
    --org-name "$ORG_NAME" \
    --username "$USERNAME" \
    --password "$PASSWORD"
)"

export BOOTSTRAP_JSON="$bootstrap_output"

SESSION_KEY="$(python - <<'PY'
import json, os, sys
payload = json.loads(os.environ["BOOTSTRAP_JSON"])
print(payload["session_key"])
PY
)"

ORG_ID="$(python - <<'PY'
import json, os, sys
payload = json.loads(os.environ["BOOTSTRAP_JSON"])
print(payload["org_id"])
PY
)"

cookie_header="sessionid=${SESSION_KEY}"

function api_post() {
  local path="$1"
  local body="${2:-{}}"
  curl -sS -X POST "${BASE_URL}${path}" \
    -H "Content-Type: application/json" \
    -H "X-Org-ID: ${ORG_ID}" \
    -H "Cookie: ${cookie_header}" \
    --data "${body}"
}

function api_get() {
  local path="$1"
  curl -sS "${BASE_URL}${path}" \
    -H "X-Org-ID: ${ORG_ID}" \
    -H "Cookie: ${cookie_header}"
}

echo "==> Creating episode"
episode_payload='{"title":"Smoke Episode","description":"Smoke test episode"}'
episode_json="$(api_post "/episodes/" "${episode_payload}")"
export EP_JSON="$episode_json"
episode_id="$(python - <<'PY'
import json, os
payload = json.loads(os.environ["EP_JSON"])
print(payload["id"])
PY
)"

echo "==> Transitioning episode"
api_post "/episodes/${episode_id}/transition/" '{"to_state":"triage"}' >/dev/null
api_post "/episodes/${episode_id}/transition/" '{"to_state":"in_progress"}' >/dev/null

echo "==> Assigning work item"
work_items="$(api_get "/work-items/?episode_id=${episode_id}&status=open&limit=1")"
export WORK_ITEMS="$work_items"
work_item_id="$(python - <<'PY'
import json, os
payload = json.loads(os.environ["WORK_ITEMS"])
items = payload.get("results") or []
print(items[0]["id"] if items else "")
PY
)"
if [[ -z "$work_item_id" ]]; then
  echo "No open work items found for episode ${episode_id}" >&2
  exit 1
fi
api_post "/work-items/${work_item_id}/assign/" '{}' >/dev/null
api_post "/work-items/${work_item_id}/complete/" '{}' >/dev/null

echo "==> Uploading evidence"
tmp_file="$(mktemp)"
echo "smoke evidence" > "$tmp_file"
evidence_json="$(curl -sS -X POST "${BASE_URL}/evidence/" \
  -H "X-Org-ID: ${ORG_ID}" \
  -H "Cookie: ${cookie_header}" \
  -F "file=@${tmp_file}" \
  -F "kind=note" \
  -F "title=Smoke Evidence")"
rm -f "$tmp_file"
export EVIDENCE_JSON="$evidence_json"
evidence_id="$(python - <<'PY'
import json, os
payload = json.loads(os.environ["EVIDENCE_JSON"])
print(payload["id"])
PY
)"

echo "==> Linking evidence to episode"
api_post "/episodes/${episode_id}/evidence/${evidence_id}/" '{}' >/dev/null

echo "==> Listing notifications"
notifications_json="$(api_get "/notifications/?unread_only=1&limit=1")"
export NOTIFY_JSON="$notifications_json"
notification_id="$(python - <<'PY'
import json, os
payload = json.loads(os.environ["NOTIFY_JSON"])
items = payload.get("results") or []
print(items[0]["id"] if items else "")
PY
)"
if [[ -n "$notification_id" ]]; then
  api_post "/notifications/${notification_id}/read/" '{}' >/dev/null
fi

echo "==> Requesting export"
export_json="$(api_post "/exports/" '{"kind":"audit_events","last_days":7}')"
export EXPORT_JSON="$export_json"
export_id="$(python - <<'PY'
import json, os
payload = json.loads(os.environ["EXPORT_JSON"])
print(payload["id"])
PY
)"

echo "==> Downloading export"
curl -sS -o /tmp/careos_export_${export_id}.csv \
  -H "X-Org-ID: ${ORG_ID}" \
  -H "Cookie: ${cookie_header}" \
  "${BASE_URL}/exports/${export_id}/download/"

echo "Smoke E2E admin script completed successfully."
