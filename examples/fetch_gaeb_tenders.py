"""Fetch German construction tenders with parsed GAEB positions and print them as CSV (standard library only).

    APIFY_TOKEN=... python fetch_gaeb_tenders.py "Wärmepumpe" "Photovoltaik" > positions.csv
"""
import csv, json, os, sys, urllib.request

URL = "https://api.apify.com/v2/acts/brsksr~german-construction-tenders-gaeb/run-sync-get-dataset-items"
run_input = {"pubDaysBack": 1, "cpvPrefixes": ["45"], "keywords": sys.argv[1:], "onlyWithGaeb": True, "maxTenders": 10}

req = urllib.request.Request(URL, data=json.dumps(run_input).encode(), method="POST", headers={
    "Content-Type": "application/json", "Authorization": f"Bearer {os.environ['APIFY_TOKEN']}"})
with urllib.request.urlopen(req, timeout=310) as resp:  # run-sync waits up to 300 s
    tenders = json.load(resp)

out = csv.writer(sys.stdout)
out.writerow(["tender", "deadline", "postalCode", "oz", "shortText", "quantity", "unit"])
for t in tenders:
    hits = {h["oz"] for h in t.get("keywordPositionHits", [])}
    for p in t["positions"]:
        if not hits or p["oz"] in hits:  # with keywords: only the matching positions
            out.writerow([t["title"], t["submissionDeadline"], (t["location"] or {}).get("postalCode"),
                          p["oz"], p["shortText"], p["quantity"], p["unit"]])
