#!/usr/bin/env bash
# Quick test: yesterday's German construction tenders with a parsed GAEB bill of quantities.
# Usage: APIFY_TOKEN=... ./curl_quickstart.sh            (token: https://console.apify.com/settings/integrations)
set -euo pipefail

curl -sS --max-time 310 -X POST \
  "https://api.apify.com/v2/acts/brsksr~german-construction-tenders-gaeb/run-sync-get-dataset-items" \
  -H "Authorization: Bearer ${APIFY_TOKEN:?set APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"pubDaysBack": 1, "cpvPrefixes": ["45"], "onlyWithGaeb": true, "maxTenders": 3}' \
  -o tenders.json

echo "Saved tenders.json"
# Optional with jq: one line per tender
command -v jq >/dev/null && jq -r '.[] | "\(.submissionDeadline)  \(.positionCount) pos  \(.title)"' tenders.json || true
