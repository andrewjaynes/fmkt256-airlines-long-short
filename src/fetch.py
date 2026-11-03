"""Step 1: pull live market + financial data for every ticker (Yahoo Finance)."""
import json
import math
import warnings
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

INFO_FIELDS = [
    "shortName", "longName", "exchange", "industry", "city", "state", "website",
    "fullTimeEmployees", "longBusinessSummary",
    "currentPrice", "marketCap", "enterpriseValue", "sharesOutstanding",
    "trailingPE", "forwardPE", "enterpriseToEbitda", "enterpriseToRevenue", "priceToBook",
    "trailingEps", "forwardEps",
    "totalRevenue", "ebitda", "revenueGrowth", "earningsGrowth",
    "grossMargins", "operatingMargins", "profitMargins", "ebitdaMargins",
    "returnOnEquity", "returnOnAssets",
    "totalDebt", "totalCash", "freeCashflow", "operatingCashflow", "debtToEquity",
    "currentRatio", "beta", "dividendYield",
    "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "fiftyDayAverage", "twoHundredDayAverage",
    "shortPercentOfFloat", "recommendationMean", "recommendationKey",
    "targetMeanPrice", "targetHighPrice", "targetLowPrice", "numberOfAnalystOpinions",
]


def _clean(v):
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if hasattr(v, "item"):
        return _clean(v.item())
    return v


def _row(df: pd.DataFrame, *names):
    for n in names:
        if df is not None and not df.empty and n in df.index:
            return df.loc[n]
    return None


def fetch_one(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    info = t.info or {}
    out = {"ticker": ticker, "info": {k: _clean(info.get(k)) for k in INFO_FIELDS}}

    # Quarterly income statement -> revenue / operating income / net income trend
    q = t.quarterly_income_stmt
    quarters = []
    if q is not None and not q.empty:
        rev = _row(q, "Total Revenue", "Operating Revenue")
        opi = _row(q, "Operating Income", "Total Operating Income As Reported")
        ni = _row(q, "Net Income", "Net Income Common Stockholders")
        for col in sorted(q.columns)[-8:]:
            if rev is None or _clean(rev[col]) is None:   # skip quarters Yahoo hasn't filled in yet
                continue
            quarters.append({
                "period": col.strftime("%Y-%m-%d"),
                "label": f"Q{(col.month - 1) // 3 + 1} '{str(col.year)[2:]}",
                "revenue": _clean(rev[col]) if rev is not None else None,
                "operating_income": _clean(opi[col]) if opi is not None else None,
                "net_income": _clean(ni[col]) if ni is not None else None,
            })
    out["quarters"] = quarters

    # Latest balance sheet cash & debt (fallback for info fields)
    bs = t.quarterly_balance_sheet
    if bs is not None and not bs.empty:
        col = sorted(bs.columns)[-1]
        debt = _row(bs, "Total Debt")
        cash = _row(bs, "Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents")
        out["balance_sheet_date"] = col.strftime("%Y-%m-%d")
        if out["info"].get("totalDebt") is None and debt is not None:
            out["info"]["totalDebt"] = _clean(debt[col])
        if out["info"].get("totalCash") is None and cash is not None:
            out["info"]["totalCash"] = _clean(cash[col])

    # One year of daily closes for performance / chart
    hist = t.history(period="1y", auto_adjust=True)
    out["prices"] = [
        {"date": d.strftime("%Y-%m-%d"), "close": round(float(c), 4)}
        for d, c in zip(hist.index, hist["Close"])
    ]
    return out


def fetch_all(tickers, data_dir: Path) -> dict:
    data_dir.mkdir(parents=True, exist_ok=True)
    companies = {}
    for tk in tickers:
        print(f"  fetching {tk} ...", flush=True)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                companies[tk] = fetch_one(tk)
        except Exception as e:  # keep going if one ticker fails
            print(f"  !! {tk} failed: {e}")
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Yahoo Finance via yfinance (prices, statements, consensus)",
        "companies": companies,
    }
    (data_dir / "raw_data.json").write_text(json.dumps(payload, indent=1))
    return payload
