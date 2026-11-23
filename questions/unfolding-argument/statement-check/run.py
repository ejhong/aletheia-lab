#!/usr/bin/env python3
"""Statement check for questions/unfolding-argument (Python standard library only).

For each item, a model from another vendor:
  A. translates the Lean back into English blind (names replaced by neutral labels, comments removed, no source
     passage);
  B. is then shown the source passage(s) and the claim, and judges whether the Lean matches.
Planted wrong items ("decoys") are mixed in to measure whether the checker catches errors.

    python3 run.py --probe                 # one tiny call per vendor, to confirm the APIs work
    python3 run.py --show                  # print what the checkers will be shown; no calls
    python3 run.py --vendor openai         # run all items for one vendor (resumes; skips finished items)
    python3 run.py --report                # write REPORT.md from out/

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
STATEMENT = HERE.parent / "lean" / "UnfoldingArgument" / "Statement.lean"
OUT = HERE / "out"  # the round the locked statements went through; earlier rounds are frozen under roundN/
ITEMS = HERE / "items.json"
NOTATION = HERE / "notation.md"
REPORT = HERE / "REPORT.md"
REPORT_HEAD = [l for l in (HERE / "report_head.txt").read_text().splitlines()] if (HERE / "report_head.txt").exists() else []

# Model IDs and list prices (USD per million tokens, input/output) as of 2026-11-22.
VENDORS = {
    "openai": {"model": "gpt-6.2-astra", "price": (8.00, 40.00)},
    "google": {"model": "gemini-4-neon", "price": (3.00, 15.00)},
    "xai": {"model": "grok-4.7", "price": (None, None)},
}

# Every name the lab chose is replaced by a neutral label before a checker sees the Lean, so that the blind
# translation rests on what the Lean says and not on what its names suggest. Structures: S. Structure fields: a, b,
# c. Definitions: D or d. Bound variables: single letters.
RENAME = {
    "Network": "S1", "Node": "A1", "fintypeNode": "a2", "St": "A3", "init": "a4", "step": "a5", "out": "a6",
    "State": "D1", "next": "d2", "run": "d3", "response": "d4", "AgreeUpTo": "D5", "AgreeAlways": "D6",
    "DependsOn": "D7", "Influences": "D8", "LoopFree": "D9", "Recurrent": "D10", "Integrated": "D11",
    "FeedbackFree": "D12", "size": "d13", "unfold": "d14", "latch": "d15",
    "PlasticSystem": "S2", "W": "B1", "A": "B2", "w0": "b3", "a0": "b4", "act": "b5", "learn": "b6",
    "perturbedResponse": "d16",
    "Testing": "S3", "obs": "c1", "pred": "c2", "rep": "c3", "inf": "c4", "Datasets": "D17",
    "FalsificationAt": "D18", "Produces": "D19", "predOf": "D20", "SubstitutionAt": "D21", "Arises": "D22",
    "UniversalSubstitution": "D23", "behaviourUpTo": "d24",
    "conscious": "Q", "truth": "w", "beh": "g", "extra": "h", "Sys": "X1", "Beh": "X2", "ic": "u1", "rc": "u2",
    "Obar": "V2", "intervene": "v", "I": "X", "O": "Y",
}

PROMPT_A = """You are checking a formalization in Lean 4. Below are a notation key, some definitions, and one TARGET. \
Names chosen by the author have been replaced by neutral labels (S1, A3, a5, D9, d14, ..., Target) and comments \
removed, so judge only what the formal text says.

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



PROMPT_B_OWN = """You are checking a Lean 4 formalization. Earlier, without seeing anything else, you translated \
the TARGET below into English; that translation is included.

The author says the TARGET is the author's OWN statement. It is not offered as a rendering of any passage. The \
passages below are what it bears on. The author's description of the TARGET, and of how it relates to the passages:

{claim}

Judge two things. (a) Does the TARGET, as formally written, say exactly what the author's description says it \
says? List anything the Lean adds, omits, strengthens, weakens, reverses or gets wrong relative to that \
description. (b) Is what the description says about the passages accurate? List anything it misreports about what \
the passages say or concede. Do not count it as a divergence that the passages do not themselves assert the \
TARGET, or that the TARGET is stronger or weaker than the passages in a way the description states. Rate each \
divergence "major" (the Lean says something materially different from the description, or the description \
misreports a passage, or a reader would be misled about what was established) or "minor" (an idealization or \
presentational choice). Be strict: a reversed inequality, a dropped hypothesis or a swapped quantifier is major.

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

# Passage(s) the statement bears on
{passages}
"""


def strip_comments(code):
    code = re.sub(r"/-[-!].*?-/\n?", "", code, flags=re.S)
    return "\n".join(line for line in code.splitlines() if line.strip()) + "\n"


def parse():
    """Return (prelude, blocks). `prelude` is every definition in the statement file, in order, comments removed,
    with the namespace lines kept so that it reads as Lean. `blocks` maps each declared name (qualified by its
    namespace inside `Unfolding`) to its declaration text."""
    spec = json.loads(ITEMS.read_text())
    statements = {n for it in spec["real"] for n in it["names"] if it["id"].startswith("S")}
    text = STATEMENT.read_text()
    body = text[text.index("namespace Unfolding"):text.index("end Unfolding")]
    blocks, prelude, stack = {}, [], []
    for chunk in re.split(r"\n(?=/--|/-!)", body):
        code = strip_comments(chunk)
        decl, rest = [], []
        for line in code.splitlines():
            if line.startswith(("namespace ", "end ", "variable ", "attribute ", "universe ")):
                rest.append(line)
            else:
                decl.append(line)
        decl_text = "\n".join(decl) + "\n" if decl else ""
        m = re.search(r"^(?:noncomputable )?(?:def|abbrev|structure) ([\w.′']+)", decl_text, flags=re.M)
        if m:
            name = ".".join(stack + [m.group(1)])
            blocks[name] = decl_text[m.start():]
            if m.group(1) not in statements:
                prelude.append(decl_text[m.start():])
        for line in rest:
            if line.startswith("namespace "):
                ns = line.split()[1]
                if ns != "Unfolding":
                    stack.append(ns)
            elif line.startswith("end ") and stack and line.split()[1] == stack[-1]:
                stack.pop()
            if not line.startswith("universe ") and line != "namespace Unfolding":
                prelude.append(line + "\n")
    return "".join(prelude), blocks


def anonymize(code, target_names=()):
    for name in target_names:
        code = re.sub(rf"(?<![\w.]){re.escape(name)}(?![\w′'])", "Target", code)
    for name, label in RENAME.items():
        code = re.sub(rf"(?<![\w]){name}(?![\w′'])", label, code)
    return code


def build_items():
    spec = json.loads(ITEMS.read_text())
    prelude, blocks = parse()
    passages = {}
    for sec in re.split(r"\n## ", (HERE / "passages.md").read_text())[1:]:
        pid = sec.split(" ")[0]
        if pid.startswith("P-"):
            head = re.sub(r" \[source: [^\]]+\]", "", sec.splitlines()[0])
            quote = " ".join(line[2:] for line in sec.splitlines() if line.startswith("> "))
            passages[pid] = f"[{head}]\n{quote}"
    context = anonymize(prelude)
    items = []
    for it in spec["real"]:
        is_statement = it["id"].startswith("S")
        target = "\n".join(blocks[n] for n in it["names"])
        target = anonymize(target, it["names"] if is_statement else ())
        if not is_statement:
            labels = ", ".join(anonymize(n.split(".")[-1]) for n in it["names"])
            target = f"-- The TARGET is these definitions, which also appear in the context: {labels}\n" + target
        items.append({**it, "decoy": False, "target": target, "context": context})
    for it in spec["decoys"]:
        code = strip_comments(it["lean"])
        names = re.findall(r"^(?:noncomputable )?(?:def|abbrev|structure) ([\w.′']+)", code, flags=re.M)
        items.append({**it, "names": names, "decoy": True, "target": anonymize(code, names), "context": context})
    for it in items:
        it["passage_text"] = "\n\n".join(passages[p] for p in it["passages"])
    order = spec["order"]
    assert sorted(order) == sorted(i["id"] for i in items), "order must list every item exactly once"
    return [next(i for i in items if i["id"] == k) for k in order]


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
            text, tin, tout, raw = call(vendor, (PROMPT_B_OWN if it.get("own") else PROMPT_B).format(
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
    if args == ["--probe"]:
        for v in ("openai", "google"):
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
        items = build_items()
        print("=" * 20, "context (the same for every item)")
        print(items[0]["context"])
        for it in items:
            print("=" * 20, it["id"], "decoy" if it["decoy"] else "")
            print(it["target"])
    else:
        sys.exit(__doc__)
