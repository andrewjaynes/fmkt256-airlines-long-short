"""Step 3: AI write-ups (one per company) and the long/short decision.

Three ways the AI text can be produced - no code changes needed for any of them:
  1. Claude API (ANTHROPIC_API_KEY set): fully automatic, with live web search.
  2. Saved write-ups in analysis/<slug>/*.json are reused until they are stale.
  3. Manual: a ready-to-paste prompt is written for each missing write-up.
     Paste it into Claude.ai or ChatGPT, save the JSON reply as
     analysis/<slug>/<TICKER>.json, and re-run.
"""
import json
import os
import re
from datetime import date, datetime
from pathlib import Path

from .fmt import METRIC_ROWS, PILLAR_LABELS

ROOT = Path(__file__).resolve().parent.parent


def _fill(template: str, **kw) -> str:
    return template.format(**kw)


def metrics_block(tk, scored):
    c = scored["companies"][tk]
    lines = []
    for key, label, f, _ in METRIC_ROWS:
        v = c["metrics"].get(key)
        med = scored["medians"].get(key)
        rank = c["metric_ranks"].get(key)
        r = f" (rank {rank}/{scored['n']})" if rank else ""
        lines.append(f"- {label}: {f(v)} [{f(med)}]{r}")
    lines.append(f"- Composite score: {c['composite']:.0f}/100 (rank {c['rank']}/{scored['n']})")
    lines.append("- Pillars: " + ", ".join(f"{PILLAR_LABELS[p]} {s:.0f}" for p, s in c["pillars"].items()))
    return "\n".join(lines)


def peer_table(scored, names):
    rows = ["Rank | Ticker | Name | Composite | EV/EBITDA | Fwd P/E | Op margin | Net debt/EBITDA | 1y return | Short int."]
    for tk in scored["order"]:
        c = scored["companies"][tk]
        m = c["metrics"]
        from .fmt import mult, pct, pct_plain
        rows.append(f"{c['rank']} | {tk} | {names[tk]} | {c['composite']:.0f} | {mult(m['ev_ebitda'])} | "
                    f"{mult(m['pe_fwd'])} | {pct_plain(m['op_margin'])} | {mult(m['net_debt_ebitda'])} | "
                    f"{pct(m['ret_1y'])} | {pct_plain(m['short_pct'])}")
    return "\n".join(rows)


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in model reply")
    return json.loads(m.group(0))


def _call_claude(prompt: str, model: str) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    with client.beta.messages.stream(
        model=model,
        max_tokens=16000,
        output_config={"effort": "high"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 6}],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError("model declined the request")
    text = "".join(b.text for b in msg.content if b.type == "text")
    return _extract_json(text)


def _stale(path: Path, max_days: int) -> bool:
    try:
        d = json.loads(path.read_text()).get("_as_of")
        return (date.today() - date.fromisoformat(d)).days > max_days
    except Exception:
        return True


def _mode(cfg):
    mode = cfg.get("ai", {}).get("mode", "auto")
    if mode == "auto":
        return "api" if os.environ.get("ANTHROPIC_API_KEY") else "manual"
    return mode


def run_ai(cfg, raw, scored, analysis_dir: Path, prompt_dir: Path, refresh=False):
    analysis_dir.mkdir(parents=True, exist_ok=True)
    mode = _mode(cfg)
    ai_cfg = cfg.get("ai", {})
    model = ai_cfg.get("model", "claude-opus-5-5")
    max_days = ai_cfg.get("refresh_after_days", 30)
    today = date.today().isoformat()
    names = {tk: (raw["companies"][tk]["info"].get("longName") or tk) for tk in scored["order"]}
    one_tpl = (ROOT / "prompts" / "one_pager.md").read_text()
    ls_tpl = (ROOT / "prompts" / "long_short.md").read_text()
    ranking = "\n".join(f"{scored['companies'][t]['rank']}. {t} ({scored['companies'][t]['composite']:.0f})"
                        for t in scored["order"])
    pending = []

    # ---- one write-up per company --------------------------------------
    writeups = {}
    for tk in scored["order"]:
        path = analysis_dir / f"{tk}.json"
        need = refresh or not path.exists() or (mode == "api" and _stale(path, max_days))
        prompt = _fill(one_tpl, sector=cfg["sector"], today=today, name=names[tk], ticker=tk,
                       sector_context=cfg.get("sector_context", ""), n=scored["n"],
                       metrics_block=metrics_block(tk, scored), peer_ranking=ranking)
        if need and mode == "api":
            print(f"  Claude is writing the {tk} one-pager ...", flush=True)
            data = _call_claude(prompt, model)
            data["_as_of"], data["_generated_by"] = today, f"{model} via Claude API + web search"
            path.write_text(json.dumps(data, indent=2))
        elif need and not path.exists():
            prompt_dir.mkdir(parents=True, exist_ok=True)
            (prompt_dir / f"{tk}.md").write_text(prompt)
            pending.append(tk)
        if path.exists():
            writeups[tk] = json.loads(path.read_text())

    # ---- long / short decision -----------------------------------------
    ls_path = analysis_dir / "long_short.json"
    wu_text = "\n\n".join(
        f"## {tk} - {w.get('model_type', '')}\nHeadline: {w.get('headline')}\nRecent: {w.get('recent')}\n"
        f"Strengths: {w.get('strengths')}\nRisks: {w.get('risks')}\nStance: {w.get('stance')}"
        for tk, w in writeups.items())
    ls_prompt = _fill(ls_tpl, sector=cfg["sector"], today=today, n=scored["n"],
                      sector_context=cfg.get("sector_context", ""),
                      peer_table=peer_table(scored, names), writeups=wu_text)
    tickers_now = set(scored["order"])
    # a saved decision is only valid for the same set of companies
    ls_ok = ls_path.exists() and set(json.loads(ls_path.read_text()).get("_universe", tickers_now)) == tickers_now
    if mode == "api" and (refresh or not ls_ok or _stale(ls_path, max_days)) and not pending:
        print("  Claude is choosing the long and the short ...", flush=True)
        data = _call_claude(ls_prompt, model)
        data["_as_of"], data["_generated_by"] = today, f"{model} via Claude API"
        data["_universe"] = sorted(tickers_now)
        ls_path.write_text(json.dumps(data, indent=2))
    elif not ls_ok:
        prompt_dir.mkdir(parents=True, exist_ok=True)
        (prompt_dir / "LONG_SHORT.md").write_text(ls_prompt)
        pending.append("LONG_SHORT")
    long_short = None
    if ls_path.exists():
        saved = json.loads(ls_path.read_text())
        if set(saved.get("_universe", tickers_now)) == tickers_now:
            long_short = saved

    return {"writeups": writeups, "long_short": long_short, "pending": pending, "mode": mode}
