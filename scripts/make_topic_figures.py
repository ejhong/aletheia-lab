#!/usr/bin/env python3
"""Draw the figures for the topic pages from the questions' own results files. Standard library only.

    python3 scripts/make_topic_figures.py        # writes site/figures/topic-<slug>/*.html

A topic page (site/topics/<slug>.md) includes them with {{figure: topic-<slug>/<name>}}. The numbers in the timeline
come from the results files named below; the words in the scorecards are written here and must be kept in step with
each question's RESULTS.md when a result changes.
"""
import csv
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
Q = ROOT / "questions"
FIG = ROOT / "site" / "figures"
esc = lambda s: html.escape(str(s), quote=True)


def figure(folder, name, title, svg, caption, legend=""):
    (FIG / folder).mkdir(parents=True, exist_ok=True)
    (FIG / folder / f"{name}.html").write_text(
        f'<figure class="fig" aria-label="{esc(title)}">\n{legend}<div class="fig-scroll">\n{svg}\n</div>\n'
        f'<figcaption>{caption}</figcaption>\n</figure>\n')


def tiles(folder, items):
    (FIG / folder).mkdir(parents=True, exist_ok=True)
    (FIG / folder / "tiles.html").write_text('<div class="tiles">\n' + "\n".join(
        f'<div class="tile"><p class="tile-value{" is-word" if word else ""}">{esc(v)}</p><p class="tile-label">{esc(l)}</p></div>'
        for v, l, word in items) + "\n</div>\n")


def scorecard(folder, name, label, heads, rows):
    """A table of studies: what was predicted or claimed, what was found, and a short verdict with a mark.

    rows: (issue number, slug, mark, prediction, finding, chip, verdict, kind). kind sets the chip's glyph:
    'no' (hollow), 'partly' (half), 'yes' (full) or 'open' (dashed).
    """
    out = [f'<div class="score" role="table" aria-label="{esc(label)}">',
           '<div class="score-head" role="row">' + "".join(f'<span role="columnheader">{esc(h)}</span>' for h in heads) + "</div>"]
    for number, slug, mark, predicted, found, chip, verdict, kind in rows:
        out.append(
            f'<div class="score-row" role="row">'
            f'<div class="score-mark" role="cell"><p class="score-num">#{number}</p>'
            f'<p class="score-title"><a href="../../questions/{slug}/">{esc(mark)}</a></p>'
            f'<p class="score-chip is-{kind}"><span class="score-glyph" aria-hidden="true"></span>{esc(chip)}</p>'
            f'<p class="score-verdict">{esc(verdict)}</p></div>'
            f'<p class="score-cell" role="cell" data-head="{esc(heads[1])}">{esc(predicted)}</p>'
            f'<p class="score-cell" role="cell" data-head="{esc(heads[2])}">{esc(found)}</p></div>')
    out.append("</div>")
    (FIG / folder).mkdir(parents=True, exist_ok=True)
    (FIG / folder / f"{name}.html").write_text("\n".join(out) + "\n")


# ---------------------------------------------------------------------------------------------------------------------
# The Younger Dryas
# ---------------------------------------------------------------------------------------------------------------------
ONSET = 12896          # years before 2000 CE: the published start of the cold (Rasmussen et al. 2014)


def yd_timeline():
    """Four records on one clock: years before and after the start of the cold, in Greenland ice."""
    shape = json.load(open(Q / "yd-cooling-shape" / "results" / "summary.json"))["profiles"]["ngrip_d18o_60ka"]
    pt = json.load(open(Q / "yd-platinum-volcanism" / "results" / "summary.json"))
    eruptions = [(ONSET - e["age_b2k"], e["dep_kg_km2"]) for e in pt["part2_volcanism"]["eruptions_around_yd_gl"]]
    plat = pt["part1_platinum"]["svensson2020_gicc05"]
    p0, p1 = ONSET - plat["age_onset_b2k"], ONSET - plat["age_end_b2k"]
    amm = sorted((int(r["bin_starts_years_after_onset"]), float(r["mean"]))
                 for r in csv.DictReader(open(Q / "cooling-ammonium" / "results" / "profiles.tsv"), delimiter="\t")
                 if r["ion"] == "ammonium" and r["core"] == "NGRIP" and r["event"] == "GS-1")
    LO, HI = -200, 300
    W, left, right, top, ph, gap = 720, 132, 700, 34, 92, 30
    H = top + 3 * ph + 2 * gap + 46
    sx = lambda t: left + (t - LO) / (HI - LO) * (right - left)
    y0 = [top + i * (ph + gap) for i in range(3)]
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Eruptions, cold, platinum and ammonium in Greenland ice, '
         f'from 200 years before the Younger Dryas began to 300 years after" xmlns="http://www.w3.org/2000/svg">']
    # the platinum layer and the onset run through all three panels
    o.append(f'<rect class="c-band c-plat" x="{sx(p0):.1f}" y="{top - 6}" width="{sx(p1) - sx(p0):.1f}" height="{H - top - 40}"/>')
    names = [("Large eruptions", "sulphate left on Greenland"), ("Greenland cold", "oxygen isotopes in the ice; lower is colder"),
             ("Ammonium", "from fires, soils and plants")]
    for i, (name, sub) in enumerate(names):
        o.append(f'<text class="c-group" x="0" y="{y0[i] + 12}">{name}</text>')
        for j, line in enumerate(wrap(sub, 20)):
            o.append(f'<text class="c-sub" x="0" y="{y0[i] + 29 + 14 * j}">{line}</text>')
        o.append(f'<line class="c-zero" x1="{left}" x2="{right}" y1="{y0[i] + ph}" y2="{y0[i] + ph}"/>')
    # 1. eruptions as sticks
    top_dep = max(d for t, d in eruptions if LO <= t <= HI)
    for t, d in eruptions:
        if LO <= t <= HI:
            h = d / top_dep * (ph - 16)
            when = f"{abs(t):.0f} years {'before' if t < 0 else 'after'} the cold began"
            o.append(f'<g class="c-mark" tabindex="0" data-tip="{esc(f"Eruption, {when}|{d:.0f} kg of sulphate per square kilometre")}">'
                     f'<rect class="c-hit" x="{sx(t) - 7:.1f}" y="{y0[0]}" width="14" height="{ph}"/>'
                     f'<rect class="c-bar{" is-on" if -150 <= t < 0 else ""}" x="{sx(t) - 2.5:.1f}" y="{y0[0] + ph - h:.1f}" width="5" height="{h:.1f}" rx="2"/></g>')
    # 2. the cold: this cooling against the usual run of the others
    T = shape["tau_mid_yr"]
    keep = [k for k, t in enumerate(T) if LO <= t <= HI]
    lo_v = min(min(shape["target"][k], shape["q25_others"][k]) for k in keep)
    hi_v = max(max(shape["target"][k], shape["q75_others"][k]) for k in keep)
    sy1 = lambda v: y0[1] + 6 + (hi_v - v) / (hi_v - lo_v) * (ph - 12)
    band = " L".join(f"{sx(T[k]):.1f},{sy1(shape['q75_others'][k]):.1f}" for k in keep) + " L" + " L".join(
        f"{sx(T[k]):.1f},{sy1(shape['q25_others'][k]):.1f}" for k in reversed(keep))
    o.append(f'<path class="c-area-ctx" d="M{band} Z"/>')
    for cls, key in (("c-line-ctx", "median_others"), ("c-line", "target")):
        path = " L".join(f"{sx(T[k]):.1f},{sy1(shape[key][k]):.1f}" for k in keep)
        o.append(f'<path class="{cls}" d="M{path}"/>')
    for k in keep:
        tip = esc(f"{bin_words(T[k] - 10, 20)}|Younger Dryas {shape['target'][k]:+.1f}‰, the usual cooling {shape['median_others'][k]:+.1f}‰")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{sx(T[k] - 10):.1f}" y="{y0[1]}" width="{sx(20) - sx(0):.1f}" height="{ph}"/></g>')
    # 3. ammonium in 20-year steps
    pts = [(t + 10, v) for t, v in amm if LO <= t + 10 <= HI]
    top_a = max(v for _, v in pts) * 1.08
    sy2 = lambda v: y0[2] + ph - v / top_a * ph
    before = [v for t, v in amm if -100 <= t < 0]
    base = sum(before) / len(before)
    o.append(f'<line class="c-tickmark" x1="{left}" x2="{right}" y1="{sy2(base):.1f}" y2="{sy2(base):.1f}" stroke-dasharray="3 4"/>')
    o.append(f'<text class="c-sub" x="{left + 4}" y="{sy2(base) + 13:.1f}">level in the century before</text>')
    path = " L".join(f"{sx(t):.1f},{sy2(v):.1f}" for t, v in pts)
    o.append(f'<path class="c-line" d="M{path}"/>')
    for t, v in pts:
        tip = esc(f"{bin_words(t - 10, 20)}|ammonium {v:.0f} µg/kg, {v / base:.1f} times the century before")
        o.append(f'<g class="c-mark" tabindex="0" data-tip="{tip}"><rect class="c-hit" x="{sx(t - 10):.1f}" y="{y0[2]}" width="{sx(20) - sx(0):.1f}" height="{ph}"/></g>')
    # the onset line, the labels and the clock
    o.append(f'<line class="c-onset" x1="{sx(0):.1f}" x2="{sx(0):.1f}" y1="{top - 10}" y2="{y0[2] + ph}"/>')
    o.append(f'<text class="c-label-sm" x="{sx(0) - 6:.1f}" y="{top - 14}" text-anchor="end">the cold begins</text>')
    o.append(f'<text class="c-label-sm" x="{sx(p0):.1f}" y="{top - 14}">platinum layer</text>')
    for t in range(LO, HI + 1, 100):
        label = "0" if t == 0 else f"{abs(t)} {'before' if t < 0 else 'after'}"
        anchor = "start" if t == LO else "end" if t == HI else "middle"
        o.append(f'<text class="c-tick" x="{sx(t):.1f}" y="{y0[2] + ph + 16}" text-anchor="{anchor}">{label}</text>')
    o.append(f'<text class="c-axis" x="{left}" y="{H - 6}">Years before and after the published start of the Younger Dryas cold, 12,896 years before 2000 CE.</text>')
    o.append("</svg>")
    legend = ('<p class="fig-legend"><span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="var(--copper)" stroke-width="2"/></svg>'
              ' The Younger Dryas</span><span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><rect x="0" y="1" width="16" height="10" fill="var(--faint)" opacity=".25"/>'
              '<line x1="0" x2="16" y1="6" y2="6" stroke="var(--faint)" stroke-width="2"/></svg> Eighteen other sudden coolings (middle and middle half)</span>'
              '<span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><rect x="3" y="0" width="10" height="12" fill="var(--copper)" opacity=".2"/></svg> The platinum layer</span></p>\n')
    figure("topic-younger-dryas", "timeline", "The order of events in Greenland ice around the start of the Younger Dryas", "\n".join(o),
           "Four records from Greenland ice on one clock. Four eruptions, two of them very large, come in the 150 years before the cold begins, "
           f"the last about twenty years before. The cold then sets in more slowly than at most other sudden coolings. The platinum arrives about "
           f"{p0:.0f} years in, and the ammonium climbs after that. Nothing in the ice marks a single instant when everything changed. "
           "Eruptions and platinum are placed by tie points between ice cores, good to about ten years. Hover or focus for the numbers.", legend)


def wrap(text, width):
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def bin_words(start, width):
    a, b = start, start + width
    if b <= 0:
        return f"{-b:.0f} to {-a:.0f} years before the cold began"
    if a >= 0:
        return f"{a:.0f} to {b:.0f} years after the cold began"
    return "the years around the start of the cold"


def younger_dryas():
    tiles("topic-younger-dryas", [
        ("14", "studies, each with its test fixed before the data were looked at", False),
        ("0", "found the fires, the darkened sky or the sudden cold that the hypothesis says followed", False),
        ("4", "eruptions, two of them very large, in the 150 years before the cold: among the heaviest runs in 51,000 years", False),
        ("Still open", "whether anything fell at all: the microscopic grains in the claimed layer, which only laboratories can test", True)])
    scorecard("topic-younger-dryas", "scorecard", "What each study tested and found",
              ["The mark", "If a comet did it", "What the record shows"], [
        (43, "ice-core-fire", "Smoke in Greenland's ice", "A burst of fire chemicals at the moment the cold begins.",
         "A real, century-long rise in ammonium in three ice cores. It starts 30 to 40 years after the cold and builds slowly.",
         "Partly", "Unusual, but late and slow", "partly"),
        (60, "cooling-ammonium", "Is that rise a one-off?", "Nothing like it after the ice age's other sudden coolings.",
         "Ammonium rises after most of 24 other coolings. The Younger Dryas rise is 2nd and 3rd largest of 25, in two cores.",
         "Partly", "The strong end of a common pattern", "partly"),
        (69, "yd-global-burn", "A burn across the planet", "A jolt in the carbon of the whole atmosphere, and charcoal worldwide.",
         "The shift in Antarctic air is small, late and matched at other cold spells. The best-dated charcoal records show no peak.",
         "Not found", "No sign of a global burn", "no"),
        (75, "yd-cooling-shape", "The cooling itself", "A cooling sharper, deeper or more worldwide than the natural ones.",
         "It began more slowly than 16 of 18 other coolings, reached an ordinary depth, and Antarctica did not cool.",
         "Not found", "An ordinary cooling, slow to start", "no"),
        (76, "yd-platinum-volcanism", "Platinum in the ice", "The platinum layer at or just before the start of the cold.",
         "It lies about 20 to 30 years after the cold began, though before the steepest fall. Four eruptions, two very large, came just before the cold.",
         "Unclear", "Platinum a little late; eruptions unusually heavy", "open"),
        (120, "yd-platinum-fingerprint", "Chemistry of the platinum", "Where all six platinum-group elements were measured, they stand in a meteorite's proportions, as in the layer left by the asteroid that ended the dinosaurs.",
         "At two sites, 23 of 27 samples look like ordinary crust or rhenium-rich mud and 4 lean towards the impact pattern. The largest spikes are not at the boundary. A small cosmic share is not ruled out.",
         "Unclear", "Mostly not an impact layer's chemistry", "open"),
        (100, "tunguska-calibration", "What one airburst leaves", "The one known airburst, Tunguska in 1908, marks the ice in the way the Younger Dryas ice is marked.",
         "Across Greenland 1908 is an ordinary year for ammonium. At some sites there is a sharp, sooty spike, at others nothing. The Younger Dryas century has a steady rise and few spikes.",
         "Not found", "A spike where it shows, not a steady rise", "no"),
        (114, "yd-neem-spikes", "Fire spikes in a second core", "A century of repeated fires fills a second Greenland core with many more big smoke plumes. (A version we built ourselves; the authors describe one day.)",
         "The rise in ammonium is a raised background, 2.6 times the level before. Years with a big plume: 18 after the cold began, 14 before. No tripling of fires; a modest rise is not ruled out.",
         "Not found", "Raised background; no surge of big plumes", "no"),
        (103, "taurid-swarm", "A swarm in the Taurid stream", "The stream the Earth crosses each autumn still carries a swarm of large fragments of the broken comet.",
         "No sign of one among today's asteroids or in 32 years of airbursts seen by satellite. Seventeen large asteroids do line up with the comet, as was known in 2010; smaller ones do not.",
         "Not found", "No swarm of large fragments today", "no"),
        (121, "yd-cosmic-dust-he3", "Comet dust in ocean mud", "A comet breaking up over thousands of years surrounds the Earth with fine dust, and helium-3 in sea-floor mud rises. (This cannot see a single day.)",
         "No rise across 20,000 to 10,000 years ago in nine cores: the usual amount or slightly less. Solid for thousands of years; one core's evidence for centuries. One of three checks on the method failed.",
         "Unclear", "No long dust cloud; one check on the method failed", "open"),
        (116, "yd-megafauna-timing", "The great animals", "In the 2007 version the animals die at the strike. The authors now say a blow at the onset, with losses over centuries.",
         "Dung spores were already falling in most lake cores. Dated bones fall steeply as the cold begins, and ten well-dated animals lived 200 to 1,900 years on.",
         "Partly", "Not sudden; a steep fall at the onset", "partly"),
        (113, "ydb-site-synchrony", "Are the layers the same age?", "Radiocarbon dates from the claimed layers agree on one age.",
         "The precise dates do not agree, though charcoal older than its layer could explain that. Only 4 of 32 sites have a tight date on the layer itself.",
         "Unclear", "Dates disagree; most sites too loosely dated", "open"),
        (127, "yd-retracted-plos-audit", "Two retracted papers, checked", "Two papers from 2025 give new evidence of the layer: comet dust in Baffin Bay mud, and shocked quartz at three sites.",
         "Dated as the paper itself describes, the Baffin Bay layers are 300 to 610 years too young. The quartz paper cannot show its grains belong to one layer of one age. Nobody has faulted the grains themselves.",
         "Unclear", "One paper's dates fail; the quartz grains are untested", "open"),
        (40, "younger-dryas-crash", "A crash in human numbers", "Dated traces of people thin out at once, above all in North America.",
         "No drop on three continents. But radiocarbon dating is at its most distorted in exactly those centuries.",
         "Not found", "No sign, though the test was blurred", "no")])
    yd_timeline()


# ---------------------------------------------------------------------------------------------------------------------
# Minds and machines
# ---------------------------------------------------------------------------------------------------------------------
def minds():
    tiles("topic-minds-and-machines", [
        ("2", "famous arguments about minds, written out in Lean 4 and checked line by line", False),
        ("68", "statements fixed in advance, read by outside models, then proved", False),
        ("1", "assumption carries each argument once it is written out in full", False),
        ("Both smaller", "than their slogans: each proves something real, and less than is claimed for it", True)])
    scorecard("topic-minds-and-machines", "scorecard", "What each study tested and found",
              ["The claim", "What it says", "What we found"], [
        (19, "godel-argument", "Penrose and Gödel", "Gödel's theorem shows that human mathematical insight is not the work of any machine.",
         "If your mind were a particular machine, you could not also know that machine to be reliable. That much is proved. It does not follow that the mind is no machine: a machine can be reliable without being able to know it.",
         "Partly holds", "The modest conclusion is proved; the proof of the strong one fails", "partly"),
        (66, "unfolding-argument", "The unfolding argument", "Any system with feedback loops has a loop-free twin that behaves the same, so a theory tying consciousness to loops is false or untestable.",
         "The twin exists for an experiment of fixed length, and needs one more part for every further step. With no limit on time there is no twin. All of it rests on behaviour being the only evidence about consciousness.",
         "Partly holds", "Valid for experiments of fixed length only", "partly"),
        (48, "anaesthetics-microtubules", "Anaesthetics and microtubules", "Anaesthetics switch consciousness off by settling into pockets in the microtubules of nerve cells.",
         "A computer fit of 35 gases into eight proteins shows nothing special about the microtubule protein. But it shows nothing special about the accepted targets either, and an unrelated protein does as well as any. The scores follow the size of the molecule.",
         "Could not tell", "The method cannot pick out any anaesthetic target", "open"),
        (115, "anaesthetics-terahertz", "The vibration in the microtubule protein", "A 2017 calculation found that anaesthetics slow a vibration in the microtubule protein, while look-alike gases that cause no anaesthesia speed it up.",
         "Rebuilt and run on nine targets, the calculation gives that split for egg-white protein and for rings placed at random: it follows the size of the gas molecule. Scored the paper's own way, anaesthetics do stand out on the microtubule protein, but just as much on a known anaesthetic target and on a blood protein.",
         "Not special to microtubules", "The calculation gives no reason to pick out microtubules", "no")])


def deep_memory():
    tiles("topic-deep-memory", [
        ("3", "tests of a shared past that do not depend on stories: two in ancient DNA, one in the sky", False),
        ("12,977", "ancient people searched for anyone buried on the wrong side of an ocean; none unexplained", False),
        ("After 201 BCE", "the date read from the empty patch in the classical sky: that of the catalogue's own makers", True),
        ("Still open", "the stories and images themselves, which the atlas weighs", True)])
    scorecard("topic-deep-memory", "scorecard", "What each study tested and found",
              ["The trace", "If there was a shared past", "What the record shows"], [
        (31, "population-y", "The Australasian signal in the Amazon", "The resemblance between some Amazonians and Australasians traces to a crossing of the Pacific.",
         "It is real and faint, and it leads back to mainland Asia tens of thousands of years ago. None of 58 groups of ancient Americans stands out for it.",
         "Not found", "Real, but not from across the Pacific", "no"),
        (41, "strangers", "Strangers in the record", "Somebody before Columbus lies buried on the wrong side of an ocean.",
         "Among 12,977 ancient people nobody does, apart from the medieval Norse of Greenland. The one person left unexplained was checked in her raw DNA, which points to modern contamination.",
         "Not found", "No strangers found", "no"),
        (85, "ancient-sky-hole", "The hole in the ancient sky", "The empty southern patch in the classical constellations is centred where the pole stood long before Babylon or Greece.",
         "It is centred where the pole stood for Hipparchus and Ptolemy, who compiled the catalogue. A sky of 3000 BCE fits far worse. But a catalogue's edge dates its last compilers, not the first people to draw the figures.",
         "Not found", "The hole dates the catalogue, not the constellations", "no"),
        (92, "gobekli-star-map", "The star map on a pillar", "The animals on Pillar 43 at Göbekli Tepe match constellations so well that chance is ruled out.",
         "Three vision models, shown the paper's pictures blind, could not match even the scorpion to its constellation, so they could not serve as judges. The paper's odds rest on its authors' own ranking, which nobody else has checked.",
         "Could not tell", "Blind machine judges were not up to it", "open")])
    (FIG / "topic-deep-memory" / "sky-plate.html").write_text(
        '<figure class="plate"><img src="../../assets/illustrations/ancient-skies.jpg" loading="lazy" width="1536" height="1024" '
        'alt="An engraving of a round chart of the southern sky, crowded with constellation figures around an empty circle at its centre, '
        'with an astronomer sighting from a rocky shore below.">'
        '<figcaption>An illustration made with an AI image model, for decoration. It is not evidence and is not a real star chart.</figcaption></figure>\n')


def mind_over_matter():
    tiles("topic-mind-over-matter", [
        ("58", "fresh events from 2016 to 2025, chosen by a rule and not by the experimenters", False),
        ("−1.83", "the combined score, where the project's own record predicts about +2.5", False),
        ("27 of 57", "events beat their matched ordinary day: no better than a coin", False),
        ("+6.08", "the combined score of 395 of the project's own events, recomputed from the raw data", True)])
    scorecard("topic-mind-over-matter", "scorecard", "What each test looked for and found",
              ["The claim", "If it were real", "What the data show"], [
        (47, "global-consciousness", "The random-number network", "Random-number devices around the world stray from chance on days of shared emotion.",
         "On 58 later events, scored with the project's own statistic, the network behaved as it does on ordinary days. Event days and control days cannot be told apart.",
         "Not found", "No effect on a fresh test", "no"),
        (74, "gcp-audit", "The original 500 events", "The project's published result for its own events follows from its public raw data, and is tied to those events.",
         "Recomputed from the raw data, 395 events match the published scores and add up to +6.08. The same hours a week away add up to −0.42. The numbers are right; how the events were chosen is the open question.",
         "Found", "The original result is in the data", "yes")])


def main():
    younger_dryas()
    minds()
    deep_memory()
    mind_over_matter()
    for folder in ("topic-younger-dryas", "topic-minds-and-machines", "topic-deep-memory", "topic-mind-over-matter"):
        print(folder + ":", ", ".join(sorted(p.name for p in (FIG / folder).iterdir())))


if __name__ == "__main__":
    main()
