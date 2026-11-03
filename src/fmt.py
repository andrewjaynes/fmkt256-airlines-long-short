"""Number formatting + the list of metrics shown on every one-pager."""


def money(v):
    if v is None:
        return "n/a"
    a = abs(v)
    s = "-" if v < 0 else ""
    if a >= 1e9:
        return f"{s}${a / 1e9:,.1f}B"
    if a >= 1e6:
        return f"{s}${a / 1e6:,.0f}M"
    return f"{s}${a:,.2f}"


def pct(v, d=1):
    return "n/a" if v is None else f"{v * 100:+.{d}f}%".replace("+-", "-")


def pct_plain(v, d=1):
    return "n/a" if v is None else f"{v * 100:.{d}f}%"


def pct_nm(v, d=1):
    """For ratios that don't exist when the base is negative (e.g. ROE with negative equity)."""
    return "n/m" if v is None else f"{v * 100:.{d}f}%"


def mult(v, d=1):
    return "n/m" if v is None else f"{v:.{d}f}x"


def num(v, d=2):
    return "n/a" if v is None else f"{v:,.{d}f}"


def price(v):
    return "n/a" if v is None else f"${v:,.2f}"


# (key, label, formatter, group)  - order = order on the one-pager
METRIC_ROWS = [
    ("market_cap", "Market cap", money, "Size & valuation"),
    ("enterprise_value", "Enterprise value", money, "Size & valuation"),
    ("ev_ebitda", "EV / EBITDA (TTM)", mult, "Size & valuation"),
    ("pe_fwd", "P/E (forward)", mult, "Size & valuation"),
    ("pe_ttm", "P/E (trailing)", mult, "Size & valuation"),
    ("p_b", "Price / book", mult, "Size & valuation"),
    ("revenue_ttm", "Revenue (TTM)", money, "Growth & profitability"),
    ("rev_growth", "Revenue growth (latest qtr YoY)", pct, "Growth & profitability"),
    ("op_margin", "Operating margin (TTM)", pct_plain, "Growth & profitability"),
    ("net_margin", "Net margin (TTM)", pct_plain, "Growth & profitability"),
    ("roe", "Return on equity", pct_nm, "Growth & profitability"),
    ("total_debt", "Total debt", money, "Balance sheet"),
    ("total_cash", "Cash & investments", money, "Balance sheet"),
    ("net_debt_ebitda", "Net debt / EBITDA", mult, "Balance sheet"),
    ("cash_to_rev", "Cash / revenue", pct_plain, "Balance sheet"),
    ("fcf", "Free cash flow (TTM)", money, "Balance sheet"),
    ("ret_1y", "1-year total return", pct, "Market & street"),
    ("pct_off_high", "vs. 52-week high", pct, "Market & street"),
    ("upside", "Upside to mean target", pct, "Market & street"),
    ("short_pct", "Short interest (% float)", pct_plain, "Market & street"),
    ("beta", "Beta", num, "Market & street"),
]

PILLAR_LABELS = {
    "valuation": "Valuation",
    "profitability": "Profitability",
    "balance_sheet": "Balance sheet",
    "momentum": "Momentum",
    "street": "Street view",
}
