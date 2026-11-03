You are an equity research analyst covering the {sector} sector. Today is {today}.

Write the qualitative half of a one-page summary for **{name} ({ticker})**. The
quantitative half (valuation, margins, leverage, returns, peer ranks) is already
computed from live data and shown below. Use it, do not contradict it, and do
not invent any other numbers. If you cite a figure that is not in the data
below (for example, from the latest earnings release), it must come from a
source you list in "sources".

Before writing, search the web for this company's most recent quarterly
earnings release, guidance changes, and material news from the last 6 months.

Sector context: {sector_context}

LIVE DATA FOR {ticker} (peer median in brackets, rank 1 = best of {n}):
{metrics_block}

Peer composite ranking (1 = most attractive on the quantitative screen):
{peer_ranking}

Return ONLY a JSON object, with no other text, in exactly this shape:
{{
  "ticker": "{ticker}",
  "model_type": "short label for the business model, e.g. 'Global network carrier'",
  "headline": "one sentence investment takeaway, at most 25 words",
  "business": "2-3 sentences: what the company does, scale, network/hubs, what makes it different",
  "recent": ["3 bullets on the latest quarter and guidance, each with concrete figures from your sources"],
  "strengths": ["3 short bullets"],
  "risks": ["3 short bullets"],
  "catalysts": ["2-3 short bullets: dated events or drivers over the next 6-12 months"],
  "stance": "Overweight | Neutral | Underweight",
  "sources": [{{"title": "...", "url": "https://..."}}]
}}
Keep every bullet under 30 words. The whole write-up must fit on half a page.
