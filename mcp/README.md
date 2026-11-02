# German construction tenders + GAEB bills of quantities as an MCP tool

Give Claude, Cursor, ChatGPT or your own OpenAI agent a tool that searches German public construction tenders
(oeffentlichevergabe.de) and returns the parsed GAEB bill of quantities (Leistungsverzeichnis) of each tender:
OZ, short text, long text, quantity, unit. The tool is the Apify Actor
[`brsksr/german-construction-tenders-gaeb`](https://apify.com/brsksr/german-construction-tenders-gaeb), served by the
official Apify MCP server [`@apify/actors-mcp-server`](https://www.npmjs.com/package/@apify/actors-mcp-server).

You need an [Apify API token](https://console.apify.com/settings/integrations). Keep it out of repositories.
You pay only for tenders with at least one extracted GAEB position (see the Actor's *Pricing* tab).

## Claude Desktop

Copy [`claude_desktop_config.json`](claude_desktop_config.json) into your Claude Desktop config
(*Settings → Developer → Edit Config*; macOS `~/Library/Application Support/Claude/claude_desktop_config.json`,
Windows `%APPDATA%\Claude\claude_desktop_config.json`), replace `YOUR_APIFY_TOKEN` and restart Claude.
Requires Node.js 22+. The `--tools` flag limits the server to this one Actor (plus Apify's run/storage helpers).

Without Node.js: *Settings → Connectors → Add custom connector*, URL
`https://mcp.apify.com?tools=brsksr/german-construction-tenders-gaeb`, sign in with Apify (OAuth).

## Cursor

Copy [`cursor_mcp.json`](cursor_mcp.json) to `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project)
and replace `YOUR_APIFY_TOKEN`. It uses the hosted server, so nothing runs locally. Alternatively run
`apify mcp install cursor` with the [Apify CLI](https://docs.apify.com/cli) and add `?tools=brsksr/german-construction-tenders-gaeb` to the URL.

## Claude Code

```bash
claude mcp add german-tenders "https://mcp.apify.com?tools=brsksr/german-construction-tenders-gaeb" -t http \
  -H "Authorization: Bearer $APIFY_TOKEN"
```

## OpenAI Agents SDK (Python)

```python
import asyncio, os
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async def main():
    async with MCPServerStreamableHttp(
        name="german-construction-tenders-gaeb",
        params={
            "url": "https://mcp.apify.com?tools=brsksr/german-construction-tenders-gaeb",
            "headers": {"Authorization": f"Bearer {os.environ['APIFY_TOKEN']}"},
            "timeout": 60,
            "sse_read_timeout": 900,
        },
        client_session_timeout_seconds=600,  # an Actor run can take a few minutes
    ) as tenders:
        agent = Agent(
            name="Tender analyst",
            instructions="Use the German construction tenders tool. Answer with tables; quote OZ numbers.",
            mcp_servers=[tenders],
        )
        result = await Runner.run(agent, "Which tenders published yesterday contain heat pumps (Wärmepumpe)?")
        print(result.final_output)

asyncio.run(main())
```

ChatGPT (Developer mode / connectors) accepts the same URL as a remote MCP server.

## Example prompts / Beispiel-Prompts

1. **Mengen-Tabelle Brandschutztüren (Sachsen)**
   > Suche alle Bauausschreibungen der letzten 3 Tage in Sachsen (PLZ 01, 02, 04, 08, 09) mit GAEB-Positionen zu Brandschutztüren (Keywords „Brandschutztür“, „T30“, „T90“, „EI2 30“) und erstelle eine Mengen-Tabelle: Ausschreibung, Vergabestelle, Frist, OZ, Kurztext, Menge, Einheit.

2. **Heat-pump sales leads (Bavaria, English)**
   > Find German public construction tenders published in the last 2 days in Bavaria (NUTS DE2) whose bill of quantities mentions "Wärmepumpe" or "Luft-Wasser-Wärmepumpe". For each tender list buyer, submission deadline, place of performance and the matching positions with quantity and unit, sorted by deadline.

3. **Kalkulations-Vorbereitung Straßenbau**
   > Lade die Bauausschreibungen von gestern mit CPV 45233 (Straßenbau) und extrahiertem Leistungsverzeichnis. Summiere je Ausschreibung die Mengen für Asphaltdeckschicht, Asphaltbinderschicht und Gussasphalt (Einheit m² bzw. t) und markiere Ausschreibungen mit mehr als 5.000 m² Asphaltfläche.

Tip: the agent maps these requests to the Actor input (`pubDaysBack`, `postalCodePrefixes`, `nutsPrefixes`,
`cpvPrefixes`, `keywords`, `maxTenders`). Narrow filters make runs faster and cheaper.
