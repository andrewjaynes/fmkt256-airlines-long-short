You are an equity research analyst covering the U.S. Class I Railroads sector. Today is 2026-11-03.

Write the qualitative half of a one-page summary for **Canadian National Railway Company (CNI)**. The
quantitative half (valuation, margins, leverage, returns, peer ranks) is already
computed from live data and shown below. Use it, do not contradict it, and do
not invent any other numbers. If you cite a figure that is not in the data
below (for example, from the latest earnings release), it must come from a
source you list in "sources".

Before writing, search the web for this company's most recent quarterly
earnings release, guidance changes, and material news from the last 6 months.

Sector context: Key railroad value drivers: volume (carloads/intermodal), pricing above inflation, operating ratio, precision scheduled railroading, fuel surcharge lag, merger and regulatory (STB) outcomes, and capital intensity.


LIVE DATA FOR CNI (peer median in brackets, rank 1 = best of 8):
- Market cap: $76.0B [$76.8B]
- Enterprise value: $99.1B [$96.2B]
- EV / EBITDA (TTM): 10.6x [14.5x] (rank 1/8)
- P/E (forward): 19.8x [21.5x] (rank 3/8)
- P/E (trailing): 22.1x [25.5x]
- Price / book: 4.9x [4.4x]
- Revenue (TTM): $18.4B [$14.0B]
- Revenue growth (latest qtr YoY): +14.5% [+14.1%]
- Operating margin (TTM): 37.6% [36.1%] (rank 2/8)
- Net margin (TTM): 26.4% [22.3%] (rank 2/8)
- Return on equity: 22.4% [19.6%] (rank 4/8)
- Total debt: $23.9B [$18.3B]
- Cash & investments: $770M [$624M]
- Net debt / EBITDA: 2.5x [2.6x] (rank 3/8)
- Cash / revenue: 4.2% [9.5%] (rank 6/8)
- Free cash flow (TTM): $2.5B [$2.0B]
- 1-year total return: +34.9% [+32.6%] (rank 4/8)
- vs. 52-week high: -3.6% [-4.6%] (rank 3/8)
- Upside to mean target: +7.6% [+6.0%] (rank 4/8)
- Short interest (% float): n/a [3.2%]
- Beta: 0.95 [1.13]
- Composite score: 67/100 (rank 2/8)
- Pillars: Valuation 88, Profitability 79, Balance sheet 56, Momentum 69, Street view 31

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
  "ticker": "CNI",
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
