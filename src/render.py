"""Step 4: build charts + HTML, then print to PDF with headless Chrome."""
import io
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from statistics import median

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402

from . import fmt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NAVY, TEAL, GREY, GREEN, RED = "#0b2545", "#13807a", "#9aa5b1", "#1a7f4b", "#b3261e"

plt.rcParams.update({
    "font.family": "Helvetica", "font.size": 7.5, "axes.edgecolor": "#c8ced6",
    "axes.labelcolor": "#334", "xtick.color": "#556", "ytick.color": "#556",
    "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none",
})


def _svg(fig) -> str:
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)
    s = buf.getvalue()
    return s[s.index("<svg"):]


def price_chart(tk, raw):
    """1-year price indexed to 100 vs. the peer median."""
    series = {}
    for t, c in raw["companies"].items():
        p = c.get("prices", [])
        if p:
            series[t] = {d["date"]: d["close"] / p[0]["close"] * 100 for d in p}
    dates = sorted(series[tk])
    peer = [median([series[t][d] for t in series if t != tk and d in series[t]] or [100]) for d in dates]
    xs = [datetime.fromisoformat(d) for d in dates]
    fig, ax = plt.subplots(figsize=(3.55, 1.42))
    ax.plot(xs, peer, color=GREY, lw=1.1, label="Peer median")
    ax.plot(xs, [series[tk][d] for d in dates], color=NAVY, lw=1.5, label=tk)
    ax.axhline(100, color="#dde2e8", lw=0.8, zorder=0)
    ax.set_title("1-year price, indexed to 100", loc="left", fontsize=8, color=NAVY, fontweight="bold")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b '%y"))
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
    ax.grid(axis="y", color="#eef1f4", lw=0.6)
    return _svg(fig)


def quarters_chart(tk, raw):
    """Quarterly revenue bars with operating-margin line."""
    qs = [q for q in raw["companies"][tk].get("quarters", []) if q.get("revenue")]
    fig, ax = plt.subplots(figsize=(3.55, 1.42))
    if not qs:
        ax.text(0.5, 0.5, "No quarterly data", ha="center", transform=ax.transAxes)
        return _svg(fig)
    labels = [q["label"] for q in qs]
    rev = [q["revenue"] / 1e9 for q in qs]
    ax.bar(labels, rev, color=TEAL, width=0.6)
    ax.set_ylabel("Revenue ($B)")
    ax2 = ax.twinx()
    om = [(q["operating_income"] / q["revenue"] * 100) if q.get("operating_income") is not None else None for q in qs]
    ax2.plot(labels, om, color=NAVY, marker="o", ms=3, lw=1.3)
    ax2.axhline(0, color=RED, lw=0.6, ls=":")
    ax2.set_ylabel("Op. margin (%)")
    ax2.spines["right"].set_visible(True)
    ax.set_title("Quarterly revenue (bars) & operating margin (line)", loc="left", fontsize=8,
                 color=NAVY, fontweight="bold")
    ax.tick_params(axis="x", labelsize=6.5)
    return _svg(fig)


def scatter_chart(scored):
    """EV/EBITDA vs operating margin, bubble = market cap."""
    fig, ax = plt.subplots(figsize=(3.6, 2.15))
    pts = []
    for tk in scored["order"]:
        m = scored["companies"][tk]["metrics"]
        if m["op_margin"] is None:
            continue
        x = m["ev_ebitda"] if m["ev_ebitda"] is not None and m["ev_ebitda"] < 25 else 25
        y = m["op_margin"] * 100
        ax.scatter(x, y, s=max(25, (m["market_cap"] or 0) / 1e9 * 4), color=TEAL, alpha=0.55, edgecolor=NAVY, lw=0.6)
        pts.append((tk + (" (n/m)" if x == 25 else ""), x, y))
    ax.axhline(0, color=RED, lw=0.6, ls=":")
    ax.set_xlabel("EV / EBITDA (x)  ->  more expensive   [n/m = negative/extreme, capped at 25x]")
    ax.set_ylabel("Operating margin, TTM (%)")
    ax.set_title("Cheap AND profitable = top-left", loc="left", fontsize=8, color=NAVY, fontweight="bold")
    ax.grid(color="#eef1f4", lw=0.6)
    ax.margins(x=0.08, y=0.14)

    # place each label at the candidate offset farthest from other points and labels
    fig.canvas.draw()
    to_px = ax.transData.transform
    k = fig.dpi / 72
    box = ax.get_window_extent()
    centers = [tuple(to_px((x, y))) for _, x, y in pts]
    taken = list(centers)
    for (lab, x, y), (cx, cy) in zip(pts, centers):
        w = len(lab) * 3.6
        best, best_d = (5, 4), -1
        for dx, dy in [(5, 4), (5, -11), (-w - 5, 4), (-w - 5, -11), (5, 13), (-w / 2, 12)]:
            lx, ly = cx + (dx + w / 2) * k, cy + (dy + 3) * k
            d = min([((lx - tx) ** 2 + (ly - ty) ** 2) ** 0.5 for tx, ty in taken if (tx, ty) != (cx, cy)] or [1e9])
            inside = box.x0 < lx - w / 2 * k and lx + w / 2 * k < box.x1 and box.y0 < ly < box.y1 - 4 * k
            if inside and d > 14 * k:   # first clear spot wins, so labels stay close to their dot
                best = (dx, dy)
                break
            if inside and d > best_d:
                best, best_d = (dx, dy), d
        ax.annotate(lab, (x, y), fontsize=7, xytext=best, textcoords="offset points")
        taken.append((cx + (best[0] + w / 2) * k, cy + (best[1] + 3) * k))
    return _svg(fig)


def returns_chart(scored):
    order = sorted(scored["order"], key=lambda t: scored["companies"][t]["metrics"]["ret_1y"] or 0)
    vals = [(scored["companies"][t]["metrics"]["ret_1y"] or 0) * 100 for t in order]
    fig, ax = plt.subplots(figsize=(3.6, 2.15))
    ax.barh(order, vals, color=[GREEN if v >= 0 else RED for v in vals], height=0.6)
    for i, v in enumerate(vals):
        ax.text(v + (2 if v >= 0 else -2), i, f"{v:+.0f}%", va="center", ha="left" if v >= 0 else "right", fontsize=7)
    ax.axvline(0, color="#556", lw=0.6)
    ax.set_title("1-year share price return", loc="left", fontsize=8, color=NAVY, fontweight="bold")
    lo, hi = min(vals + [0]), max(vals + [0])
    ax.set_xlim(lo - 25, hi + 25)
    ax.grid(axis="x", color="#eef1f4", lw=0.6)
    return _svg(fig)


def config_excerpt(text: str) -> str:
    """The parts of the sector file a user actually edits (drops the long comments)."""
    keep, skip = [], False
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith(("sector_context:", "ai:")):
            skip = True
            keep.append(line.split(":")[0] + ":  ...  (optional, plain English / settings)")
            continue
        if skip and (line.startswith(" ") or not line.strip()):
            continue
        skip = False
        keep.append(line)
    return "\n".join(keep).strip()


def build(cfg, raw, scored, ai, out_dir: Path, config_path: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    names = {tk: (raw["companies"][tk]["info"].get("longName") or tk) for tk in scored["order"]}
    ls = ai["long_short"] or {}
    long_tk = (ls.get("long") or {}).get("ticker")
    short_tk = (ls.get("short") or {}).get("ticker")

    companies = []
    for tk in scored["order"]:
        c = scored["companies"][tk]
        rows, last_group = [], None
        for key, label, f, group in fmt.METRIC_ROWS:
            rows.append({
                "group": group if group != last_group else None, "label": label,
                "value": f(c["metrics"].get(key)), "median": f(scored["medians"].get(key)),
                "rank": c["metric_ranks"].get(key),
            })
            last_group = group
        companies.append({
            "ticker": tk, "name": names[tk], "c": c, "m": c["metrics"], "rows": rows,
            "info": raw["companies"][tk]["info"], "w": ai["writeups"].get(tk),
            "role": "LONG" if tk == long_tk else "SHORT" if tk == short_tk else None,
            "price_svg": price_chart(tk, raw), "q_svg": quarters_chart(tk, raw),
            "latest_q": (raw["companies"][tk].get("quarters") or [{}])[-1].get("label", "n/a"),
        })

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
    env.filters.update({k: getattr(fmt, k) for k in ["money", "pct", "pct_plain", "mult", "num", "price"]})
    html = env.get_template("report.html.j2").render(
        cfg=cfg, raw=raw, scored=scored, ai=ai, ls=ls, companies=companies,
        by_tk={c["ticker"]: c for c in companies}, names=names,
        pillars=fmt.PILLAR_LABELS, generated=datetime.now().strftime("%B %d, %Y %I:%M %p"),
        fetched=raw["fetched_at"], config_text=config_excerpt(config_path.read_text()), config_name=str(config_path.name),
        scatter_svg=scatter_chart(scored), returns_svg=returns_chart(scored), other_sectors=_other_sectors(cfg["slug"]),
    )
    # small summary other sector reports can show as proof of reuse
    (out_dir / "summary.json").write_text(json.dumps({
        "sector": cfg["sector"], "config": config_path.name, "n": scored["n"], "generated": datetime.now().isoformat(timespec="minutes"),
        "ranking": [[tk, round(scored["companies"][tk]["composite"])] for tk in scored["order"]],
        "long": long_tk, "short": short_tk, "ai_pending": len(ai["pending"])}, indent=1))
    html_path = out_dir / "report.html"
    html_path.write_text(html)

    pdf_path = out_dir / f"{cfg['slug']}_report.pdf"
    chrome = _find_chrome()
    if chrome:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                       check=True, capture_output=True, timeout=180)
    else:
        print("  (Chrome/Chromium not found - open output/.../report.html and Print -> Save as PDF)")
    return pdf_path


def _other_sectors(slug):
    """Summaries of reports built for OTHER sector files with this same code."""
    out = []
    for f in sorted((ROOT / "output").glob("*/summary.json")):
        if f.parent.name != slug:
            out.append(json.loads(f.read_text()))
    return out


def _find_chrome():
    for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]:
        if Path(p).exists():
            return p
    for n in ["google-chrome", "chromium", "chromium-browser", "chrome", "msedge"]:
        if shutil.which(n):
            return shutil.which(n)
    return None
