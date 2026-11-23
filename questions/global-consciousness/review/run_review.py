#!/usr/bin/env python3
"""Pre-lock design review: ask models from two other vendors to criticise protocol.md.

    python3 review/run_review.py <round-name>      # writes review/<round-name>/<vendor>.md and .json

Standard library only. Keys come from the environment: OPENAI_API_KEY, GEMINI_API_KEY.
"""
import datetime
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
# Model IDs and list prices (USD per million tokens, input/output), as recorded in the lab on 2026-11-22.
VENDORS = {"openai": {"model": "gpt-6.2-astra", "price": (8.00, 40.00)},
           "google": {"model": "gemini-4-neon", "price": (3.00, 15.00)}}

PROMPT = """You are reviewing a pre-registration (a locked analysis plan) for a test of a claimed anomaly in a \
network of hardware random-number generators, before any result exists. The plan is below. The analysis has not been run. Your job is to find problems now, \
while they can still be fixed.

Be concrete and critical. Please cover:
1. Flaws that could produce a false positive or a false negative (device variance biases, missing data, \
how windows and controls are chosen, the standardising, the normal approximation, mistakes in the statistics).
2. Decision rules that are unfair, too easy or too hard to pass, or that do not test what they claim to test.
3. Anything ambiguous enough that an independent programmer, given only this plan and the data files, could \
reasonably compute something different.
4. Important checks that are missing, in order of importance. Keep to what is feasible with the public data named \
in the plan.
5. Anything in the plan's summary of the literature that you believe is wrong. Say how confident you are.

For each point give a severity: "must fix", "should fix" or "minor". Finish with a short list of the three \
changes you would make first. Do not rewrite the plan.

# The plan

{protocol}
"""


NARROW = """You are doing a last check of a pre-registration (a locked analysis plan) for a test of a claimed \
anomaly in a network of random-number generators, before any result exists. It has been through one round of review already. Report ONLY:
(a) errors of sign, algebra or logic: places where a statistic, formula or decision rule would do something \
different from what the text says it does;
(b) factual statements you are confident are wrong;
(c) instructions that contradict each other.
Do not suggest additional checks, extra analyses or softer wording. If you find nothing in a category, say so. \
For each item, quote the sentence and give the correction in one or two lines.

# The plan

{protocol}
"""


def post(url, headers, body, timeout=1200):
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
    model = VENDORS[vendor]["model"]
    if vendor == "openai":
        raw = post("https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                   {"model": model, "messages": [{"role": "user", "content": prompt}], "reasoning_effort": "high"})
        u = raw.get("usage", {})
        return raw["choices"][0]["message"]["content"], u.get("prompt_tokens", 0), u.get("completion_tokens", 0), raw
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    raw = post(url, {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, {"contents": [{"role": "user", "parts": [{"text": prompt}]}]})
    text = "".join(p.get("text", "") for p in raw["candidates"][0]["content"]["parts"] if not p.get("thought"))
    u = raw.get("usageMetadata", {})
    return text, u.get("promptTokenCount", 0), u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0), raw


def main():
    out = HERE / sys.argv[1]
    out.mkdir(exist_ok=True)
    protocol = (HERE.parent / "protocol.md").read_text()
    (out / "protocol_as_reviewed.md").write_text(protocol)
    narrow = "--narrow" in sys.argv
    prompt = (NARROW if narrow else PROMPT).format(protocol=protocol)
    for vendor in [a for a in sys.argv[2:] if not a.startswith("--")] or list(VENDORS):
        text, tin, tout, raw = call(vendor, prompt)
        pin, pout = VENDORS[vendor]["price"]
        cost = (tin * pin + tout * pout) / 1e6
        meta = {"vendor": vendor, "model": VENDORS[vendor]["model"], "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "input_tokens": tin, "output_tokens": tout, "cost_usd_list_price": round(cost, 4)}
        (out / f"{vendor}.json").write_text(json.dumps(meta, indent=1) + "\n")
        (out / f"{vendor}.md").write_text(f"<!-- {json.dumps(meta)} -->\n\n{text}\n")
        print(meta)


if __name__ == "__main__":
    main()
