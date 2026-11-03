You are an equity research analyst covering the U.S. Class I Railroads sector. Today is 2026-11-03.

Write the qualitative half of a one-page summary for **Union Pacific Corporation (UNP)**. The
quantitative half (valuation, margins, leverage, returns, peer ranks) is already
computed from live data and shown below. Use it, do not contradict it, and do
not invent any other numbers. If you cite a figure that is not in the data
below (for example, from the latest earnings release), it must come from a
source you list in "sources".

Before writing, search the web for this company's most recent quarterly
earnings release, guidance changes, and material news from the last 6 months.

Sector context: Key railroad value drivers: volume (carloads/intermodal), pricing above inflation, operating ratio, precision scheduled railroading, fuel surcharge lag, merger and regulatory (STB) outcomes, and capital intensity.


LIVE DATA FOR UNP (peer median in brackets, rank 1 = best of 8):
- Market cap: $182.4B [$76.8B]
- Enterprise value: $210.5B [$96.2B]
- EV / EBITDA (TTM): 15.8x [14.5x] (rank 6/8)
- P/E (forward): 21.3x [21.5x] (rank 4/8)
- P/E (trailing): 23.9x [25.5x]
- Price / book: 8.3x [4.4x]
- Revenue (TTM): $26.4B [$14.0B]
- Revenue growth (latest qtr YoY): +15.3% [+14.1%]
- Operating margin (TTM): 40.1% [36.1%] (rank 1/8)
- Net margin (TTM): 28.9% [22.3%] (rank 1/8)
- Return on equity: 38.7% [19.6%] (rank 1/8)
- Total debt: $31.1B [$18.3B]
- Cash & investments: $3.1B [$624M]
- Net debt / EBITDA: 2.1x [2.6x] (rank 1/8)
- Cash / revenue: 11.7% [9.5%] (rank 2/8)
- Free cash flow (TTM): $5.1B [$2.0B]
- 1-year total return: +43.3% [+32.6%] (rank 2/8)
- vs. 52-week high: -2.8% [-4.6%] (rank 1/8)
- Upside to mean target: +7.9% [+6.0%] (rank 2/8)
- Short interest (% float): 5.2% [3.2%] (rank 5/8)
- Beta: 0.84 [1.13]
- Composite score: 80/100 (rank 1/8)
- Pillars: Valuation 50, Profitability 100, Balance sheet 94, Momentum 94, Street view 65

Peer composite ranking (1 = most attractive on the quantitative screen):
1. UNP (80)
2. CNI (67)
3. CSX (64)
4. CP (55)
5. NSC (51)
6. WAB (47)
7. TRN (46)
8. GBX (38)

Return ONLY a JSON object, with no other text, in exactly this shape:
{
  "ticker": "UNP",
  "model_type": "short label for the business model, e.g. 'Global network carrier'",
  "headline": "one sentence investment takeaway, at most 25 words",
  "business": "2-3 sentences: what the company does, scale, network/hubs, what makes it different",
  "recent": ["3 bullets on the latest quarter and guidance, each with concrete figures from your sources"],
  "strengths": ["3 short bullets"],
  "risks": ["3 short bullets"],
  "catalysts": ["2-3 short bullets: dated events or drivers over the next 6-12 months"],
  "stance": "Overweight | Neutral | Underweight",
  "sources": [{"title": "...", "url": "https://..."}]
}
Keep every bullet under 30 words. The whole write-up must fit on half a page.
