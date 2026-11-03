You are an equity research analyst covering the U.S. Class I Railroads sector. Today is 2026-11-03.

Write the qualitative half of a one-page summary for **Canadian Pacific Kansas City Limited (CP)**. The
quantitative half (valuation, margins, leverage, returns, peer ranks) is already
computed from live data and shown below. Use it, do not contradict it, and do
not invent any other numbers. If you cite a figure that is not in the data
below (for example, from the latest earnings release), it must come from a
source you list in "sources".

Before writing, search the web for this company's most recent quarterly
earnings release, guidance changes, and material news from the last 6 months.

Sector context: Key railroad value drivers: volume (carloads/intermodal), pricing above inflation, operating ratio, precision scheduled railroading, fuel surcharge lag, merger and regulatory (STB) outcomes, and capital intensity.


LIVE DATA FOR CP (peer median in brackets, rank 1 = best of 8):
- Market cap: $79.6B [$76.8B]
- Enterprise value: $106.0B [$96.2B]
- EV / EBITDA (TTM): 12.5x [14.5x] (rank 2/8)
- P/E (forward): 21.8x [21.5x] (rank 5/8)
- P/E (trailing): 29.3x [25.5x]
- Price / book: 2.4x [4.4x]
- Revenue (TTM): $16.0B [$14.0B]
- Revenue growth (latest qtr YoY): +15.2% [+14.1%]
- Operating margin (TTM): 36.4% [36.1%] (rank 4/8)
- Net margin (TTM): 24.1% [22.3%] (rank 3/8)
- Return on equity: 8.3% [19.6%] (rank 7/8)
- Total debt: $25.8B [$18.3B]
- Cash & investments: $399M [$624M]
- Net debt / EBITDA: 3.0x [2.6x] (rank 6/8)
- Cash / revenue: 2.5% [9.5%] (rank 8/8)
- Free cash flow (TTM): $2.7B [$2.0B]
- 1-year total return: +30.2% [+32.6%] (rank 5/8)
- vs. 52-week high: -5.6% [-4.6%] (rank 5/8)
- Upside to mean target: +7.8% [+6.0%] (rank 3/8)
- Short interest (% float): 2.1% [3.2%] (rank 1/8)
- Beta: 1.16 [1.13]
- Composite score: 55/100 (rank 4/8)
- Pillars: Valuation 69, Profitability 54, Balance sheet 25, Momentum 50, Street view 88

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
  "ticker": "CP",
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
