#!/usr/bin/env python3
"""Ask a model from another vendor to write an independent implementation of the protocol.

    python3 replication/run_replication.py openai            # first request; writes replication/openai/round1.*
    python3 replication/run_replication.py openai FILE       # follow-up: FILE holds an error report to send back

The model sees protocol.md, amendments.md and replication/FORMAT.md, and nothing else: none of our code and none
of our numbers. Follow-ups contain only tracebacks or a description of a crash. Standard library only.
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
Q = HERE.parent
VENDORS = {"openai": {"model": "gpt-6.2-astra", "price": (8.00, 40.00)},
           "google": {"model": "gemini-4-neon", "price": (3.00, 15.00)}}

PROMPT = """You are an independent replicator. Below are a locked analysis protocol, its amendments, and notes on \
file formats. Write ONE complete Python 3.12 program that carries out the analysis from scratch. You may use numpy \
and the standard library, nothing else. You cannot run code or see the data; write carefully.

Requirements:
- Usage: `python replicate.py OUTDIR`, run from the folder `questions/strangers/`.
- Build everything yourself from the `.anno`, `.ind`, `.snp` and `.geno` files by the protocol's rules: the tested \
people, their sides, types, sites and neighbours, and the reference sets. Do not read any other `.tsv`.
- Compute test 1 and test 2 for every tested person as the LOCKED protocol defines them (S with the fitted \
controls; E_R; D1 and D2; G_R), the single threshold, and the list of hits by the decision rule. You may skip the \
robustness checks, the centres, the made-up strangers and the amendment.
- Write the output files exactly as the strangers format note describes.
- It must finish in under 30 minutes on a machine with 128 GB of memory and 18 cores: vectorise with numpy and do \
not loop over SNPs in Python. The genotype file is 7 GB; about 13,000 people are needed. Processing people one at a \
time with numpy operations over the 1.15 million autosomal SNPs is fast enough.
- Where the protocol is ambiguous, make a choice and list every such choice in a comment block at the top.
- Keep the program compact (aim for under 600 lines); the whole reply must fit within your output limit.
- Reply with the program in a single ```python fenced block and nothing else.

# protocol.md

{protocol}

# amendments.md

{amendments}

# strangers/replication/FORMAT.md

{format}

# population-y/replication/FORMAT.md (the input files)

{format31}
"""


FOLLOWUP = """Your program was run and failed. Here is the report. Reply with the complete corrected program in a \
single ```python fenced block and nothing else.

{report}
"""


def post(url, headers, body, timeout=2400):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:600]
            if e.code in (429, 500, 502, 503, 529) and attempt < 2:
                time.sleep(15 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None


def call(vendor, messages):
    model = VENDORS[vendor]["model"]
    if vendor == "openai":
        raw = post("https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                   {"model": model, "messages": messages, "reasoning_effort": "high"})
        u = raw.get("usage", {})
        return raw["choices"][0]["message"]["content"], u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in messages]
    raw = post(url, {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, {"contents": contents})
    text = "".join(p.get("text", "") for p in raw["candidates"][0]["content"]["parts"] if not p.get("thought"))
    u = raw.get("usageMetadata", {})
    return text, u.get("promptTokenCount", 0), u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)


def main():
    vendor = sys.argv[1]
    out = HERE / vendor
    out.mkdir(exist_ok=True)
    convo = out / "conversation.json"
    if convo.exists():
        messages = json.loads(convo.read_text())
        messages.append({"role": "user", "content": FOLLOWUP.format(report=pathlib.Path(sys.argv[2]).read_text())})
    else:
        messages = [{"role": "user", "content": PROMPT.format(protocol=(Q / "protocol.md").read_text(),
                                                               amendments=(Q / "amendments.md").read_text(),
                                                               format=(HERE / "FORMAT.md").read_text(),
                                                               format31=(Q.parent / "population-y" / "replication" / "FORMAT.md").read_text())}]
    n = sum(1 for m in messages if m["role"] == "user")
    text, tin, tout = call(vendor, messages)
    messages.append({"role": "assistant", "content": text})
    convo.write_text(json.dumps(messages, indent=1))
    pin, pout = VENDORS[vendor]["price"]
    meta = {"vendor": vendor, "model": VENDORS[vendor]["model"], "round": n,
            "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "input_tokens": tin, "output_tokens": tout,
            "cost_usd_list_price": round((tin * pin + tout * pout) / 1e6, 4)}
    with open(out / "calls.jsonl", "a") as f:
        f.write(json.dumps(meta) + "\n")
    m = re.search(r"```python\n(.*)```", text, flags=re.S)
    code = m.group(1) if m else text
    (out / f"replicate_round{n}.py").write_text(code)
    print(meta, "lines of code:", code.count("\n"))


if __name__ == "__main__":
    main()
