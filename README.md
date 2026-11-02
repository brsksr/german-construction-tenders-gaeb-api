# German Public Procurement API: construction tenders + GAEB bill of quantities as JSON

**GAEB Parser API for German construction tenders.** Daily public construction tenders from the official
[oeffentlichevergabe.de API](https://oeffentlichevergabe.de), with the complete **GAEB bill of quantities
(Leistungsverzeichnis, `.x83` `.d83` `.p83` to JSON)** of every tender: OZ, short text, long text, quantity, unit.
No portal account, no manual download, no PDF guessing.

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-F86606?style=for-the-badge)](https://apify.com/brsksr/german-construction-tenders-gaeb)
[![n8n template](https://img.shields.io/badge/n8n-workflow%20template-EA4B71?style=for-the-badge)](n8n/daily-german-gaeb-tenders-workflow.json)
[![MCP](https://img.shields.io/badge/MCP-Claude%20%7C%20Cursor%20%7C%20OpenAI-black?style=for-the-badge)](mcp/README.md)

🇬🇧 [English](#english) · 🇩🇪 [Deutsch](#deutsch)

This repository contains **integration templates and examples** for the hosted Apify Actor
[**German Construction Tenders + GAEB Bill of Quantities Extractor**](https://apify.com/brsksr/german-construction-tenders-gaeb).
The extraction itself runs on Apify; you call it through the Apify API, n8n, Make, Zapier or an AI agent via MCP.

| Folder | What it is |
|---|---|
| [`n8n/`](n8n/daily-german-gaeb-tenders-workflow.json) | Importable **n8n Vergabe workflow**: every weekday 07:00, new tenders whose LV mentions your keywords |
| [`mcp/`](mcp/README.md) | MCP configs for **Claude Desktop, Cursor, Claude Code and the OpenAI Agents SDK** + example prompts |
| [`examples/`](examples/) | [`fetch_gaeb_tenders.py`](examples/fetch_gaeb_tenders.py) (GAEB positions as CSV, standard library only) and [`curl_quickstart.sh`](examples/curl_quickstart.sh) |

---

<a id="english"></a>

## 🇬🇧 What you get

- **German public procurement data as an API:** every construction notice (CPV 45) from the national notice
  service oeffentlichevergabe.de, filterable by publication day, CPV code, postal code and NUTS region.
- **GAEB .x83 .d83 .p83 to JSON:** the Actor opens the public tender documents on the e-procurement platform,
  finds the GAEB file and parses it: GAEB DA XML 3.x (`.x83`), GAEB 90 (`.d83`) and GAEB 2000 (`.p83`).
- **Keyword search inside the bill of quantities:** `keywords` are matched against title, description **and every
  position's short and long text**. Hits come back with their OZ (ordinal number).
- **Deadline, place of performance, buyer, reference number** for every tender, normalised (ISO 8601, Europe/Berlin).
- **Fair pay-per-event pricing:** you pay only for tenders with at least one extracted LV position. Tenders without
  public documents, PDF-only bills of quantities or login-only procedures are free.

### Supported e-procurement platforms

Documents are read anonymously (§ 41 VgV: free, unrestricted, direct access) from:
**evergabe-online.de** (federal) · **evergabe.de** · **subreport ELViS** · **Cosinex** marketplaces
(DTVP, Vergabemarktplatz NRW, Niedersachsen, Brandenburg, Baden-Württemberg, Rheinland-Pfalz, …) ·
**AI NetServer** platforms (HAD Hessen, Vergabeplattform Hessen, Land Baden-Württemberg, Bremen, Düsseldorf,
Köln, Frankfurt, tender24, Die Autobahn GmbH, …) · **Healy Hudson** bidder portals (Deutsche Bahn, Hamburg) ·
**Deutsche eVergabe** · **RIB meinauftrag**.

Live check on two working days (29/30 Oct 2026, 648 construction notices): **551 notices (85 %) are on supported
platforms; 347 of them yielded a parsed bill of quantities with 70,983 positions.** Per-platform hit rates are in the
[Actor README](https://apify.com/brsksr/german-construction-tenders-gaeb). *Die Autobahn's platform currently does not
answer requests from the Apify cloud; those tenders are reported as `portal_unreachable` and are free.*

### Quickstart (cURL)

```bash
export APIFY_TOKEN=...   # https://console.apify.com/settings/integrations
curl -sS -X POST "https://api.apify.com/v2/acts/brsksr~german-construction-tenders-gaeb/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"pubDaysBack": 1, "keywords": ["Wärmepumpe"], "onlyWithGaeb": true, "maxTenders": 5}'
```

The synchronous endpoint waits up to 300 seconds; keep filters narrow or start the run asynchronously
(`POST /v2/acts/brsksr~german-construction-tenders-gaeb/runs`) for large searches.

### Python: GAEB positions as CSV

```bash
APIFY_TOKEN=... python examples/fetch_gaeb_tenders.py "Brandschutztür" > positions.csv
```

### Main input fields

| Field | Example | Meaning |
|---|---|---|
| `pubDaysBack` / `pubDays` | `1` / `["2026-10-30"]` | Which daily notice exports to load |
| `cpvPrefixes` | `["45"]`, `["4526"]` | CPV filter (45 = construction, 4526 = roofing, 45233 = road construction) |
| `postalCodePrefixes` / `nutsPrefixes` | `["01", "04"]` / `["DED"]` | Region of the place of performance |
| `keywords` | `["Wärmepumpe", "Gussasphalt"]` | Searched in notice **and** all LV positions |
| `onlyWithGaeb` | `true` | Only return tenders with an extracted bill of quantities |
| `maxTenders` | `20` | Upper limit of returned tenders per run |

Full schema and all options: [Actor input](https://apify.com/brsksr/german-construction-tenders-gaeb/input-schema).
Ready-made example run: [GAEB Leistungsverzeichnis keyword search](https://apify.com/brsksr/german-construction-tenders-gaeb/examples/gaeb-leistungsverzeichnis-keyword-search).

### Example output: a real parsed GAEB position

One dataset item per tender (shortened: one of 51 positions shown, buyer contact omitted):

```json
{
  "title": "Neubau Kita Kuhweid und MGH Weinheim, Tischlerarbeiten Innentüren",
  "pubDay": "2026-10-29",
  "buyer": { "name": "Stadt Weinheim", "postalCode": "69469", "city": "Weinheim", "nutsCode": "DE128" },
  "cpvCodes": ["45421000"],
  "location": { "postalCode": "69469", "city": "Weinheim", "street": "Kurt-Schumacher-Str. 17+19",
                "nutsCode": "DE128", "region": "Baden-Württemberg", "source": "placeOfPerformance" },
  "submissionDeadline": "2026-11-30T11:00:00+01:00",
  "deadlineType": "offer",
  "referenceNumber": "SWEIN-2026-0020",
  "portal": "vergabe.vmstart.de",
  "gaebFiles": [{ "fileName": "LV Tischler Innentueren.x83", "format": "GAEB DA XML", "version": "3.3",
                  "exchangePhase": "83", "boqName": "Tischler - Innentüren", "positionCount": 51 }],
  "positionCount": 51,
  "positions": [
    {
      "oz": "1.1.2.1",
      "category": "Feuchtraumtüren",
      "categoryPath": ["Gebäue KITA", "innentürelemente ohne Anforderungen Feuerwiderstand", "Feuchtraumtüren"],
      "shortText": "Innentürel. Feuchtraumtür Drehflügeltür 1flg B 915 mm H 2125 mm 27dB Klimakl.I Prüfklima a Umfassungszarge Stahlblech D 1,5mm Maulweite 170 mm Holzwerkstoff PZ-Schloss",
      "longText": "Innentürelement aus Türblatt und Zarge, Feuchtraumtür, als Drehflügeltür, einflügelig, stumpf einschlagend, …",
      "quantity": 1,
      "unit": "St",
      "positionType": "normal",
      "isLumpSum": false,
      "refOz": null,
      "sourceFile": "LV Tischler Innentueren.x83"
    }
  ],
  "matchedKeywords": [],
  "keywordPositionHits": [],
  "status": "gaeb_extracted"
}
```

This run used no keywords. With `"keywords": ["Feuchtraumtür"]` the same tender would list
`"matchedKeywords": ["Feuchtraumtür"]` and `"keywordPositionHits": [{"oz": "1.1.2.1", "keywords": ["Feuchtraumtür"]}]`.

### Use cases

- **Building material suppliers and manufacturers:** every tender whose LV specifies your product category, with quantities for lead scoring.
- **Contractors and estimators:** pre-screen tenders by scope and import positions into your calculation software.
- **n8n / Make / Zapier:** daily schedule → CRM, Slack, Teams, Google Sheets. Start with the [n8n template](n8n/daily-german-gaeb-tenders-workflow.json).
- **AI agents (MCP):** let Claude, Cursor or an OpenAI agent answer questions such as *"Which tenders in Saxony need more than 200 m of railings?"* from real BoQ data. See [`mcp/`](mcp/README.md).

---

<a id="deutsch"></a>

## 🇩🇪 Öffentliche Bauausschreibungen + GAEB-Leistungsverzeichnis als JSON-API

**Leistungsverzeichnis automatisch auslesen, ohne Portal-Account.** Der Apify Actor
[German Construction Tenders + GAEB Bill of Quantities Extractor](https://apify.com/brsksr/german-construction-tenders-gaeb)
lädt täglich alle Bauausschreibungen aus der **oeffentlichevergabe.de API** (amtlicher Bekanntmachungsservice),
öffnet die frei zugänglichen Vergabeunterlagen und wandelt das **GAEB-Leistungsverzeichnis (.x83, .d83, .p83) in JSON**
um: Ordnungszahl (OZ), Kurztext, Langtext, Menge, Einheit, Positionsart.

- **GAEB-Parser für alle drei Formate:** GAEB DA XML 3.x (`.x83`), GAEB 90 (`.d83`), GAEB 2000 (`.p83`).
- **Keyword-Suche direkt in den LV-Positionen:** z. B. „Wärmepumpe“, „Gussasphalt“, „Brandschutztür“ in Kurz- und Langtexten; Treffer mit OZ.
- **Angebotsfrist, Ausführungsort, Vergabestelle und Vergabenummer** zu jeder Ausschreibung.
- **Faire Abrechnung:** Kosten nur für Ausschreibungen mit mindestens einer extrahierten LV-Position.

**Unterstützte Vergabeplattformen:** evergabe-online.de, evergabe.de, subreport ELViS, Cosinex-Vergabemarktplätze
(DTVP, Vergabemarktplatz NRW, Niedersachsen, Brandenburg, Baden-Württemberg, Rheinland-Pfalz u. a.),
AI-NetServer-Plattformen (HAD Hessen, Vergabeplattform Hessen, Land Baden-Württemberg, Bremen, Düsseldorf, Köln,
Frankfurt, tender24, Die Autobahn GmbH u. a.), Healy-Hudson-Bieterportale (Deutsche Bahn, Hamburg), Deutsche eVergabe
und RIB meinauftrag. Stichprobe 29./30.10.2026: **551 von 648 Bau-Bekanntmachungen (85 %) liegen auf unterstützten
Plattformen, bei 347 wurde das Leistungsverzeichnis mit 70.983 Positionen extrahiert.** Die Plattform der Autobahn GmbH
antwortet derzeit nicht auf Anfragen aus der Apify-Cloud; diese Ausschreibungen erhalten `portal_unreachable` und sind kostenlos.

### Schnellstart

- **n8n Vergabe Workflow:** [`n8n/daily-german-gaeb-tenders-workflow.json`](n8n/daily-german-gaeb-tenders-workflow.json) in n8n importieren
  (*Workflows → Import from File*), Apify-Token in der URL des HTTP-Knotens eintragen, Suchbegriffe im JSON-Body anpassen.
  Der Workflow läuft werktags um 7:00 Uhr und liefert je Ausschreibung Vergabestelle, Frist, Ort, Anzahl der GAEB-Positionen
  und die Keyword-Treffer mit Textauszug aus dem Langtext, fertig für E-Mail, Slack oder CRM.
- **KI-Agenten (MCP):** Konfigurationen für Claude Desktop, Cursor, Claude Code und das OpenAI Agents SDK in [`mcp/`](mcp/README.md),
  inklusive Beispiel-Prompts wie *„Suche alle aktuellen Bauausschreibungen in Sachsen mit GAEB-Positionen für Brandschutztüren und erstelle eine Mengen-Tabelle.“*
- **Python / cURL:** [`examples/`](examples/).

### Typische Einsatzszenarien

- **Baustoffhandel und Hersteller:** jeden Morgen alle Ausschreibungen im Vertriebsgebiet, deren LV Ihr Produkt enthält, inklusive Mengen.
- **Bauunternehmen und Kalkulation:** Ausschreibungen nach Leistungsumfang vorfiltern, Positionen direkt in die Kalkulation übernehmen.
- **Automatisierung mit n8n, Make oder Zapier:** Treffer als Lead ins CRM, nach Teams, Slack oder Google Sheets.

---

## Links

- Apify Actor: https://apify.com/brsksr/german-construction-tenders-gaeb
- Example task (keyword search in the LV): https://apify.com/brsksr/german-construction-tenders-gaeb/examples/gaeb-leistungsverzeichnis-keyword-search
- Apify API docs (run Actor synchronously): https://docs.apify.com/api/v2/act-run-sync-get-dataset-items-post
- Apify MCP server: https://mcp.apify.com

*Data source: open-data notice exports of oeffentlichevergabe.de and the public tender documents of the respective
e-procurement platforms. This repository contains only integration templates and examples; the extraction runs as a
hosted Apify Actor.*
