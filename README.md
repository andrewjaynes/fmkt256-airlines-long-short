# Sector One-Pagers + AI Long/Short (FMKT 256 Extra Credit, Option 2)

**Team:** Andrew Jaynes (ahj20), Finn Kelly (fmk11), Ryan Readlinger (rr407)

This tool takes a list of tickers and produces a PDF with:

- a one-page summary of every company, with live quantitative metrics, peer medians and ranks, charts, and an AI-written qualitative assessment
- a sector comparison dashboard
- an AI-argued **best long** and **best short**

**Deliverable:** [`output/airlines/airlines_report.pdf`](output/airlines/airlines_report.pdf) (9 U.S. airlines, 14 pages)

---

## Reusing it: new companies or new data, no new code

Everything is driven by a plain-text **sector file**. The code never changes.

| I want to… | Do this |
|---|---|
| Refresh with today's data | `python run.py` (re-run the same command) |
| Add or drop a company | Edit the `tickers:` list in `sectors/airlines.yaml`, re-run |
| Cover a whole new sector | Copy the sector file, change `sector`, `slug` and `tickers`, then run `python run.py sectors/<new>.yaml` |
| Change the scoring emphasis | Edit the `weights:` numbers in the sector file |
| Force fresh AI write-ups | `python run.py --refresh-ai` (needs an API key) |
| Rebuild the PDF without changing any numbers | `python run.py --no-fetch` |
| Change what the AI writes | Edit the plain-English prompts in `prompts/` |

`sectors/railroads.yaml` is included as a working second example. Running
`python run.py sectors/railroads.yaml` produced `output/railroads/railroads_report.pdf`
with zero code changes.

### How the AI part works (three no-code options)

1. **Claude API (fully automatic).** Set `ANTHROPIC_API_KEY`. Claude searches the web for each company's latest earnings and news, writes every one-pager, then picks the long and short.
2. **Copy-paste (no key needed).** For any company without a write-up, the tool saves a ready-to-paste prompt in `output/<sector>/prompts_to_paste/`. Paste it into Claude.ai or ChatGPT, save the JSON reply as `analysis/<sector>/<TICKER>.json`, and re-run.
3. **Saved write-ups.** Anything in `analysis/<sector>/` is reused, so prices and scores refresh daily while the narrative stays put until you choose to update it.

The AI write-ups in this edition were produced by Claude (Opus 5.5) in Claude Code. It
searched the web for the Q3 2026 earnings coverage, saw the same metrics block the prompt
supplies, and returned the JSON format defined in `prompts/`. Sources are cited on every page.

---

## Setup (one time)

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/python run.py
```

PDF output needs Google Chrome, Chromium or Edge installed. Without one, open
`output/<sector>/report.html` and use Print → Save as PDF.

## Project layout

```
run.py                 one command that runs the whole pipeline
sectors/*.yaml         INPUT: sector name, tickers, weights (the only file you edit)
prompts/*.md           the plain-English instructions given to the AI
src/fetch.py           1. pull prices, statements, consensus (Yahoo Finance)
src/score.py           2. metrics, peer medians, percentile ranks, composite score
src/ai.py              3. AI write-ups + long/short (API, saved, or copy-paste)
src/render.py          4. charts + HTML -> PDF
templates/             page layout
data/<sector>/         raw data snapshot from the last run
analysis/<sector>/     AI write-ups (JSON), one per company + long_short.json
output/<sector>/       the finished report (PDF + HTML)
```

## Scoring method

Eleven metrics are percentile-ranked within the peer group, averaged into five pillars,
then weighted (default weights shown, editable in the sector file):

- Valuation 25%: EV/EBITDA, forward P/E
- Profitability 20%: operating margin, net margin, ROE
- Balance sheet 25%: net debt/EBITDA, cash/revenue
- Momentum 15%: 1-year return, distance from 52-week high
- Street 15%: upside to consensus target, short interest

The AI starts from this screen but may override it if it explains why. In this edition it
picked SKYW over the #1-ranked UAL because of SkyWest's fuel pass-through contracts.

*For educational purposes only. Not investment advice.*
