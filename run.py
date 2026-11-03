"""ONE command builds the whole report:

    python run.py                          # default: sectors/airlines.yaml
    python run.py sectors/railroads.yaml   # any other sector file
    python run.py --refresh-ai             # force fresh AI write-ups (API mode)

Edit the sector file (tickers, weights, context), never this code.
"""
import argparse
import warnings
from pathlib import Path

import yaml

warnings.filterwarnings("ignore")

from src.ai import run_ai  # noqa: E402
from src.fetch import fetch_all  # noqa: E402
from src.render import build  # noqa: E402
from src.score import score_all  # noqa: E402

ROOT = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description="Sector one-pagers + AI long/short report")
    ap.add_argument("config", nargs="?", default="sectors/airlines.yaml")
    ap.add_argument("--refresh-ai", action="store_true", help="re-write all AI analysis (needs API key)")
    args = ap.parse_args()

    cfg_path = (ROOT / args.config).resolve()
    cfg = yaml.safe_load(cfg_path.read_text())
    slug = cfg["slug"]
    print(f"\n== {cfg['sector']}: {len(cfg['tickers'])} companies ==")

    print("[1/4] Pulling live market data and financials")
    raw = fetch_all(cfg["tickers"], ROOT / "data" / slug)

    print("[2/4] Computing metrics, peer ranks and composite scores")
    scored = score_all(raw, cfg["weights"])
    for tk in scored["order"]:
        print(f"      #{scored['companies'][tk]['rank']}  {tk:<6} {scored['companies'][tk]['composite']:5.1f}")

    print("[3/4] AI analysis")
    ai = run_ai(cfg, raw, scored, ROOT / "analysis" / slug, ROOT / "output" / slug / "prompts_to_paste",
                refresh=args.refresh_ai)
    if ai["pending"]:
        print(f"      {len(ai['pending'])} AI write-up(s) still needed: {', '.join(ai['pending'])}")
        print(f"      -> paste each file in output/{slug}/prompts_to_paste/ into Claude.ai or ChatGPT,")
        print(f"         save the JSON reply as analysis/{slug}/<TICKER>.json (or long_short.json), re-run.")

    print("[4/4] Rendering report")
    pdf = build(cfg, raw, scored, ai, ROOT / "output" / slug, cfg_path)
    print(f"\nDone -> {pdf.relative_to(ROOT)}\n")


if __name__ == "__main__":
    main()
