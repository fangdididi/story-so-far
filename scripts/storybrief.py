#!/usr/bin/env python3
"""storybrief.py - helper for the story-so-far skill.

Commands
  new    <dir> "<one-line story>"     scaffold a story.json
  lint   <story.json>                  check the claim ledger and timeline rules
  render <story.json> [--lang en|zh]   print the catch-up brief as Markdown
  diff   <old.json> <new.json>         show what moved since the last brief

Standard library only. Exit code 0 = clean, 1 = lint errors, 2 = usage error.
"""
import json, sys, os, re, datetime

STATUSES = ["CONFIRMED", "REPORTED", "CLAIMED", "RUMOR", "DISPUTED", "CORRECTED", "RETRACTED", "SUPERSEDED"]
LAYERS = ["primary", "reporting", "community", "market"]
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2}))?$")

LABELS = {
    "en": {"title": "Story so far", "asof": "As of", "headline": "Where it stands",
           "solid": "What is solid", "loose": "What is still loose", "dead": "Walked back or overtaken",
           "timeline": "Timeline", "sides": "The sides, in their own words", "heat": "What people are loudest about",
           "watch": "What to watch", "change": "What would change the picture", "sources": "Sources",
           "none": "(none)", "event": "event", "reported": "reported"},
    "zh": {"title": "事件进展", "asof": "截至", "headline": "现在的局面",
           "solid": "站得住的", "loose": "仍未落地的", "dead": "已撤回或被推翻的",
           "timeline": "时间线", "sides": "各方说法（原话转述）", "heat": "大家最关注什么",
           "watch": "接下来盯什么", "change": "什么会改变判断", "sources": "来源",
           "none": "（无）", "event": "发生", "reported": "报道"},
}


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cmd_new(d, line):
    os.makedirs(d, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    story = {
        "card": {"story": line, "as_of": now, "window_from": "", "user_knows": "",
                 "why": "decide|act|talk|curious", "depth": "60s|5min", "out_of_scope": []},
        "origin": {"id": "", "what": "", "event_time": "", "url": ""},
        "sources": [],
        "claims": [],
        "beats": [],
        "sides": [],
        "heat": [],
        "watch": [],
        "would_change": [],
        "headline": "",
    }
    p = os.path.join(d, "story.json")
    if os.path.exists(p):
        print("refusing to overwrite", p); return 2
    with open(p, "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=2)
    print("created", p); return 0


def lint(s):
    errs, warns = [], []
    card = s.get("card", {})
    if not card.get("story"): errs.append("C01 card.story is empty")
    if not ISO.match(card.get("as_of", "") or ""): errs.append("C02 card.as_of must be an ISO date/time")
    src = {x.get("id"): x for x in s.get("sources", [])}
    for sid, x in src.items():
        if x.get("layer") not in LAYERS: errs.append(f"S01 source {sid}: layer must be one of {LAYERS}")
        if not x.get("url") and not x.get("where"): errs.append(f"S02 source {sid}: needs url or where")
        if x.get("published") and not ISO.match(x["published"]): errs.append(f"S03 source {sid}: published not ISO")
        if x.get("echo_of") and x["echo_of"] not in src: errs.append(f"S04 source {sid}: echo_of points to unknown source {x['echo_of']}")
        if x.get("self_interested") is None and x.get("layer") == "primary":
            warns.append(f"S05 source {sid}: say whether this primary source is a party to the story (self_interested)")

    def root(sid, seen=None):
        seen = seen or set()
        x = src.get(sid)
        if not x or not x.get("echo_of") or sid in seen: return sid
        seen.add(sid); return root(x["echo_of"], seen)

    ids = set()
    for c in s.get("claims", []):
        cid = c.get("id", "?")
        if cid in ids: errs.append(f"L00 claim {cid}: duplicate id")
        ids.add(cid)
        st = c.get("status")
        if st not in STATUSES: errs.append(f"L01 claim {cid}: status must be one of {STATUSES}"); continue
        cs = c.get("sources", [])
        for sid in cs:
            if sid not in src: errs.append(f"L02 claim {cid}: unknown source {sid}")
        roots = {root(x) for x in cs if x in src}
        layers = {src[r].get("layer") for r in roots}
        neutral_primary = any(src[r].get("layer") == "primary" and src[r].get("self_interested") is False for r in roots)
        independent_reporting = [r for r in roots if src[r].get("layer") == "reporting" and src[r].get("own_access")]
        if st == "CONFIRMED" and not (neutral_primary or len(independent_reporting) >= 2):
            errs.append(f"L03 claim {cid}: CONFIRMED needs a non-party primary record or two independent reports with their own access (found {len(roots)} independent root(s) after collapsing echoes)")
        if st == "REPORTED" and not any(src[r].get("layer") == "reporting" for r in roots):
            errs.append(f"L04 claim {cid}: REPORTED needs at least one reporting-layer source")
        if st == "CLAIMED" and not c.get("by"):
            errs.append(f"L05 claim {cid}: CLAIMED must name who is claiming it (by)")
        if st == "DISPUTED" and not c.get("against"):
            errs.append(f"L06 claim {cid}: DISPUTED must cite the contradicting source(s) in against")
        if st in ("CORRECTED", "RETRACTED") and not c.get("correction"):
            errs.append(f"L07 claim {cid}: {st} must link the correction/retraction itself")
        if st == "SUPERSEDED" and not c.get("superseded_by"):
            errs.append(f"L08 claim {cid}: SUPERSEDED must point to the claim that replaced it")
        if st != "RUMOR" and not cs:
            errs.append(f"L09 claim {cid}: only RUMOR may have no sources")
        if layers == {"market"} and st in ("CONFIRMED", "REPORTED"):
            errs.append(f"L10 claim {cid}: market prices are sentiment, never evidence of fact")
        if len(cs) >= 3 and len(roots) == 1:
            warns.append(f"W01 claim {cid}: {len(cs)} sources but one root - one source, many mouths")
        if any(w in (c.get("text", "").lower()) for w in ("reportedly", "allegedly", "sources say", "据悉", "据传")) and st == "CONFIRMED":
            warns.append(f"W02 claim {cid}: hedge words inside a CONFIRMED claim - rewrite it as the plain fact or downgrade it")
    for b in s.get("beats", []):
        if not ISO.match(b.get("event_time", "") or ""): errs.append(f"T01 beat '{b.get('what','')[:40]}': event_time must be ISO")
        for cid in b.get("claims", []):
            if cid not in ids: errs.append(f"T02 beat '{b.get('what','')[:40]}': unknown claim {cid}")
    times = [b.get("event_time") for b in s.get("beats", []) if b.get("event_time")]
    if times != sorted(times): warns.append("W03 beats are not in event-time order")
    for h in s.get("heat", []):
        if h.get("engagement") and not h.get("fetched_at"):
            errs.append(f"H01 heat '{h.get('topic','')[:40]}': engagement numbers need fetched_at")
    if not s.get("watch"): warns.append("W04 nothing in the watch list - is the story really over?")
    if not s.get("headline"): errs.append("C03 headline is empty - write the one sentence a reader keeps")
    return errs, warns


def cmd_lint(p):
    errs, warns = lint(load(p))
    for e in errs: print("ERROR", e)
    for w in warns: print("WARN ", w)
    print(f"{len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


def cmd_render(p, lang="en"):
    s = load(p); L = LABELS[lang]
    src = {x["id"]: x for x in s.get("sources", [])}
    out = [f"# {L['title']}: {s['card']['story']}", "", f"_{L['asof']} {s['card']['as_of']}_", "",
           f"**{L['headline']}:** {s.get('headline','')}", ""]
    def claims(st_set):
        rows = [c for c in s.get("claims", []) if c.get("status") in st_set]
        if not rows: return [f"- {L['none']}"]
        return [f"- [{c['status']}] {c['text']}" + (f" ({c['by']})" if c.get("by") else "") +
                (" " + " ".join(f"[{x}]" for x in c.get("sources", [])) if c.get("sources") else "") for c in rows]
    out += [f"## {L['solid']}"] + claims({"CONFIRMED"}) + [""]
    out += [f"## {L['loose']}"] + claims({"REPORTED", "CLAIMED", "RUMOR", "DISPUTED"}) + [""]
    out += [f"## {L['dead']}"] + claims({"CORRECTED", "RETRACTED", "SUPERSEDED"}) + [""]
    out += [f"## {L['timeline']}"]
    for b in s.get("beats", []):
        rep = f" / {L['reported']} {b['report_time']}" if b.get("report_time") else ""
        turn = " **<- turn**" if b.get("turn") else ""
        out.append(f"- {b['event_time']} ({L['event']}{rep}): {b['what']}{turn}")
    out += ["", f"## {L['sides']}"] + ([f"- **{x['who']}**: {x['position']}" for x in s.get("sides", [])] or [f"- {L['none']}"])
    out += ["", f"## {L['heat']}"] + ([f"- {h['topic']}" + (f" ({h['engagement']}, {h['fetched_at']})" if h.get("engagement") else "") for h in s.get("heat", [])] or [f"- {L['none']}"])
    out += ["", f"## {L['watch']}"] + ([f"- {w['when']}: {w['what']}" for w in s.get("watch", [])] or [f"- {L['none']}"])
    out += ["", f"## {L['change']}"] + ([f"- {x}" for x in s.get("would_change", [])] or [f"- {L['none']}"])
    out += ["", f"## {L['sources']}"]
    for sid, x in src.items():
        echo = f" (echo of {x['echo_of']})" if x.get("echo_of") else ""
        out.append(f"- [{sid}] {x.get('layer')}: {x.get('who','')} {x.get('published','')} {x.get('url') or x.get('where','')}{echo}")
    print("\n".join(out)); return 0


def cmd_diff(a, b):
    A, B = load(a), load(b)
    ca = {c["id"]: c for c in A.get("claims", [])}
    cb = {c["id"]: c for c in B.get("claims", [])}
    print(f"since {A['card'].get('as_of')} -> {B['card'].get('as_of')}")
    for cid, c in cb.items():
        if cid not in ca: print(f"NEW      {cid} [{c['status']}] {c['text']}")
        elif ca[cid]["status"] != c["status"]: print(f"MOVED    {cid} {ca[cid]['status']} -> {c['status']}: {c['text']}")
    for cid in ca:
        if cid not in cb: print(f"DROPPED  {cid} (say why in the brief)")
    old_beats = {(x.get("event_time"), x.get("what")) for x in A.get("beats", [])}
    for x in B.get("beats", []):
        if (x.get("event_time"), x.get("what")) not in old_beats: print(f"BEAT     {x['event_time']}: {x['what']}")
    if A.get("headline") != B.get("headline"): print(f"HEADLINE {B.get('headline')}")
    return 0


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    c = argv[1]
    try:
        if c == "new" and len(argv) == 4: return cmd_new(argv[2], argv[3])
        if c == "lint" and len(argv) == 3: return cmd_lint(argv[2])
        if c == "render" and len(argv) in (3, 5):
            lang = argv[4] if len(argv) == 5 and argv[3] == "--lang" else "en"
            if lang not in LABELS: print("lang must be en or zh"); return 2
            return cmd_render(argv[2], lang)
        if c == "diff" and len(argv) == 4: return cmd_diff(argv[2], argv[3])
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print("error:", e); return 2
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
