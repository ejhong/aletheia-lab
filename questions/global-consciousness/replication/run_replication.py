#!/usr/bin/env python3
"""Ask a model from another vendor to write an independent implementation of the protocol.

    python3 replication/run_replication.py openai            # first request; writes replication/openai/round1.*
    python3 replication/run_replication.py openai FILE       # follow-up: FILE holds an error report to send back

The model sees protocol.md, events.tsv and replication/FORMAT.md, and nothing else: none of our code and none
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

PROMPT = """You are an independent replicator. Below are a locked analysis protocol, the event list it uses, and \
notes on file formats. Write ONE complete Python 3.12 program that carries out the analysis from scratch. You may \
use numpy and the standard library, nothing else. You cannot run code or see the data; write carefully.

Requirements:
- Usage: `python replicate.py OUTDIR`, run from the folder `questions/global-consciousness/`.
- Read `events.tsv` and the day files, and score every event window and every control window of the events marked \
`in_test = yes`, exactly as the protocol's sections "The data" and "The statistic" say, including the cleaning, the \
egg check and the standardising from the control windows of the same year.
- Compute the combined scores for events and for controls, the two verdicts, and the paired check.
- You may skip the other items under "Reported alongside" (classes, theoretical standardising, the cross-egg part).
- Write the output files exactly as the format notes describe.
- Each day file holds 86,400 lines of about 40 fields; there are about 160 of them. Parse each file once and keep \
the arrays in memory or cache them; the whole run should take minutes, not hours.
- Where the protocol is ambiguous, make a choice and list every such choice in a comment block at the top.
- Keep the program compact (aim for under 300 lines).
- Reply with the program in a single ```python fenced block and nothing else.

# protocol.md

{protocol}

# events.tsv

{events}

# replication/FORMAT.md

{format}
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
                                                               events=(Q / "events.tsv").read_text(),
                                                               format=(HERE / "FORMAT.md").read_text())}]
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
