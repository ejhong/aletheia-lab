#!/usr/bin/env python3
"""Statement check for questions/godel-argument (Python standard library only).

For each item, a model from another vendor:
  A. translates the Lean back into English blind (names anonymized, docstrings stripped, no source passage);
  B. is then shown the source passage(s) and the claim, and judges whether the Lean matches.
Planted wrong items ("decoys") are mixed in to measure whether the checker catches errors.

    python3 run.py --probe                 # one tiny call per vendor, to confirm the APIs work
    python3 run.py --vendor openai         # run all items for one vendor (resumes; skips finished items)
    python3 run.py --report                # write REPORT.md from out/
    python3 run.py --stage 2a ...          # the same commands for Stage 2A (Statement2.lean, items2a.json, out2a/)
    python3 run.py --stage 2r ...          # and for Amendment 3 (Statement3.lean, items2r.json, out2r/)
    python3 run.py --stage 2b ...          # and for Amendment 4, tier 2B (Statement4.lean, items2b.json, out2b/)

Keys come from the environment: OPENAI_API_KEY, GEMINI_API_KEY, XAI_API_KEY.
"""
import datetime
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
STATEMENT = HERE.parent / "lean" / "GodelArgument" / "Statement.lean"
OUT = HERE / "out"  # round 2; round 1 is frozen under round1/
ITEMS = HERE / "items.json"
NOTATION = HERE / "notation.md"
REPORT = HERE / "REPORT.md"
REPORT_HEAD = [
    "Round 2. Written by `run.py --report` from the raw outputs in `out/`. Verdicts are the checkers' own.",
    "Round 1 (first draft of the statements, earlier prompt) is frozen under `round1/`.",
    "S1e was compared with its source on 2026-11-23 under Amendment 1, once Penrose's text was in hand; its",
    "blind translations are those of round 2."]
# Fixed order that interleaves decoys with real items; item ids shown to the model are neutral.
ORDER = ["DEF-A", "S1a", "X2", "DEF-B", "S1b1", "X1", "S1b2", "DEF-C", "S1c", "X3", "S1a2", "S1a3", "DEF-D",
         "S1b3", "S1c2", "S1c3", "S1c4", "S1d", "S1d2", "S1e"]
PREAMBLE = ""  # a `variable` line shown above the definitions, when the statement file has one
KEEP = set()   # names shown as they are (basic syntax), although they are listed in DEFS for the context

# Model IDs and list prices (USD per million tokens, input/output) as of 2026-11-22.
VENDORS = {
    "openai": {"model": "gpt-6.2-astra", "price": (8.00, 40.00)},
    "google": {"model": "gemini-4-neon", "price": (3.00, 15.00)},
    "xai": {"model": "grok-4.7", "price": (None, None)},
}

DEFS = ["Mind", "IsTrue", "Sound", "Consistent", "IsTheoremSetOf", "IsMechanical", "Con", "KnowsOwnMachineConsistent",
        "ContainsSoundnessOf", "IsPi1", "DeductivelyClosed"]



def use_stage_2a():
    """Stage 2A (Amendment 2): a second statement file, with its own items, notation key and output folder."""
    global STATEMENT, OUT, ITEMS, NOTATION, REPORT, REPORT_HEAD, ORDER, DEFS, PREAMBLE
    # Until it is locked the statement file is a draft kept here, outside lean/, because the lab check
    # treats every lean/**/Statement*.lean as something that must already be locked.
    STATEMENT = HERE.parent / "lean" / "GodelArgument" / "Statement2.lean"
    if not STATEMENT.exists():
        STATEMENT = HERE / "Statement2.draft.lean"
    OUT, ITEMS, NOTATION, REPORT = HERE / "out2a", HERE / "items2a.json", HERE / "notation2a.md", HERE / "REPORT-2A.md"
    REPORT_HEAD = ["Stage 2A (Amendment 2), final. Written by `run.py --stage 2a --report` from the raw outputs in",
                   "`out2a/`. Verdicts are the checkers' own. Rounds 1 and 2 are frozen under `round1-2a/` and",
                   "`round2-2a/`. S2b2 (S2b′), S2e and X7 are from round 3; every other item is from round 2 and",
                   "was not changed after it."]
    ORDER = ["DEF-E", "S2a", "X5", "DEF-F", "S2c", "DEF-G", "X6", "S2a2", "S2e", "S2b", "X4", "S2d", "X7", "S2b2"]
    DEFS = ["ClosedUnderNecessitation", "KnowledgeClosedUnderMP", "Factive", "KnowsOwnFactivity", "HasGödelSentence"]
    PREAMBLE = next(line for line in STATEMENT.read_text().splitlines() if line.startswith("variable ")) + "\n"


def use_stage_2b():
    """Amendment 4, tier 2B: a concrete logic of knowledge with quantifiers, defined in its own statement file."""
    global STATEMENT, OUT, ITEMS, NOTATION, REPORT, REPORT_HEAD, ORDER, DEFS, PREAMBLE, KEEP
    STATEMENT = HERE.parent / "lean" / "GodelArgument" / "Statement4.lean"
    if not STATEMENT.exists():
        STATEMENT = HERE / "Statement4.draft.lean"
    OUT, ITEMS, NOTATION, REPORT = HERE / "out2b", HERE / "items2b.json", HERE / "notation2b.md", HERE / "REPORT-2B.md"
    REPORT_HEAD = ["Amendment 4, tier 2B. Written by `run.py --stage 2b --report` from the raw outputs in `out2b/`.",
                   "Verdicts are the checkers' own."]
    ORDER = ["DEF-L1", "S3b", "X11", "DEF-L2", "S3a", "X12", "S3c", "DEF-L3", "X10", "S3d", "S3e", "S3f"]
    DEFS = ["Form", "neg", "and", "iff", "ex", "Free", "subst", "FreeFor", "PropVal", "Tautology", "BaseAx", "Sig",
            "Axiom", "Proves", "U", "diagAll", "diagQ"]
    KEEP = {"Form", "neg", "and", "iff", "ex"}
    PREAMBLE = ""


def use_stage_2r():
    """Amendment 3: statements added after reading Reinhardt (1985), plus two locked Stage 2A statements compared
    again with his text. Definitions come from Statement2.lean and the new file together."""
    global STATEMENT, OUT, ITEMS, NOTATION, REPORT, REPORT_HEAD, ORDER, DEFS, PREAMBLE
    s2 = HERE.parent / "lean" / "GodelArgument" / "Statement2.lean"
    s3 = HERE.parent / "lean" / "GodelArgument" / "Statement3.lean"
    if not s3.exists():
        s3 = HERE / "Statement3.draft.lean"
    STATEMENT = [s2, s3]
    OUT, ITEMS, NOTATION, REPORT = HERE / "out2r", HERE / "items2r.json", HERE / "notation2a.md", HERE / "REPORT-2R.md"
    REPORT_HEAD = ["Amendment 3. Written by `run.py --stage 2r --report` from the raw outputs in `out2r/`. Verdicts",
                   "are the checkers' own. S2aR and S2dR are the locked Stage 2A statements `ReinhardtTheorem3` and",
                   "`NoKnownSelfDiagonal`, translated blind again and compared with Reinhardt's own text."]
    ORDER = ["DEF-H", "S2f", "X9", "S2aR", "S2g", "X8", "S2dR"]
    DEFS = ["ClosedUnderNecessitation", "KnowledgeClosedUnderMP", "Factive", "KnowsOwnFactivity", "HasGödelSentence",
            "KnowledgeSelfReflective"]
    PREAMBLE = next(line for line in s2.read_text().splitlines() if line.startswith("variable ")) + "\n"


PROMPT_A = """You are checking a formalization in Lean 4. Below are a notation key, some definitions, and one TARGET. \
Names have been replaced by neutral labels (Def1, Def2, ..., Target) and comments removed, so judge only what the \
formal text says.

Translate the TARGET into plain, precise English: say exactly what it defines or asserts, including every \
hypothesis, the order of quantifiers, and what is and is not required. Do not guess what the author intended; \
describe what is written. If something is unusual or looks like a slip, describe it as it is written.

Reply with JSON only: {{"translation": "<your English rendering of the TARGET>"}}

# Notation key
{notation}

# Definitions (context)
```lean
{context}
```

# TARGET
```lean
{target}
```
"""

PROMPT_B = """You are checking whether a Lean 4 formalization says what a source text says. Earlier, without seeing \
the source, you translated the TARGET below into English; that translation is included.

The author's claim about the TARGET: {claim}

The TARGET is a definition, or a statement that will be proved separately. Do not count the absence of a proof, \
of philosophical commentary, or of parts of the passage that the claim does not mention, as a divergence; other \
parts are covered by other items.

Judge whether the TARGET, as formally written, matches the source passage(s) for that claim. List every divergence: \
anything the Lean adds, omits, strengthens, weakens, reverses, or gets wrong relative to the passage, and anything \
in the passage the Lean cannot express. Rate each divergence "major" (the Lean says something materially different, \
or would mislead a reader about what was established) or "minor" (an idealization, a harmless strengthening or \
weakening, or a presentational choice). Be strict: a formal statement that is the converse of the claim, drops a \
clause, or swaps "equal" for "included in" is a major divergence even if it looks similar.

Reply with JSON only:
{{"verdict": "faithful" | "faithful_with_caveats" | "divergent",
  "divergences": [{{"severity": "major" | "minor", "description": "..."}}],
  "summary": "<one or two sentences>"}}
Use "divergent" if there is any major divergence.

# Notation key
{notation}

# Definitions (context)
```lean
{context}
```

# TARGET
```lean
{target}
```

# Your earlier blind translation of the TARGET
{translation}

# Source passage(s)
{passages}
"""


def strip_comments(code):
    code = re.sub(r"/-[-!].*?-/\n?", "", code, flags=re.S)
    return "\n".join(line for line in code.splitlines() if line.strip()) + "\n"


def lean_blocks():
    """Map each declared name in Statement.lean to its declaration text (docstring removed)."""
    files = STATEMENT if isinstance(STATEMENT, list) else [STATEMENT]
    body = ""
    for f in files:
        text = f.read_text()
        body += text[text.index("namespace GodelArgument"):text.index("end GodelArgument")] + "\n"
    blocks = {}
    for chunk in re.split(r"\n(?=/--)", body):
        code = strip_comments(chunk)
        code = "\n".join(line for line in code.splitlines() if line.strip() not in ("end", "section") and not line.startswith(("open ", "namespace ", "variable ", "end "))) + "\n"
        m = re.search(r"^(?:noncomputable )?(?:def|abbrev|inductive) (\w+)", code, flags=re.M)
        if m:
            blocks[m.group(1)] = code[m.start():]
    return blocks


def anonymize(code, target_names):
    for i, name in enumerate(DEFS, 1):
        if name in KEEP:
            continue
        label = "Target" if name in target_names and len(target_names) == 1 else f"Def{i}"
        code = re.sub(rf"(?<![\w.]){name}\b", label, code)
    for name in target_names:
        if name not in DEFS:
            code = re.sub(rf"(?<![\w.]){name}\b", "Target", code)
    return code


def build_items():
    spec = json.loads(ITEMS.read_text())
    blocks = lean_blocks()
    passages = {}
    for sec in re.split(r"\n## ", (HERE / "passages.md").read_text())[1:]:
        pid = sec.split(" ")[0]
        if pid.startswith("P-"):
            head = sec.splitlines()[0]
            quote = " ".join(line[2:] for line in sec.splitlines() if line.startswith("> "))
            passages[pid] = f"[{head}]\n{quote}"
    items = []
    for it in spec["real"]:
        names = it["names"]
        target = "\n".join(blocks[n] for n in names)
        context = PREAMBLE + "\n".join(blocks[n] for n in DEFS if n not in names)
        items.append({**it, "decoy": False, "target": anonymize(target, names), "context": anonymize(context, names)})
    for it in spec["decoys"]:
        code = strip_comments(it["lean"])
        names = re.findall(r"^(?:noncomputable )?(?:def|abbrev|inductive) (\w+)", code, flags=re.M)
        context = PREAMBLE + "\n".join(blocks[n] for n in DEFS if n not in names)
        items.append({**it, "names": names, "decoy": True, "target": anonymize(code, names),
                      "context": anonymize(context, names)})
    for it in items:
        it["passage_text"] = "\n\n".join(passages[p] for p in it["passages"])
    return [next(i for i in items if i["id"] == k) for k in ORDER]


def post(url, headers, body, timeout=900):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:600]
            if e.code in (429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(str(e)) from None


def call(vendor, prompt):
    """Return (text, input_tokens, output_tokens, raw)."""
    model = VENDORS[vendor]["model"]
    if vendor in ("openai", "xai"):
        base = "https://api.openai.com/v1" if vendor == "openai" else "https://api.x.ai/v1"
        key = os.environ["OPENAI_API_KEY" if vendor == "openai" else "XAI_API_KEY"]
        body = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        if vendor == "openai":
            body["reasoning_effort"] = "high"
        raw = post(f"{base}/chat/completions", {"Authorization": f"Bearer {key}"}, body)
        u = raw.get("usage", {})
        return raw["choices"][0]["message"]["content"], u.get("prompt_tokens", 0), u.get("completion_tokens", 0), raw
    if vendor == "google":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        raw = post(url, {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, body)
        text = "".join(p.get("text", "") for p in raw["candidates"][0]["content"]["parts"] if not p.get("thought"))
        u = raw.get("usageMetadata", {})
        out = u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)
        return text, u.get("promptTokenCount", 0), out, raw
    raise ValueError(vendor)


def parse_json(text):
    m = re.search(r"\{.*\}", text, flags=re.S)
    return json.loads(m.group(0)) if m else None


def run(vendor):
    notation = NOTATION.read_text()
    outdir = OUT / vendor
    outdir.mkdir(parents=True, exist_ok=True)
    items = build_items()

    def one(n_it):
        n, it = n_it
        path = outdir / f"{it['id']}.json"
        if path.exists():
            # Amendment 1: an item that had no passage when it was translated blind, and has one now, gets
            # the comparison step only. The blind translation on file is reused unchanged.
            rec = json.loads(path.read_text())
            if it["passages"] and "judgement" not in rec:
                text, tin, tout, raw = call(vendor, PROMPT_B.format(
                    notation=notation, context=it["context"], target=it["target"], claim=it["claim"],
                    translation=rec["translation"], passages=it["passage_text"]))
                rec["usage"].append([tin, tout])
                rec["b_raw"] = text
                rec["judgement"] = parse_json(text)
                rec["judgement_time"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
                print(f"[{vendor}] {n:2d}/{len(items)} {it['id']:6s} (comparison only) "
                      f"{(rec['judgement'] or {}).get('verdict')}", flush=True)
            return
        rec = {"id": it["id"], "decoy": it["decoy"], "vendor": vendor, "model": VENDORS[vendor]["model"],
               "time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "target": it["target"], "usage": []}
        text, tin, tout, raw = call(vendor, PROMPT_A.format(notation=notation, context=it["context"], target=it["target"]))
        rec["usage"].append([tin, tout])
        rec["a_raw"] = text
        a = parse_json(text) or {}
        rec["translation"] = a.get("translation", text)
        if it["passages"]:
            text, tin, tout, raw = call(vendor, PROMPT_B.format(
                notation=notation, context=it["context"], target=it["target"], claim=it["claim"],
                translation=rec["translation"], passages=it["passage_text"]))
            rec["usage"].append([tin, tout])
            rec["b_raw"] = text
            rec["judgement"] = parse_json(text)
        path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        v = (rec.get("judgement") or {}).get("verdict", "translation only")
        print(f"[{vendor}] {n:2d}/{len(items)} {it['id']:6s} {'(decoy) ' if it['decoy'] else ''}{v}", flush=True)

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(one, enumerate(items, 1)))


def cost(vendor, usage):
    pin, pout = VENDORS[vendor]["price"]
    if pin is None:
        return None
    return sum(i * pin + o * pout for i, o in usage) / 1e6


def report():
    spec = json.loads(ITEMS.read_text())
    planted = {d["id"]: d for d in spec["decoys"]}
    lines = ["# Statement check report", "", *REPORT_HEAD, ""]
    vendors = [v for v in VENDORS if (OUT / v).is_dir()]
    recs = {v: {p.stem: json.loads(p.read_text()) for p in sorted((OUT / v).glob("*.json"))} for v in vendors}
    lines += ["## Models", ""]
    for v in vendors:
        usage = [u for r in recs[v].values() for u in r["usage"]]
        c = cost(v, usage)
        times = sorted(r["time"] for r in recs[v].values())
        lines.append(f"- {v}: `{VENDORS[v]['model']}`, {len(recs[v])} items, run {times[0]} to {times[-1]}, "
                     f"{sum(i for i, _ in usage):,} input and {sum(o for _, o in usage):,} output tokens"
                     + (f", about ${c:.2f} at list price" if c is not None else ""))
    lines += ["", "## Planted errors", "", "| Item | Planted error | " + " | ".join(vendors) + " |",
              "|---|---|" + "---|" * len(vendors)]
    for k, d in planted.items():
        row = [k, d["planted_error"]]
        for v in vendors:
            j = (recs[v].get(k) or {}).get("judgement") or {}
            row.append(j.get("verdict", "missing"))
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "A planted error counts as caught when the verdict is `divergent`.", "",
              "## Real items", "", "| Item | Lean names | " + " | ".join(vendors) + " |", "|---|---|" + "---|" * len(vendors)]
    for it in spec["real"]:
        row = [it["id"], ", ".join(f"`{n}`" for n in it["names"])]
        for v in vendors:
            r = recs[v].get(it["id"]) or {}
            j = r.get("judgement") or {}
            majors = sum(1 for d in j.get("divergences", []) if d.get("severity") == "major")
            minors = sum(1 for d in j.get("divergences", []) if d.get("severity") == "minor")
            row.append(f"{j['verdict']} ({majors} major, {minors} minor)" if j else ("translation only" if r else "missing"))
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Divergences listed for real items", ""]
    for it in spec["real"]:
        lines += [f"### {it['id']}: " + ", ".join(f"`{n}`" for n in it["names"]), ""]
        for v in vendors:
            r = recs[v].get(it["id"])
            if not r:
                continue
            lines += [f"**{v} ({VENDORS[v]['model']})**", "", f"Blind translation: {r['translation']}", ""]
            j = r.get("judgement")
            if j:
                lines.append(f"Verdict: {j.get('verdict')}. {j.get('summary', '')}")
                lines += [f"- {d.get('severity')}: {d.get('description')}" for d in j.get("divergences", [])]
                lines.append("")
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:2] == ["--stage", "2a"]:
        use_stage_2a()
        args = args[2:]
    elif args[:2] == ["--stage", "2r"]:
        use_stage_2r()
        args = args[2:]
    elif args[:2] == ["--stage", "2b"]:
        use_stage_2b()
        args = args[2:]
    if args == ["--probe"]:
        for v in ("openai", "google", "xai"):
            try:
                text, tin, tout, _ = call(v, 'Reply with JSON only: {"ok": true}')
                print(v, VENDORS[v]["model"], repr(text[:60]), tin, tout)
            except Exception as e:  # report and carry on to the next vendor
                print(v, "FAILED:", str(e)[:400])
    elif len(args) == 2 and args[0] == "--vendor" and args[1] in VENDORS:
        run(args[1])
    elif args == ["--report"]:
        report()
    elif args == ["--show"]:
        for it in build_items():
            print("=" * 20, it["id"], "decoy" if it["decoy"] else "")
            print("--- context\n" + it["context"] + "--- target\n" + it["target"])
    else:
        sys.exit(__doc__)
