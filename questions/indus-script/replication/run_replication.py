#!/usr/bin/env python3
"""Ask a model from another vendor to write an independent implementation of the contest.

    python3 replication/run_replication.py google            # first request; writes replication/google/round1.*
    python3 replication/run_replication.py google FILE       # follow-up: FILE holds an error report to send back

The model sees protocol.md, analysis/METHOD.md and replication/FORMAT.md, and nothing else: none of our code and
none of our numbers. Follow-ups contain only tracebacks or a description of a crash. Standard library only.
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
VENDORS = {"google": {"model": "gemini-4-neon", "price": (3.00, 15.00)}}

PROMPT = """You are an independent replicator. Below are a locked analysis protocol, the step-by-step method it \
refers to, and notes on file formats. Write ONE complete Python 3.12 program that carries out one list's main \
analysis from scratch. Standard library only. You cannot run code or see the data; write carefully.

Requirements:
- Follow the method exactly, including every seed and the order of every random call, so that the numbers can be \
compared to two decimal places with an archive of published runs.
- Usage and output exactly as the format notes describe.
- Where the method is ambiguous, make a choice and list every such choice in a comment block at the top.
- Keep the program compact (aim for under 300 lines).
- Reply with the program in a single ```python fenced block and nothing else.

# protocol.md

{protocol}

# analysis/METHOD.md

{method}

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
        protocol = (Q / "protocol.md").read_text()
        for name in ("Eugene Jhong", "Eugene"):  # the director's name is not sent to outside services
            protocol = protocol.replace(name, "the lab's director")
        messages = [{"role": "user", "content": PROMPT.format(protocol=protocol,
                                                               method=(Q / "analysis" / "METHOD.md").read_text(),
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
