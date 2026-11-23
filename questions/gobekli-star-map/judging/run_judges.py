"""Ask vision models to rank pictures by shape similarity. Standard library only.

Task A: one line figure + 12 object pictures (labelled A-L) -> ranking of all 12 letters.
Task B: one object picture + 8 line figures (labelled A-H) -> ranking of all 8 letters.

Usage (from questions/gobekli-star-map/):
  python judging/run_judges.py --make-trials --b-symbols S01,S02,... [--seed 92 --reps 5]
      writes judging/trials.json (identical for identical arguments)
  python judging/run_judges.py --vendor openai|google|xai --stimuli stimuli --out judging/out
      runs every trial in judging/trials.json, 4 at a time, resumable
  python judging/run_judges.py --probe openai|google|xai --stimuli stimuli
      2 Task A + 1 Task B trials on stimuli/dummy/ ONLY; prints, writes nothing
  python judging/run_judges.py --recognise openai|google|xai --stimuli stimuli --out judging/out [--dry-run]
      ONLY after all ranking trials are finished: two calls (8 figures with PROMPT_R1, 12 photographs with
      PROMPT_R2), saved to judging/out/<vendor>/recognition.json; skipped if that file exists.
      --dry-run builds both requests and prints them with image data replaced by its length; sends nothing.
  python judging/run_judges.py --collect judging/out
      writes judging/out/rankings.tsv (valid ranking trials only) and judging/out/summary.json (per vendor:
      model, trial counts, invalid count, first/last trial UTC, ranking tokens and cost, recognition
      tokens and cost under separate keys)

Images: Task A target stimuli/figures/<A..>.png, options stimuli/symbols_512/<S..>.png;
Task B the reverse. Keys come from OPENAI_API_KEY, GEMINI_API_KEY, XAI_API_KEY.
"""
import argparse, base64, concurrent.futures as cf, glob, json, os, random, re, socket, sys, time
import urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TRIALS = os.path.join(HERE, "trials.json")
FIGURES = [f"A{i:02d}" for i in range(1, 9)]
SYMBOLS = [f"S{i:02d}" for i in range(1, 13)]
LETTERS = "ABCDEFGHIJKL"
WORDS = {3: "three", 8: "eight", 12: "twelve"}

PROMPT_A = ("You will see one line drawing and {n} photographs labelled A to {last}. Each photograph "
            "shows a shape carved in stone. Rank the {n} photographs by how closely the overall shape of "
            "the carved figure resembles the line drawing, from most similar to least similar. Consider "
            "shape only; the drawing may match at any size. Do not explain. Reply with JSON only: "
            '{{"ranking": ["<letter>", ...]}} listing all {n} letters exactly once.')
PROMPT_B = ("You will see one photograph and {n} line drawings labelled A to {last}. The photograph "
            "shows a shape carved in stone. Rank the {n} line drawings by how closely each resembles the "
            "overall shape of the carved figure, from most similar to least similar. Consider shape only; "
            "a drawing may match at any size. Do not explain. Reply with JSON only: "
            '{{"ranking": ["<letter>", ...]}} listing all {n} letters exactly once.')

PROMPT_R1 = ("Here are eight line drawings. What do you think each one is a drawing of? Have you seen these "
             "drawings, or drawings like them, before, and if so where? Answer in a few sentences.")
PROMPT_R2 = ("Here are twelve photographs of shapes carved in stone. Do you recognise where these carvings are "
             "from? Do you know of any published claim about what they represent? Answer in a few sentences.")

VENDORS = {  # model id, USD per million tokens (input, output) or None
    "openai": ("gpt-6.2-astra", (8.0, 40.0)),
    "google": ("gemini-4-neon", (3.0, 15.0)),
    "xai": ("grok-4.7", None),
}
GEMINI_THINKING_BUDGET = 512


def make_trials(seed, reps, b_symbols):
    rng = random.Random(seed)
    trials = []
    for fig in FIGURES:
        for r in range(1, reps + 1):
            opts = SYMBOLS[:]; rng.shuffle(opts)
            trials.append({"id": f"A-{fig}-r{r}", "task": "A", "target": fig,
                           "letters": dict(zip(LETTERS, opts))})
    for sym in b_symbols:
        for r in range(1, reps + 1):
            opts = FIGURES[:]; rng.shuffle(opts)
            trials.append({"id": f"B-{sym}-r{r}", "task": "B", "target": sym,
                           "letters": dict(zip(LETTERS, opts))})
    return {"seed": seed, "reps": reps, "b_symbols": b_symbols, "trials": trials}


def prompt_for(trial):
    n = len(trial["letters"])
    tpl = PROMPT_A if trial["task"] == "A" else PROMPT_B
    return tpl.format(n=WORDS.get(n, str(n)), last=LETTERS[n - 1])


def build_parts(trial, path_of):
    """[(kind, value)] in request order: prompt, target, then options in letter order."""
    a = trial["task"] == "A"
    parts = [("text", prompt_for(trial)), ("text", "Line drawing:" if a else "Photograph:"),
             ("image", path_of(trial["target"]))]
    for letter, sid in trial["letters"].items():
        parts += [("text", f"{'Photograph' if a else 'Line drawing'} {letter}:"), ("image", path_of(sid))]
    return parts


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def http_json(url, body, headers, tries=6):
    data = json.dumps(body).encode()
    for i in range(tries):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:2000]
            if (e.code == 429 or e.code >= 500) and i < tries - 1:
                time.sleep(min(60, 2 ** i * 3 + random.random())); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}") from None
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
            if i < tries - 1:
                time.sleep(min(60, 2 ** i * 3 + random.random())); continue
            raise RuntimeError(f"network: {e}") from None


OPENAI_URL = "https://api.openai.com/v1/chat/completions"
XAI_URL = "https://api.x.ai/v1/chat/completions"
GOOGLE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_gemini_thinking = {"ok": True}


def request_for(vendor, parts):
    """(url, body) exactly as sent for this vendor; same settings for ranking and recognition calls."""
    model = VENDORS[vendor][0]
    if vendor == "google":
        ps = [{"text": v} if k == "text" else {"inlineData": {"mimeType": "image/png", "data": b64(v)}}
              for k, v in parts]
        body = {"contents": [{"role": "user", "parts": ps}]}
        if _gemini_thinking["ok"]:
            body["generationConfig"] = {"thinkingConfig": {"thinkingBudget": GEMINI_THINKING_BUDGET}}
        return GOOGLE_URL.format(model=model), body
    content = [{"type": "text", "text": v} if k == "text" else
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64(v)}}
               for k, v in parts]
    body = {"model": model, "messages": [{"role": "user", "content": content}]}
    if vendor == "openai":
        body["reasoning_effort"] = "low"
    return (OPENAI_URL if vendor == "openai" else XAI_URL), body


def call(vendor, parts):
    """Return (reply text, input tokens, output tokens)."""
    url, body = request_for(vendor, parts)
    if vendor != "google":
        key = os.environ["OPENAI_API_KEY" if vendor == "openai" else "XAI_API_KEY"]
        r = http_json(url, body, {"Authorization": "Bearer " + key})
        u = r.get("usage", {})
        return (r["choices"][0]["message"].get("content") or "", u.get("prompt_tokens", 0),
                u.get("completion_tokens", 0))
    try:
        r = http_json(url, body, {"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    except RuntimeError as e:
        if "HTTP 400" in str(e) and "hinking" in str(e) and _gemini_thinking["ok"]:
            _gemini_thinking["ok"] = False  # API refused the budget: fall back to default thinking
            print("google: thinkingBudget refused, using default:", str(e)[:300], file=sys.stderr)
            return call(vendor, parts)
        raise
    u = r.get("usageMetadata", {})
    cand = (r.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
    return text, u.get("promptTokenCount", 0), u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)


def parse(text, trial):
    """Return (ranking as stimulus ids, valid)."""
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        letters = [str(x).strip().upper() for x in json.loads(m.group(0))["ranking"]]
    except Exception:
        return [], False
    mp = trial["letters"]
    ids = [mp.get(x, "?" + x) for x in letters]
    return ids, sorted(letters) == sorted(mp) and len(letters) == len(mp)


def cost(vendor, tin, tout):
    p = VENDORS[vendor][1]
    return None if p is None else round((tin * p[0] + tout * p[1]) / 1e6, 6)


def run_trial(vendor, trial, path_of):
    parts, attempts, t0 = build_parts(trial, path_of), [], time.time()
    for _ in range(3):  # first try + up to 2 retries for an invalid reply
        text, tin, tout = call(vendor, parts)
        ids, valid = parse(text, trial)
        attempts.append({"raw": text, "input_tokens": tin, "output_tokens": tout, "valid": valid})
        if valid:
            break
    tin, tout = sum(a["input_tokens"] for a in attempts), sum(a["output_tokens"] for a in attempts)
    return {"trial": trial, "vendor": vendor, "model": VENDORS[vendor][0], "prompt": prompt_for(trial),
            "raw": text, "ranking": ids, "valid": valid, "attempts": attempts,
            "input_tokens": tin, "output_tokens": tout, "cost_usd": cost(vendor, tin, tout),
            "seconds": round(time.time() - t0, 2), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def run_vendor(vendor, stimuli, out):
    trials = json.load(open(TRIALS))["trials"]
    d = os.path.join(out, vendor); os.makedirs(d, exist_ok=True)

    def path_of(sid):
        return os.path.join(stimuli, "figures" if sid.startswith("A") else "symbols_512", sid + ".png")

    todo = [t for t in trials if not os.path.exists(os.path.join(d, t["id"] + ".json"))]
    print(f"{vendor}: {len(trials) - len(todo)} done, {len(todo)} to run")

    def one(t):
        rec = run_trial(vendor, t, path_of)
        tmp = os.path.join(d, t["id"] + ".json.tmp")
        json.dump(rec, open(tmp, "w"), indent=1); os.replace(tmp, tmp[:-4])
        return t["id"], rec["valid"]

    with cf.ThreadPoolExecutor(4) as ex:
        for fut in cf.as_completed([ex.submit(one, t) for t in todo]):
            try:
                print(*fut.result())
            except Exception as e:  # leave the trial unwritten so a re-run retries it
                print("FAILED:", str(e)[:500], file=sys.stderr)


def probe(vendor, stimuli):
    dd = os.path.join(stimuli, "dummy")
    objs, lines = [f"D{i:02d}" for i in range(1, 13)], ["L01", "L02", "L03"]
    rng = random.Random(1)
    trials = []
    for tgt in ("L01", "L02"):
        o = objs[:]; rng.shuffle(o)
        trials.append({"id": f"probe-A-{tgt}", "task": "A", "target": tgt, "letters": dict(zip(LETTERS, o))})
    o = lines[:]; rng.shuffle(o)
    trials.append({"id": "probe-B-D03", "task": "B", "target": "D03", "letters": dict(zip(LETTERS, o))})
    total = 0.0
    for t in trials:
        rec = run_trial(vendor, t, lambda sid: os.path.join(dd, sid + ".png"))
        print(f"\n[{vendor} {VENDORS[vendor][0]}] {t['id']} valid={rec['valid']} attempts={len(rec['attempts'])}")
        print("reply:", rec["raw"][:400].replace("\n", " "))
        print("ranking (ids):", rec["ranking"])
        print(f"tokens in/out: {rec['input_tokens']}/{rec['output_tokens']}  cost: {rec['cost_usd']}  "
              f"time: {rec['seconds']}s")
        total += rec["cost_usd"] or 0
    print(f"\nprobe total cost ({vendor}): ${total:.4f}")


def recognition_parts(stimuli):
    p1 = [("text", PROMPT_R1)]
    for i, a in enumerate(FIGURES, 1):
        p1 += [("text", f"Drawing {i}:"), ("image", os.path.join(stimuli, "figures", a + ".png"))]
    p2 = [("text", PROMPT_R2)]
    for i, sid in enumerate(SYMBOLS, 1):
        p2 += [("text", f"Photograph {i}:"), ("image", os.path.join(stimuli, "symbols_512", sid + ".png"))]
    return [("R1", p1), ("R2", p2)]


def redact(x):
    """Copy of a request body with base64 image data replaced by its length."""
    if isinstance(x, dict):
        return {k: (f"<{len(v)} base64 chars>" if k == "data" else
                    f"data:image/png;base64,<{len(v) - 22} base64 chars>" if k == "url" and v.startswith("data:")
                    else redact(v)) for k, v in x.items()}
    return [redact(v) for v in x] if isinstance(x, list) else x


def recognise(vendor, stimuli, out, dry_run=False):
    calls = recognition_parts(stimuli)
    if dry_run:
        for name, parts in calls:
            url, body = request_for(vendor, parts)
            print(f"--- {name} POST {url}\n" + json.dumps(redact(body), indent=1))
        return
    path = os.path.join(out, vendor, "recognition.json")
    if os.path.exists(path):
        print("exists, skipping:", path); return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rec = {"vendor": vendor, "model": VENDORS[vendor][0], "calls": []}
    for name, parts in calls:
        t0 = time.time()
        text, tin, tout = call(vendor, parts)
        rec["calls"].append({"call": name, "prompt": parts[0][1],
                             "images": [os.path.relpath(v, stimuli) for k, v in parts if k == "image"],
                             "raw": text, "input_tokens": tin, "output_tokens": tout,
                             "cost_usd": cost(vendor, tin, tout), "seconds": round(time.time() - t0, 2),
                             "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        print(f"[{vendor}] {name}: {text}\n")
    json.dump(rec, open(path + ".tmp", "w"), indent=1); os.replace(path + ".tmp", path)


def collect(out):
    rows, summ = [], {}

    def add_cost(s, key, c):
        s[key] = None if (c is None or s[key] is None) else round(s[key] + c, 6)

    for v in sorted(os.listdir(out)):
        d = os.path.join(out, v)
        if not os.path.isdir(d):
            continue
        s = summ[v] = {"model": VENDORS.get(v, ("?",))[0], "trials": 0, "valid": 0, "invalid": 0,
                       "first_trial_utc": None, "last_trial_utc": None, "input_tokens": 0, "output_tokens": 0,
                       "cost_usd": 0.0, "recognition_input_tokens": 0, "recognition_output_tokens": 0,
                       "recognition_cost_usd": 0.0}
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            r = json.load(open(f))
            if os.path.basename(f) == "recognition.json":
                for c in r["calls"]:
                    s["recognition_input_tokens"] += c["input_tokens"]
                    s["recognition_output_tokens"] += c["output_tokens"]
                    add_cost(s, "recognition_cost_usd", c["cost_usd"])
                continue
            t = r["trial"]; s["model"] = r["model"]
            s["trials"] += 1; s["valid" if r["valid"] else "invalid"] += 1
            s["input_tokens"] += r["input_tokens"]; s["output_tokens"] += r["output_tokens"]
            add_cost(s, "cost_usd", r["cost_usd"])
            s["first_trial_utc"] = min(filter(None, [s["first_trial_utc"], r["utc"]]))
            s["last_trial_utc"] = max(filter(None, [s["last_trial_utc"], r["utc"]]))
            if r["valid"]:
                rows += [(v, t["id"], t["task"], t["target"], str(i + 1), sid) for i, sid in enumerate(r["ranking"])]
        if VENDORS.get(v, (0, None))[1] is None:
            s["cost_usd"] = s["recognition_cost_usd"] = None
    with open(os.path.join(out, "rankings.tsv"), "w") as f:
        f.write("vendor\ttrial_id\ttask\ttarget_id\tposition\toption_id\n")
        f.writelines("\t".join(x) + "\n" for x in rows)
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--make-trials", action="store_true")
    ap.add_argument("--b-symbols", help="comma-separated symbol ids for Task B, e.g. S01,S02")
    ap.add_argument("--seed", type=int, default=92)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--vendor", choices=VENDORS)
    ap.add_argument("--probe", choices=VENDORS)
    ap.add_argument("--recognise", choices=VENDORS)
    ap.add_argument("--dry-run", action="store_true", help="with --recognise: print requests, send nothing")
    ap.add_argument("--collect", metavar="OUT")
    ap.add_argument("--stimuli", default=os.path.join(HERE, "..", "stimuli"))
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    a = ap.parse_args()
    if a.make_trials:
        if not a.b_symbols:
            ap.error("--make-trials needs --b-symbols")
        b = [s.strip() for s in a.b_symbols.split(",")]
        assert all(s in SYMBOLS for s in b) and len(set(b)) == len(b), b
        with open(TRIALS, "w") as f:
            json.dump(make_trials(a.seed, a.reps, b), f, indent=1)
        print("wrote", TRIALS)
    elif a.probe:
        probe(a.probe, a.stimuli)
    elif a.vendor:
        run_vendor(a.vendor, a.stimuli, a.out)
    elif a.recognise:
        recognise(a.recognise, a.stimuli, a.out, a.dry_run)
    elif a.collect:
        collect(a.collect)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
