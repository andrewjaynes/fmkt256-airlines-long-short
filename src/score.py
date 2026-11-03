"""Step 2: turn raw data into comparable metrics, peer ranks and a composite score."""
from statistics import median


def _ttm(quarters, key):
    vals = [q.get(key) for q in quarters[-4:]]
    if len(vals) < 4 or any(v is None for v in vals):
        return None
    return sum(vals)


def _pos(v):
    """Ratios like EV/EBITDA or P/E are meaningless when negative -> treat as missing."""
    return v if (v is not None and v > 0) else None


def derive(c: dict) -> dict:
    i, qs, px = c["info"], c.get("quarters", []), c.get("prices", [])
    price = i.get("currentPrice") or (px[-1]["close"] if px else None)
    rev_ttm, opi_ttm, ni_ttm = _ttm(qs, "revenue"), _ttm(qs, "operating_income"), _ttm(qs, "net_income")
    revenue = rev_ttm or i.get("totalRevenue")
    debt, cash, ebitda = i.get("totalDebt"), i.get("totalCash"), i.get("ebitda")
    net_debt = (debt - cash) if (debt is not None and cash is not None) else None

    # Latest-quarter YoY revenue growth from statements when 5 quarters exist
    rev_growth = i.get("revenueGrowth")
    if len(qs) >= 5 and qs[-1]["revenue"] and qs[-5]["revenue"]:
        rev_growth = qs[-1]["revenue"] / qs[-5]["revenue"] - 1

    ret_1y = (px[-1]["close"] / px[0]["close"] - 1) if len(px) > 1 else None
    ret_3m = (px[-1]["close"] / px[-64]["close"] - 1) if len(px) > 64 else None
    hi = i.get("fiftyTwoWeekHigh")
    target = i.get("targetMeanPrice")

    return {
        "price": price,
        "market_cap": i.get("marketCap"),
        "enterprise_value": i.get("enterpriseValue"),
        "revenue_ttm": revenue,
        "rev_growth": rev_growth,
        "op_margin": (opi_ttm / rev_ttm) if (opi_ttm is not None and rev_ttm) else i.get("operatingMargins"),
        "net_margin": (ni_ttm / rev_ttm) if (ni_ttm is not None and rev_ttm) else i.get("profitMargins"),
        "roe": i.get("returnOnEquity"),
        "ev_ebitda": _pos(i.get("enterpriseToEbitda")) if (ebitda or 0) > 0 else None,
        "pe_ttm": _pos(i.get("trailingPE")),
        "pe_fwd": _pos(i.get("forwardPE")),
        "p_b": _pos(i.get("priceToBook")),
        "ebitda": ebitda,
        "total_debt": debt,
        "total_cash": cash,
        "net_debt": net_debt,
        "net_debt_ebitda": (net_debt / ebitda) if (net_debt is not None and ebitda and ebitda > 0) else None,
        "cash_to_rev": (cash / revenue) if (cash is not None and revenue) else None,
        "fcf": i.get("freeCashflow"),
        "ret_1y": ret_1y,
        "ret_3m": ret_3m,
        "pct_off_high": (price / hi - 1) if (price and hi) else None,
        "upside": (target / price - 1) if (price and target) else None,
        "short_pct": i.get("shortPercentOfFloat"),
        "rec_mean": i.get("recommendationMean"),
        "beta": i.get("beta"),
        "div_yield": i.get("dividendYield"),
        "employees": i.get("fullTimeEmployees"),
        "fifty_two_low": i.get("fiftyTwoWeekLow"),
        "fifty_two_high": hi,
        "target": target,
    }


# metric -> (pillar, higher_is_better)
SCORED = {
    "ev_ebitda": ("valuation", False),
    "pe_fwd": ("valuation", False),
    "op_margin": ("profitability", True),
    "net_margin": ("profitability", True),
    "roe": ("profitability", True),
    "net_debt_ebitda": ("balance_sheet", False),
    "cash_to_rev": ("balance_sheet", True),
    "ret_1y": ("momentum", True),
    "pct_off_high": ("momentum", True),
    "upside": ("street", True),
    "short_pct": ("street", False),
}
PILLARS = ["valuation", "profitability", "balance_sheet", "momentum", "street"]


def _percentile_scores(values: dict, higher_better: bool) -> dict:
    """0-100 within the peer group. Missing/meaningless values (e.g. negative EBITDA) score 0."""
    present = {k: v for k, v in values.items() if v is not None}
    n = len(present)
    out = {k: 0.0 for k in values}
    if n == 0:
        return out
    ordered = sorted(present, key=lambda k: present[k], reverse=not higher_better)  # worst -> best
    for rank, k in enumerate(ordered):
        out[k] = 100.0 * (rank + 1) / n
    return out


def score_all(raw: dict, weights: dict) -> dict:
    comps = raw["companies"]
    metrics = {tk: derive(c) for tk, c in comps.items()}

    metric_scores = {m: _percentile_scores({tk: metrics[tk][m] for tk in metrics}, hb)
                     for m, (_, hb) in SCORED.items()}
    results = {}
    for tk in metrics:
        pillar_scores = {}
        for p in PILLARS:
            ms = [metric_scores[m][tk] for m, (pp, _) in SCORED.items() if pp == p]
            pillar_scores[p] = sum(ms) / len(ms)
        composite = sum(pillar_scores[p] * weights.get(p, 0) for p in PILLARS)
        results[tk] = {"metrics": metrics[tk], "pillars": pillar_scores, "composite": composite}

    ranked = sorted(results, key=lambda tk: results[tk]["composite"], reverse=True)
    for r, tk in enumerate(ranked, 1):
        results[tk]["rank"] = r

    # peer medians + rank for every numeric metric (rank 1 = best for scored metrics)
    medians, ranks = {}, {tk: {} for tk in results}
    for m in next(iter(metrics.values())).keys():
        vals = [metrics[tk][m] for tk in metrics if isinstance(metrics[tk][m], (int, float))]
        medians[m] = median(vals) if vals else None
        if m in SCORED:
            hb = SCORED[m][1]
            present = sorted([tk for tk in metrics if metrics[tk][m] is not None],
                             key=lambda tk: metrics[tk][m], reverse=hb)
            for r, tk in enumerate(present, 1):
                ranks[tk][m] = r
    for tk in results:
        results[tk]["metric_ranks"] = ranks[tk]

    return {"companies": results, "order": ranked, "medians": medians, "n": len(results)}
