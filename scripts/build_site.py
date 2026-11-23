#!/usr/bin/env python3
"""Build the lab's website into _site/ (Python standard library only).

    python3 scripts/build_site.py               build; read issue titles, labels and text from GitHub if possible
    python3 scripts/build_site.py --offline     build without the network (every status then shows as proposed)
    python3 scripts/build_site.py --snapshot    refresh site/issues-snapshot.json from GitHub, then build

Preview the result with:  python3 -m http.server -d _site 8000

Inputs
  QUESTIONS.md               the question table: number, title, lane, folder slug
  GitHub issues              status:* and lane:* labels, titles, issue text (text falls back to the snapshot)
  site/issues-snapshot.json  copy of issue titles and text for offline builds; never holds labels
  AGENTS.md                  the lanes table (section 4)
  SPENDING.md                the spending log
  site/templates/            base.html (page shell), home.html (home page prose)
  site/pages/                how-it-works.md
  site/content/<slug>.md     optional full page for a question; replaces the short page built from the issue
  site/figures/<slug>/       HTML fragments (inline SVG charts) that a content file includes with {{figure: slug/name}}
  site/assets/               CSS, JS, icon

Content files are Markdown with an optional front matter block (key: value lines between --- lines). The keys
are summary (the question in a sentence, shown in lists), dek (the page's opening line), updated (a date), and,
once there is an outcome, verdict (a few words) and result (two or three plain sentences). The home page shows
verdict and result under the question, so a reader need not open the page to learn what was found. Inside them,
a heading "### Stage N · Title" starts a stage of the plan; its first lines may be "Status: done | in progress |
not started", "Gate: ..." and "Condition: ...". Consecutive stages render as the progress timeline. A line
"::: details Title" opens a folded section and a line ":::" closes it.

The build never fails because GitHub is unreachable.
"""
from __future__ import annotations

import datetime
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "_site"
SNAPSHOT = SITE / "issues-snapshot.json"
REPO = os.environ.get("GITHUB_REPOSITORY") or "ejhong/aletheia-lab"
REPO_URL = "https://github.com/" + REPO
ATLAS_URL = "https://ejhong.github.io/aletheia/"
ATLAS_CLAIM_URL = ATLAS_URL + "claims/{}/"
BASE_PATH = (os.environ.get("SITE_BASE_PATH") or "/aletheia-lab").rstrip("/") + "/"
# Share images need absolute addresses: a link preview is fetched by X or Slack, not by a browser on the page.
SITE_ORIGIN = (os.environ.get("SITE_ORIGIN") or "https://ejhong.github.io").rstrip("/")
CARDS = SITE / "assets" / "cards"

LANES = ["data", "model", "proof", "audit", "protocol", "watch"]
GROUPS = [("active", "Now running"), ("done", "Done"), ("proposed", "Proposed")]
STATUS_TEXT = {
    "active": "Being worked on now. At most two questions are active at a time.",
    "proposed": "Not started. Eugene picks which questions become active, two at most at a time.",
    "done": "Finished: the lane's definition of done has been met.",
}
# Used only if the lanes table cannot be read from AGENTS.md.
LANE_FALLBACK = {
    "data": ("Re-running the analysis from scratch on public data", ""),
    "model": ("Many calls to several vendors' models, scripted", ""),
    "proof": ("The Lean build: compiles with no `sorry`, or doesn't", ""),
    "audit": ("Sources read in the original, with locators", ""),
    "protocol": ("Nothing to run; needs people or a lab", ""),
    "watch": ("New publications", ""),
}
# Small monochrome markers, one per lane, drawn on a 12x12 grid.
LANE_SHAPES = {
    "data": '<rect x="1" y="6.5" width="2.4" height="4.5"/><rect x="4.8" y="3.5" width="2.4" height="7.5"/>'
            '<rect x="8.6" y="1" width="2.4" height="10"/>',
    "model": '<circle cx="4.4" cy="6" r="3.4" fill="none" stroke="currentColor" stroke-width="1.2"/>'
             '<circle cx="7.6" cy="6" r="3.4" fill="none" stroke="currentColor" stroke-width="1.2"/>',
    "proof": '<rect x="1.75" y="1.75" width="8.5" height="8.5"/>',
    "audit": '<path d="M1.5 2.75h9M1.5 6h9M1.5 9.25h5.5" fill="none" stroke="currentColor" stroke-width="1.3"/>',
    "protocol": '<rect x="2" y="2" width="8" height="8" fill="none" stroke="currentColor" stroke-width="1.2" '
                'stroke-dasharray="2.2 1.4"/>',
    "watch": '<circle cx="6" cy="6" r="4.4" fill="none" stroke="currentColor" stroke-width="1.2"/>'
             '<circle cx="6" cy="6" r="1.7"/>',
}
STAGE_STATES = {
    "done": "done", "complete": "done", "completed": "done", "finished": "done",
    "in progress": "current", "in-progress": "current", "started": "current", "active": "current", "current": "current",
    "not started": "todo", "not-started": "todo", "todo": "todo", "planned": "todo", "next": "todo",
    "dropped": "dropped", "skipped": "dropped", "on hold": "todo",
}


def esc(s):
    return html.escape(str(s), quote=True)


# --------------------------------------------------------------------------------------------------------------
# Markdown: the small subset the site uses. Raw HTML is escaped, never passed through.
# --------------------------------------------------------------------------------------------------------------

SAFE_URL = re.compile(r"^(https?://|mailto:|#|\.{0,2}/|[\w][\w./-]*(#[\w-]*)?$)", re.I)
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
STAGE_RE = re.compile(r"^###\s+Stage\s+(\w+)\s*[·:.\-–—]\s*(.+?)\s*$")
PLACEHOLDER_RE = re.compile(r"^\{\{\s*([\w-]+)\s*\}\}$")
FIGURE_RE = re.compile(r"^\{\{\s*figure:\s*([\w-]+(?:/[\w-]+)*)\s*\}\}$")
DETAILS_RE = re.compile(r"^:::\s*details\s+(.+?)\s*$")


def inline(text, stash=None):
    """Inline Markdown: `code`, [links](url), <https://autolinks>, **strong**, *em* and _em_."""
    top = stash is None
    stash = [] if top else stash

    def keep(s):
        stash.append(s)
        return "\x00%d\x00" % (len(stash) - 1)

    text = re.sub(r"`([^`]+)`", lambda m: keep("<code>%s</code>" % esc(m.group(1))), text)

    def link(m):
        label, url = m.group(1), m.group(2)
        inner = inline(label, stash)
        if not SAFE_URL.match(url):
            return keep(inner)
        return keep('<a href="%s">%s</a>' % (esc(url), inner))

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"<(https?://[^>\s]+)>", lambda m: keep('<a href="%s">%s</a>' % (esc(m.group(1)), esc(m.group(1)))),
                  text)
    text = esc(text)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w])_(?=\S)(.+?)(?<=\S)_(?![\w])", r"<em>\1</em>", text)
    if top:
        while "\x00" in text:
            text = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
    return text


def plain(text):
    """Markdown to plain text, for meta descriptions."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[`*]|(?<![\w])_|_(?![\w])", "", text)
    return re.sub(r"\s+", " ", text).strip()


def slugify(text):
    s = re.sub(r"<[^>]+>|&\w+;", "", text).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "section"


class Doc:
    """Rendering context for one page: unique heading ids, the h2 outline, and named placeholder blocks."""

    def __init__(self, blocks=None):
        self.ids = set()
        self.outline = []
        self.blocks = blocks or {}

    def uid(self, base):
        base = slugify(base)
        n, uid = 2, base
        while uid in self.ids:
            uid, n = "%s-%d" % (base, n), n + 1
        self.ids.add(uid)
        return uid


def is_block_start(s):
    return bool(re.match(r"^(#{1,6}\s|```|:::|>|\||(-{3,}|\*{3,})$)", s)) or bool(LIST_RE.match(s))


def render_list(items, i, indent):
    ordered = items[i][1]
    has_tasks = any(re.match(r"\[[ xX]\]\s", it[2]) for it in items[i:] if it[0] == indent)
    tag = "ol" if ordered else "ul"
    out = ["<%s%s>" % (tag, ' class="tasks"' if has_tasks else "")]
    while i < len(items) and items[i][0] >= indent:
        text = items[i][2]
        m = re.match(r"\[([ xX])\]\s+(.*)$", text)
        if m:
            done = m.group(1) != " "
            body = '<span class="sr">%s </span>%s' % ("Done:" if done else "Not done:", inline(m.group(2)))
            li_open = '<li class="task%s">' % (" is-done" if done else "")
        else:
            body, li_open = inline(text), "<li>"
        i += 1
        if i < len(items) and items[i][0] > indent:
            child, i = render_list(items, i, items[i][0])
            body += child
        out.append(li_open + body + "</li>")
    out.append("</%s>" % tag)
    return "".join(out), i


def render_table(rows):
    def cells(row):
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in row.split("|")]

    head, aligns, body = cells(rows[0]), cells(rows[1]), [cells(r) for r in rows[2:]]

    def align(k):
        a = aligns[k] if k < len(aligns) else ""
        if a.startswith(":") and a.endswith(":"):
            return ' style="text-align:center"'
        return ' style="text-align:right"' if a.endswith(":") else ""

    out = ['<div class="table-wrap"><table><thead><tr>']
    out += ['<th scope="col"%s>%s</th>' % (align(k), inline(c)) for k, c in enumerate(head)]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join("<td%s>%s</td>" % (align(k), inline(c)) for k, c in enumerate(r)) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def render_note(lines, doc):
    first = lines[0] if lines else ""
    m = re.match(r"^\*\*(.+?)[.:]?\*\*\s*(.*)$", first)
    label = ""
    if m:
        label = '<p class="note-label">%s</p>' % inline(m.group(1))
        lines = [m.group(2)] + lines[1:]
    return '<div class="note" role="note">%s%s</div>' % (label, blocks("\n".join(lines), doc))


def blocks(md, doc):
    """Block-level Markdown: headings, paragraphs, lists (nested, task lists), notes (>), tables, code, rules."""
    lines = md.replace("\t", "    ").split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line, s = lines[i], lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            j, code = i + 1, []
            while j < n and not lines[j].strip().startswith("```"):
                code.append(lines[j])
                j += 1
            out.append("<pre><code>%s</code></pre>" % esc("\n".join(code)))
            i = j + 1
            continue
        m = DETAILS_RE.match(s)
        if m:
            # "::: details Title" ... ":::" folds a stretch of the page away behind its title.
            j, inner = i + 1, []
            while j < n and lines[j].strip() != ":::":
                inner.append(lines[j])
                j += 1
            out.append('<details class="more"><summary>%s</summary><div class="more-body">%s</div></details>'
                       % (inline(m.group(1)), blocks("\n".join(inner), doc)))
            i = j + 1
            continue
        m = FIGURE_RE.match(s)
        if m:
            # {{figure: folder/name}} drops in site/figures/folder/name.html as it stands. These fragments are files
            # in this repository (inline SVG and captions made by a question's own script), so they are trusted.
            out.append((SITE / "figures" / (m.group(1) + ".html")).read_text())
            i += 1
            continue
        m = PLACEHOLDER_RE.match(s)
        if m:
            out.append(doc.blocks[m.group(1)])
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", s)
        if m:
            level, text = len(m.group(1)), m.group(2)
            # "## A long heading {menu: Short}" keeps the heading and its id, and uses "Short" in the page's menu.
            short = ""
            ms = re.match(r"^(.*?)\s*\{menu:\s*(.+?)\}$", text)
            if ms:
                text, short = ms.group(1), ms.group(2)
            hid = doc.uid(text)
            if level == 2:
                doc.outline.append((hid, plain(short or text)))
            out.append('<h%d id="%s">%s</h%d>' % (level, hid, inline(text), level))
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            out.append("<hr>")
            i += 1
            continue
        if s.startswith(">"):
            q = []
            while i < n and lines[i].strip().startswith(">"):
                q.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(render_note(q, doc))
            continue
        if s.startswith("|") and i + 1 < n and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(render_table(rows))
            continue
        if LIST_RE.match(line):
            items = []
            while i < n:
                cur = lines[i]
                m = LIST_RE.match(cur)
                if m:
                    items.append([len(m.group(1)), m.group(2)[-1] in ".)", m.group(3).strip()])
                    i += 1
                elif not cur.strip():
                    j = i
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and LIST_RE.match(lines[j]):
                        i = j
                    elif j < n and lines[j].startswith("  "):
                        i = j
                    else:
                        break
                elif cur.startswith("  ") or not is_block_start(cur.strip()):
                    items[-1][2] += " " + cur.strip()
                    i += 1
                else:
                    break
            base = min(it[0] for it in items)
            for it in items:
                it[0] -= base
            html_list, _ = render_list(items, 0, 0)
            out.append(html_list)
            continue
        para = []
        while i < n and lines[i].strip() and not (para and is_block_start(lines[i].strip())):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(para)))
    return "\n".join(out)


def front_matter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            meta = {}
            for line in text[4:end].splitlines():
                if ":" in line and not line.lstrip().startswith("#"):
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
            return meta, text[end + 5:]
    return {}, text


# --------------------------------------------------------------------------------------------------------------
# Stages: the plan of a question, as a progress view.
# --------------------------------------------------------------------------------------------------------------

def parse_stage(m, body_lines):
    meta, k = {}, 0
    while k < len(body_lines):
        mm = re.match(r"^(Status|Gate|Condition):\s*(.+)$", body_lines[k].strip(), re.I)
        if not mm:
            break
        meta[mm.group(1).lower()] = mm.group(2).strip()
        k += 1
    body = "\n".join(body_lines[k:])
    status_text = meta.get("status", "not started")
    tasks = re.findall(r"^\s*(?:[-*+]|\d+[.)])\s+\[([ xX])\]", body, re.M)
    return {
        "num": m.group(1), "title": m.group(2), "status_text": status_text,
        "state": STAGE_STATES.get(status_text.lower().rstrip("."), "todo"),
        "gate": meta.get("gate", ""), "condition": meta.get("condition", ""), "body": body,
        "tasks": len(tasks), "tasks_done": sum(1 for t in tasks if t != " "),
        "id": "stage-" + slugify(m.group(1)),
    }


def find_stages(md):
    lines = md.split("\n")
    stages = []
    for i, line in enumerate(lines):
        m = STAGE_RE.match(line)
        if m:
            j = i + 1
            while j < len(lines) and not re.match(r"^#{1,3}\s", lines[j]):
                j += 1
            stages.append(parse_stage(m, lines[i + 1:j]))
    return stages


def stage_pill(st):
    cls = {"done": "pill-done", "current": "pill-active", "todo": "pill-todo", "dropped": "pill-todo"}[st["state"]]
    return '<span class="pill %s"><span class="dot" aria-hidden="true"></span>%s</span>' % (cls, esc(st["status_text"]))


def steps_text(st):
    if not st["tasks"]:
        return ""
    return "%d of %d step%s done" % (st["tasks_done"], st["tasks"], "" if st["tasks"] == 1 else "s")


def render_stages(stages, doc):
    out = ['<ol class="stages">']
    for st in stages:
        doc.ids.add(st["id"])
        count = steps_text(st)
        parts = ['<li class="stage is-%s" id="%s">' % (st["state"], st["id"]),
                 '<span class="stage-node" aria-hidden="true"></span>',
                 '<h3 class="stage-title"><span class="stage-num">Stage %s</span> %s</h3>' % (esc(st["num"]),
                                                                                             inline(st["title"])),
                 '<p class="stage-meta">%s%s</p>' % (stage_pill(st),
                                                     '<span class="stage-count">%s</span>' % count if count else "")]
        if st["condition"]:
            parts.append('<p class="stage-cond">%s</p>' % inline(st["condition"]))
        parts.append('<div class="stage-body">%s</div>' % blocks(st["body"], doc))
        if st["gate"]:
            parts.append('<p class="gate"><span class="gate-label"><span aria-hidden="true">◆</span> Gate</span>'
                         '<span>%s</span></p>' % inline(st["gate"]))
        parts.append("</li>")
        out.append("".join(parts))
    out.append("</ol>")
    return "\n".join(out)


def render_track(stages):
    """The compact progress view shown at the top of a question page."""
    items = []
    for st in stages:
        status = esc(st["status_text"])
        if st["tasks"]:
            status += " · %d of %d steps" % (st["tasks_done"], st["tasks"])
        items.append(
            '<li class="t-stage is-%s"><a class="t-link" href="#%s">'
            '<span class="t-node" aria-hidden="true"></span>'
            '<span class="t-num">Stage %s</span><span class="t-title">%s</span>'
            '<span class="t-status">%s</span></a></li>' % (st["state"], st["id"], esc(st["num"]), inline(st["title"]),
                                                           status))
    return ('<div class="track"><p class="label">The plan · %d stages, each ending at a gate</p>'
            '<ol class="track-list" style="--n:%d">%s</ol>'
            '<p class="track-key" aria-hidden="true"><span class="kp"><span class="k k-done"></span>Done</span>'
            '<span class="kp"><span class="k k-current"></span>In progress</span>'
            '<span class="kp"><span class="k k-todo"></span>Not started</span>'
            '<span class="kp"><span class="k k-gate"></span>Gate: Eugene decides</span></p></div>'
            % (len(stages), len(stages), "".join(items)))


def render_doc(md, doc):
    """Markdown with stage blocks. Consecutive '### Stage N · Title' sections become one timeline."""
    lines = md.split("\n")
    out, buf, stages, i = [], [], [], 0
    while i < len(lines):
        m = STAGE_RE.match(lines[i])
        if m:
            if buf:
                out.append(blocks("\n".join(buf), doc))
                buf = []
            j = i + 1
            while j < len(lines) and not re.match(r"^#{1,3}\s", lines[j]):
                j += 1
            stages.append(parse_stage(m, lines[i + 1:j]))
            i = j
            continue
        if stages:
            out.append(render_stages(stages, doc))
            stages = []
        buf.append(lines[i])
        i += 1
    if stages:
        out.append(render_stages(stages, doc))
    if buf:
        out.append(blocks("\n".join(buf), doc))
    return "\n".join(out)


# --------------------------------------------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------------------------------------------

def read_questions():
    text = (ROOT / "QUESTIONS.md").read_text(encoding="utf-8")
    intro, rows = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            m = re.search(r"#(\d+)", cells[0])
            if not m or len(cells) < 4:
                continue
            slug = cells[3].strip("` ")
            if not re.match(r"^[a-z0-9][a-z0-9-]*$", slug):
                print("skipping row with bad folder name: %r" % slug, file=sys.stderr)
                continue
            rows.append({"number": int(m.group(1)), "title": cells[1], "lane": cells[2].lower(), "slug": slug})
        elif s and not s.startswith("#") and not rows:
            intro.append(s)
    return " ".join(intro), rows


def fetch_rest(url, token):
    out = []
    while url:
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json", "User-Agent": "aletheia-lab-site-builder",
            "X-GitHub-Api-Version": "2022-11-28"})
        if token:
            req.add_header("Authorization", "Bearer " + token)
        with urllib.request.urlopen(req, timeout=15) as r:
            out += json.load(r)
            m = re.search(r'<([^>]+)>;\s*rel="next"', r.headers.get("Link") or "")
            url = m.group(1) if m else None
    return out


def fetch_gh():
    p = subprocess.run(
        ["gh", "api", "--paginate", "repos/%s/issues?state=all&per_page=100" % REPO,
         "--jq", ".[] | {number, title, body, labels: [.labels[].name], pull_request}"],
        capture_output=True, text=True, timeout=60, cwd=ROOT)
    if p.returncode:
        raise RuntimeError(p.stderr.strip()[:300])
    return [json.loads(line) for line in p.stdout.splitlines() if line.strip()]


def fetch_issues(offline):
    """({number: {title, body, labels}}, source name), or (None, reason). Never raises."""
    if offline:
        return None, "offline"
    url = "https://api.github.com/repos/%s/issues?state=all&per_page=100" % REPO
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    attempts = []
    if token:
        attempts.append(("GitHub API with token", lambda: fetch_rest(url, token)))
    if shutil.which("gh"):
        attempts.append(("gh", fetch_gh))
    attempts.append(("GitHub API without token", lambda: fetch_rest(url, None)))
    for name, fn in attempts:
        try:
            issues = {}
            for it in fn():
                if it.get("pull_request"):
                    continue
                labels = [lab["name"] if isinstance(lab, dict) else lab for lab in it.get("labels") or []]
                issues[int(it["number"])] = {"title": it.get("title") or "", "body": it.get("body") or "",
                                             "labels": labels}
            if issues:
                return issues, name
        except Exception as e:  # any failure: try the next way, then fall back
            print("  %s failed: %s: %s" % (name, e.__class__.__name__, str(e)[:200]), file=sys.stderr)
    return None, "unavailable"


def parse_issue_body(body):
    """The '**Field:** value' paragraphs at the top of an issue, and its closing italic note."""
    fields, note = {}, ""
    paras = re.split(r"\n\s*\n", (body or "").replace("\r\n", "\n"))
    for p in paras:
        p = p.strip()
        if p.startswith("#"):
            break
        m = re.match(r"^\*\*([^*]+?):\*\*\s*(.*)$", p, re.S)
        if m:
            fields[m.group(1).strip()] = re.sub(r"\s*\n\s*", " ", m.group(2).strip())
    for p in reversed(paras):
        p = p.strip()
        if re.match(r"^_.+_$", p, re.S):
            note = p[1:-1].strip()
            break
    return fields, note


def brainstorm_caveat(note):
    """Keep the 'from a brainstorm, unverified' sentence; drop the status sentence (labels show status)."""
    if "brainstorm" not in note.lower():
        return ""
    sentences = re.split(r"(?<=\.)\s+", note)
    return " ".join(s for s in sentences if not s.lower().startswith("not started"))


def gist(text):
    """A short excerpt for the index: up to the first question among the first two sentences, else the first."""
    sentences = [s for s in re.split(r"(?<=[.?!])[\"”’)]*\s+(?=[A-Z“\"(])", text.strip()) if s]
    if not sentences:
        return ""
    if sentences[0].endswith("?") or len(sentences) == 1:
        return sentences[0]
    if sentences[1].rstrip("\"”’)").endswith("?") or len(sentences[0]) < 60:
        return " ".join(sentences[:2])
    return sentences[0]


def read_lanes():
    """Lane -> (what checks it, done means), from the table in AGENTS.md section 4."""
    try:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        section = re.search(r"^## 4\. Lanes\s*$(.*?)(?=^## )", text, re.M | re.S).group(1)
        lanes = {}
        for line in section.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 3:
                name = cells[0].strip("` ").lower()
                if name in LANES:
                    lanes[name] = (cells[1], cells[2])
        if set(lanes) == set(LANES):
            return lanes
    except (OSError, AttributeError):
        pass
    print("  could not read the lanes table from AGENTS.md; using built-in text", file=sys.stderr)
    return dict(LANE_FALLBACK)


def read_spending():
    """(number of paid runs, total USD) from SPENDING.md."""
    runs, total = 0, 0.0
    try:
        for line in (ROOT / "SPENDING.md").read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if line.strip().startswith("|") and len(cells) >= 4 and re.match(r"^\d{4}-\d{2}-\d{2}", cells[0]):
                m = re.search(r"[\d.]+", cells[3].replace(",", ""))
                if m:
                    runs, total = runs + 1, total + float(m.group(0))
    except OSError:
        pass
    return runs, total


def load_snapshot():
    try:
        data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        return {int(k): v for k, v in data.get("issues", {}).items()}
    except (OSError, ValueError):
        return {}


def write_snapshot(issues):
    data = {
        "note": "Fallback copy of issue titles and text, used only when GitHub cannot be reached at build time. "
                "Refresh with: python3 scripts/build_site.py --snapshot. Labels (status) are never stored here.",
        "retrieved": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        "issues": {str(k): {"title": v["title"], "body": v["body"]} for k, v in sorted(issues.items())},
    }
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------------------------------------------
# Pieces of pages
# --------------------------------------------------------------------------------------------------------------

def lane_tag(lane, label=None):
    shape = LANE_SHAPES.get(lane, '<circle cx="6" cy="6" r="2.5"/>')
    return ('<span class="lane"><svg class="lane-mark" viewBox="0 0 12 12" width="12" height="12" fill="currentColor" '
            'aria-hidden="true" focusable="false">%s</svg>%s</span>' % (shape, esc(label or lane)))


def status_pill(status):
    return '<span class="pill pill-%s"><span class="dot" aria-hidden="true"></span>%s</span>' % (
        status, esc(status.capitalize()))


def issue_url(q):
    return "%s/issues/%d" % (REPO_URL, q["number"])


def autolink_claims(md):
    """Link Aletheia claim IDs (for example ORCH-C040) to their atlas pages."""
    return re.sub(r"(?<![\w\[/-])([A-Z]{2,5}-C\d{3})(?![\w\]])", lambda m: "[%s](%s)" % (
        m.group(1), ATLAS_CLAIM_URL.format(m.group(1))), md)


def fmt_date(iso):
    try:
        d = datetime.date.fromisoformat(iso)
        return "%d %s %d" % (d.day, d.strftime("%B"), d.year)
    except (TypeError, ValueError):
        return iso


def current_stage(q):
    stages = q.get("stages") or []
    for st in stages:
        if st["state"] == "current":
            return st
    return next((st for st in stages if st["state"] == "todo"), None)


def index_row(q, root):
    href = "%squestions/%s/" % (root, q["slug"])
    extra = ""
    st = current_stage(q)
    if q["status"] == "active" and st:
        bars = "".join('<i class="is-%s"></i>' % s["state"] for s in q["stages"])
        extra = ('<p class="q-progress"><span class="mini" aria-hidden="true">%s</span>'
                 '<span>Stage %s · %s · %s</span></p>' % (bars, esc(st["num"]), inline(st["title"]),
                                                          esc(st["status_text"])))
    if q["meta"].get("result"):
        # The outcome in a sentence or two, from the content file's "result:" line, so nobody has to open the page.
        verdict = q["meta"].get("verdict")
        extra += ('<div class="q-result"><p class="label">%s</p>%s<p class="q-result-text">%s</p></div>' % (
            "Result" if q["status"] == "done" else "Result so far",
            '<p class="q-verdict">%s</p>' % inline(verdict) if verdict else "", inline(q["meta"]["result"])))
    return (
        '<li class="q-row" data-lane="%s" data-status="%s">'
        '<span class="q-num">#%d</span>'
        '<div class="q-main"><h4 class="q-title"><a href="%s">%s</a></h4>%s%s</div>'
        '<div class="q-meta">%s%s<a class="q-issue" href="%s">Issue #%d<span class="sr"> on GitHub</span> '
        '<span aria-hidden="true">↗</span></a></div></li>' % (
            esc(q["lane"]), q["status"], q["number"], href, inline(q["title"]),
            '<p class="q-gist">%s</p>' % inline(q["gist"]) if q["gist"] else "", extra,
            lane_tag(q["lane"]), status_pill(q["status"]), issue_url(q), q["number"]))


def render_index(questions, intro, lanes, root):
    legend = "".join('<li data-lane="%s" title="Checked by: %s">%s</li>' % (lane, esc(plain(lanes[lane][0])),
                                                                           lane_tag(lane)) for lane in LANES)
    out = ['<div class="index-head"><div><h2 id="questions-h" class="section-title">Questions</h2>',
           '<p class="index-note">%s</p></div>' % inline(intro),
           '<div class="legend-wrap"><p class="label">Lanes <a href="%show-it-works/#lanes">what they mean</a></p>'
           '<ul class="legend" data-lane-filter>%s</ul></div></div>' % (root, legend),
           '<p class="sr" aria-live="polite" data-filter-status></p>']
    for status, label in GROUPS:
        group = [q for q in questions if q["status"] == status]
        if not group:
            if status == "active":
                out.append('<div class="q-group is-active"><h3 class="label">Now running</h3>'
                           '<p class="q-empty">No question is active right now.</p></div>')
            continue
        out.append('<div class="q-group is-%s"><h3 class="label">%s <span class="count">%d</span></h3>'
                   '<ul class="q-list" role="list">%s</ul></div>' % (
                       status, label, len(group), "".join(index_row(q, root) for q in group)))
    return "\n".join(out)


def band_head(q, root, dek_html, extra=""):
    updated = q.get("meta", {}).get("updated")
    kicker = ['<span class="kicker">Question #%d</span>' % q["number"], lane_tag(q["lane"], q["lane"] + " lane")]
    if updated:
        kicker.append('<span class="kicker-faint">Updated <time datetime="%s">%s</time></span>' % (
            esc(updated), esc(fmt_date(updated))))
    return (
        '<div class="band"><div class="wrap band-inner">'
        '<nav class="crumbs" aria-label="Breadcrumb"><a href="%s#questions">Questions</a>'
        '<span aria-hidden="true"> / </span><span aria-current="page">#%d</span></nav>'
        '<p class="kicker-row">%s</p><h1 class="display">%s</h1>%s'
        '<p class="pills">%s<a class="issue-link" href="%s">Issue #%d on GitHub <span aria-hidden="true">↗</span></a>'
        '</p>%s</div></div>' % (root, q["number"], "".join(kicker), inline(q["title"]), dek_html,
                                status_pill(q["status"]), issue_url(q), q["number"], extra))


def pager(prev_q, next_q, root):
    def one(q, cls, label):
        if not q:
            return '<span class="%s"></span>' % cls
        return ('<a class="%s" href="%squestions/%s/"><span class="label">%s · #%d</span>'
                '<span class="pager-title">%s</span></a>' % (cls, root, q["slug"], label, q["number"],
                                                              inline(q["title"])))
    return '<nav class="wrap pager-wrap" aria-label="More questions"><div class="pager">%s%s</div></nav>' % (
        one(prev_q, "prev", "Previous"), one(next_q, "next", "Next"))


def short_page(q, lanes, root):
    f = q["fields"]
    question = f.get("Question") or ""
    dek = '<p class="dek">%s</p>' % inline(question) if question else ""
    if q["caveat"]:
        dek += ('<p class="origin"><span class="pill pill-unverified">Unverified</span>'
                '<span class="origin-text">%s</span></p>' % inline(q["caveat"]))
    head = band_head(q, root, dek)
    check = f.get("What would check it")
    done_means = lanes.get(q["lane"], ("", ""))[1].replace("<slug>", q["slug"])
    panel = ""
    if check or done_means:
        cols = []
        if check:
            cols.append('<div><p class="label">What would check it</p><p>%s</p></div>' % inline(check))
        if done_means:
            cols.append('<div><p class="label">Done, in the %s lane, means</p><p>%s</p></div>' % (
                esc(q["lane"]), inline(done_means)))
        panel = '<div class="panel split">%s</div>' % "".join(cols)
    facts = [("Status", '%s <span class="fact-note">%s</span>' % (status_pill(q["status"]),
                                                                  esc(STATUS_TEXT[q["status"]])))]
    checked_by = lanes.get(q["lane"], ("", ""))[0]
    facts.append(("Lane", '%s <span class="fact-note">Checked by: %s</span>' % (lane_tag(q["lane"]),
                                                                                 inline(checked_by))))
    for key in ("Aletheia link", "Budget", "Done when", "First step"):
        val = f.get(key, "").strip()
        if val and val not in ("—", "-"):
            facts.append((key, inline(autolink_claims(val) if key == "Aletheia link" else val)))
    folder_label = next((k for k in f if k.lower().startswith("folder")), "Folder")
    facts.append((folder_label, "<code>questions/%s/</code>" % esc(q["slug"])))
    rows = "".join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(k), v) for k, v in facts)
    if not f:
        rows += ('<div><dt>Issue text</dt><dd>Not available at build time. Read it on '
                 '<a href="%s">GitHub</a>.</dd></div>' % issue_url(q))
    body = ('<div class="wrap"><div class="short">%s<dl class="facts">%s</dl>'
            '<p class="follow">The issue is where this question is discussed and tracked: '
            '<a href="%s">issue #%d on GitHub</a>.</p></div></div>' % (panel, rows, issue_url(q), q["number"]))
    return head + body


def rich_page(q, root):
    doc = Doc()
    article = render_doc(q["content"], doc)
    meta = q["meta"]
    dek = '<p class="dek">%s</p>' % inline(meta.get("dek") or q["gist"]) if (meta.get("dek") or q["gist"]) else ""
    track = render_track(q["stages"]) if q["stages"] else ""
    head = band_head(q, root, dek, track)
    subnav = ""
    if doc.outline:
        # On a phone the list is one line that scrolls sideways (site.css), so keep the labels short.
        subnav = ('<nav class="subnav" aria-label="On this page"><div class="wrap"><ul>%s</ul></div></nav>' % "".join(
            '<li><a href="#%s">%s</a></li>' % (hid, esc(text)) for hid, text in doc.outline))
    return subnav + head + '<div class="wrap"><article class="prose">%s</article></div>' % article


# --------------------------------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------------------------------

def template(name):
    return (SITE / "templates" / name).read_text(encoding="utf-8")


def fill(tpl, **ctx):
    def sub(m):
        key = m.group(1)
        if key not in ctx:
            raise KeyError("template placeholder {{%s}} has no value" % key)
        return str(ctx[key])
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", sub, tpl)


def short_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:10]


class Site:
    def __init__(self, status_note, built):
        self.base = template("base.html")
        self.status_note = status_note
        self.built = built
        self.css_v = short_hash(SITE / "assets" / "site.css")
        self.js_v = short_hash(SITE / "assets" / "site.js")
        self.pages = []

    def write(self, rel, title, description, body, root, nav="", card="default", card_alt=""):
        # The share image is site/assets/cards/<card>.png (made by scripts/make_cards.py), or the default one.
        if not (CARDS / (card + ".png")).exists():
            card, card_alt = "default", ""
        image = CARDS / (card + ".png")
        image_url = "%s%sassets/cards/%s.png?v=%s" % (SITE_ORIGIN, BASE_PATH, card, short_hash(image))
        page_url = SITE_ORIGIN + BASE_PATH + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
        page = fill(
            self.base, title=esc(title), description=esc(description), root=root, body=body,
            image_url=esc(image_url), page_url=esc(page_url),
            image_alt=esc(card_alt or "Aletheia Lab: AI experiments on big open questions."),
            nav_questions=' aria-current="page"' if nav == "questions" else "",
            nav_how=' aria-current="page"' if nav == "how" else "",
            css_v=self.css_v, js_v=self.js_v, status_note=esc(self.status_note), built=esc(self.built),
            repo_url=REPO_URL, atlas_url=ATLAS_URL)
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page, encoding="utf-8")
        self.pages.append(rel)


def main(argv):
    offline = "--offline" in argv or os.environ.get("SITE_OFFLINE") == "1"
    print("Building the lab site into %s" % OUT.relative_to(ROOT), flush=True)
    intro, questions = read_questions()
    live, source = fetch_issues(offline)
    if "--snapshot" in argv:
        if live:
            write_snapshot(live)
            print("  wrote %s" % SNAPSHOT.relative_to(ROOT))
        else:
            print("  --snapshot: GitHub unreachable; snapshot left unchanged", file=sys.stderr)
    snapshot = load_snapshot()
    lanes = read_lanes()
    runs, spent = read_spending()

    for q in questions:
        issue = (live or {}).get(q["number"]) or {}
        labels = issue.get("labels") or []
        status = next((lab.split(":", 1)[1] for lab in labels if lab.startswith("status:")), "proposed")
        q["status"] = status if status in STATUS_TEXT else "proposed"
        lane = next((lab.split(":", 1)[1] for lab in labels if lab.startswith("lane:")), None)
        if lane in LANES:
            q["lane"] = lane
        if issue.get("title"):
            q["title"] = issue["title"]
        body = issue.get("body") or (snapshot.get(q["number"]) or {}).get("body", "")
        q["fields"], note = parse_issue_body(body or "")
        q["caveat"] = brainstorm_caveat(note)
        content_path = SITE / "content" / (q["slug"] + ".md")
        q["meta"], q["content"], q["stages"] = {}, None, []
        if content_path.exists():
            q["meta"], q["content"] = front_matter(content_path.read_text(encoding="utf-8"))
            q["stages"] = find_stages(q["content"])
        q["gist"] = q["meta"].get("summary") or gist(q["fields"].get("Question", ""))

    if live:
        status_note = "Statuses read from GitHub at build time"
    else:
        status_note = "Statuses could not be read from GitHub at build time, so every status shows as proposed"
    print("  issues: %s" % (source if live else source + " (statuses default to proposed; text from snapshot)"))
    built = os.environ.get("SOURCE_DATE_EPOCH")
    built_dt = (datetime.datetime.fromtimestamp(int(built), datetime.timezone.utc) if built
                else datetime.datetime.now(datetime.timezone.utc))
    site = Site(status_note, fmt_date(built_dt.strftime("%Y-%m-%d")))

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SITE / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # Home
    order = {s: k for k, (s, _) in enumerate(GROUPS)}
    ordered = sorted(questions, key=lambda q: (order[q["status"]], q["number"]))
    counts = {s: sum(1 for q in questions if q["status"] == s) for s, _ in GROUPS}
    stats = ('<p class="stats"><a href="./how-it-works/">How the lab works <span aria-hidden="true">→</span></a>'
             '<span>%d questions · %d active · %d done · %d lanes</span></p>' % (
                 len(questions), counts["active"], counts["done"], len(LANES)))
    home = fill(template("home.html"), stats=stats, index=render_index(ordered, intro, lanes, "./"),
                atlas_url=ATLAS_URL)
    site.write("index.html", "Aletheia Lab — experiments on big open questions",
               "Aletheia Lab runs AI experiments on big open questions. Each experiment's plan is locked before any "
               "result exists, and null results are published like any other.", home, "./", nav="questions")

    # Questions, in issue order for previous/next
    by_number = sorted(questions, key=lambda q: q["number"])
    for k, q in enumerate(by_number):
        root = "../../"
        body = rich_page(q, root) if q["content"] else short_page(q, lanes, root)
        body += pager(by_number[k - 1] if k else None, by_number[k + 1] if k + 1 < len(by_number) else None, root)
        site.write("questions/%s/index.html" % q["slug"], "%s · Aletheia Lab" % plain(q["title"]),
                   plain(q["gist"]) or plain(q["title"]), body, root, card=q["slug"],
                   card_alt=q["meta"].get("card_alt", ""))

    # How it works
    lane_rows = "".join(
        '<div class="lane-row" id="lane-%s"><div class="lane-name">%s</div><div><p class="label">What checks it</p>'
        '<p>%s</p></div><div><p class="label">Done means</p><p>%s</p></div></div>' % (
            lane, lane_tag(lane), inline(lanes[lane][0]), inline(lanes[lane][1])) for lane in LANES)
    if runs:
        spend = "%d paid run%s logged so far, %s in all." % (runs, "" if runs == 1 else "s", "${:,.2f}".format(spent))
    else:
        spend = "No paid runs are logged yet."
    blocks_ctx = {
        "lanes": '<div class="lanes">%s</div>' % lane_rows,
        "spending": '<p class="spend"><span class="label">From SPENDING.md at build time</span> %s '
                    '<a href="%s/blob/main/SPENDING.md">The log</a></p>' % (esc(spend), REPO_URL),
    }
    meta, md = front_matter((SITE / "pages" / "how-it-works.md").read_text(encoding="utf-8"))
    doc = Doc(blocks_ctx)
    article = blocks(md, doc)
    how = ('<div class="wrap"><div class="page-head"><p class="kicker">%s</p><h1 class="display">%s</h1>'
           '<p class="dek">%s</p></div><article class="prose">%s</article></div>' % (
               esc(meta.get("kicker", "")), esc(meta.get("title", "How the lab works")), inline(meta.get("dek", "")),
               article))
    site.write("how-it-works/index.html", "How the lab works · Aletheia Lab", plain(meta.get("dek", "")), how, "../",
               nav="how")

    # 404: served at any path, so its links start from the site's absolute base path.
    notfound = ('<div class="wrap"><div class="page-head"><p class="kicker">404</p><h1 class="display">'
                'Nothing is here.</h1><p class="dek">The page may have moved. The questions are on the '
                '<a href="%s">home page</a>.</p></div></div>' % esc(BASE_PATH))
    site.write("404.html", "Not found · Aletheia Lab", "Page not found.", notfound, esc(BASE_PATH))

    print("  wrote %d pages" % len(site.pages))
    print("  preview: python3 -m http.server -d %s 8000" % OUT.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
