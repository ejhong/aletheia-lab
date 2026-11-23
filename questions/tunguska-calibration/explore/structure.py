"""EXPLORATORY. Blind structure check of the downloaded ice-core files.

Run from the question folder:  python3 -I explore/structure.py [name-filter]

For each file it prints: header/metadata lines, column names, time span, rows per
decade and rows per year near the target window -- all computed from the AGE (or
depth) column only. It never prints a chemistry value from a row dated 1895-1920 CE:
any header line mentioning Tunguska or a year 1895-1920 is redacted, and the only
data rows it prints are the very first and last rows of a file, and only when their
age is known and outside 1880-1930. Standard library only. Reads files as data.
"""
import collections
import csv
import io
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, 'data')
BLIND = (1895, 1920)          # never show chemistry from these years
SHOW_OK = (1880, 1930)        # only show example rows outside this wider band
REDACT = re.compile(r'tunguska|(?<![0-9.])(189[5-9]|19[01][0-9]|1920)(?![0-9])', re.I)
MAX_HDR = 25

# file registry: (folder/file, format, how to get CE age)
#   format: 'noaa' (free text, whitespace), 'noaa-tab' (# comments, tab), 'pangaea' (/* */ then tab),
#           'csv', 'csv-skip6', 'xlsx'
#   age: ('col', name_or_index, unit)  unit in ce | bp | b2k | kab2k | kabp
#        ('mid', top, bottom, unit)    midpoint of two age columns
#        ('depthmap', depthcol, agefile, fmt, depthcol, agecol, unit)  depth -> CE by linear
#                                      interpolation in an age-depth file (NEGIS, NGRIP1 on GICC05)
#        None                          no age column (depth only)
FILES = [
    ('d4-mcconnell2007/d4-2007carbon.txt', 'noaa', ('col', 0, 'ce')),
    ('negis2012/negis2012age.txt', 'noaa-tab', ('col', 'age_AD', 'ce')),
    ('negis2012/negis2012chem.txt', 'noaa-tab',
     ('depthmap', 'depth_m', 'negis2012/negis2012age.txt', 'noaa-tab', 'depth_m', 'age_AD', 'ce')),
    ('gicc05-rasmussen2022/PANGAEA.943193.tab', 'pangaea', ('col', 0, 'b2k')),
    ('ngrip-ic/PANGAEA.944172.tab', 'pangaea',
     ('depthmap', 0, 'gicc05-rasmussen2022/PANGAEA.943193.tab', 'pangaea', 2, 0, 'b2k')),
    ('gisp2-b/ionb.txt', 'noaa', ('mid', 10, 11, 'bp')),
    ('gisp2-b/detionb.txt', 'noaa', ('mid', 11, 12, 'bp')),
    ('neem2011s1-sigl2022/PANGAEA.940553.tab', 'pangaea', ('col', 1, 'ce')),
    ('d4i-sigl2023/PANGAEA.960977.tab', 'pangaea', ('col', 1, 'ce')),
    ('ngt-b16/PANGAEA.57093.tab', 'pangaea', ('col', 3, 'ce')),
    ('ngt-14C93/PANGAEA.56613.tab', 'pangaea', ('col', 3, 'ce')),
    ('ngt-27C94/PANGAEA.57295.tab', 'pangaea', ('col', 3, 'ce')),
    ('ngt-b21-mieding/PANGAEA.484983.tab', 'pangaea', ('col', 6, 'ce')),
    ('ngt-b21-mieding/PANGAEA.484984.tab', 'pangaea', ('col', 6, 'ce')),
    ('recap-segato2021/PANGAEA.937435.tab', 'pangaea', ('col', 1, 'kab2k')),
    ('recap-segato2021/PANGAEA.937429.tab', 'pangaea', ('col', 1, 'kab2k')),
    ('recap-segato2021/PANGAEA.937433.tab', 'pangaea', ('col', 1, 'kab2k')),
    ('tunu2013/Tunu13_database_120216.csv', 'csv', ('col', 'est_yr_Chrono_v1', 'ce')),
    ('tunu2022/Tunu22a_database_120624.csv', 'csv', ('col', 'Age_yb1950_DRI_NGRIP2_Chronology', 'bp')),
    ('tunu2022/Tunu22b_database_120624.csv', 'csv', ('col', 'Age_yb1950_DRI_NGRIP2_Chronology', 'bp')),
    ('tunu-va-grieman/tunuVAdataADC.csv', 'csv', ('mid', 'Min_Year', 'Max_Year', 'ce')),
    ('summit2023/Summit2023_ChemistryData_17to142m.csv', 'csv', ('col', 'est_yr', 'ce')),
    ('ht95/HT95_database_DRI.csv', 'csv', ('col', 'Est_year', 'ce')),
    ('d4i-adc/D4i_database_120216.csv', 'csv', ('col', 'est_yr', 'ce')),
    ('neem2008s3/NEEM2008S3_S_Sr_Ca.csv', 'csv', ('col', 'Year', 'ce')),
    ('zhai-6cores/GreenlandIceCoreElementalConcentration.csv', 'csv', ('col', 'MidYr', 'ce')),
    ('zhai-6cores/GreenlandIceCoreIonConcentration.csv', 'csv', ('col', 'Year', 'ce')),
    ('zhai-6cores/Ice_Core_Information.csv', 'csv', None),
    ('rbc-array-2010/1750_to_2010_global_rBC_deposition.csv', 'csv', ('col', 'Year', 'ce')),
    ('rbc-array-2010/1750_to_2010_global_ice_core_array_information.csv', 'csv', None),
    ('rbc-array-2010/1750_to_2010_global_ice_core_array_references.csv', 'csv', None),
    ('flade-isblink/Arctic_Data_Center_posting_Sept_2022.csv', 'csv-skip5', ('col', 'Mid_year', 'ce')),
    ('tunu-n/Tunu_database_031814_CADIS.xlsx', 'xlsx', ('col', 'est_yr', 'ce')),
    ('humboldt/HumbMain_database_031814_CADIS.xlsx', 'xlsx', ('col', 'est_yr', 'ce')),
    ('summit2010/Zoe2_database_031814_CADIS.xlsx', 'xlsx', ('col', 'est_yr', 'ce')),
    ('neem2011s1-adc/NEEMS1_database_031814_CADIS.xlsx', 'xlsx', ('col', 'est_yr', 'ce')),
    ('act11d/ACT11d_database_031814_CADIS.xlsx', 'xlsx', ('col', 'est_yr', 'ce')),
    ('sigl2013-jgr/Sigl_et_al_JGR_2013_data.xlsx', 'xlsx', ('col', 'Year*', 'ce')),
    ('summit2007-coledai/SU07chem_Data.xlsx', 'xlsx', None),
]


MISSING = (-0.999, -999.0, -9.999, 999999.0)


def to_ce(v, unit):
    if v in MISSING:
        return None
    return {'ce': v, 'bp': 1950 - v, 'b2k': 2000 - v,
            'kab2k': 2000 - 1000 * v, 'kabp': 1950 - 1000 * v}[unit]


def num(x):
    try:
        v = float(str(x).strip())
    except ValueError:
        return None
    return v if v == v else None


def red(line):
    return '[REDACTED: mentions target window]' if REDACT.search(line) else line


# ---------- readers: return (header_lines, colnames, rows as lists of strings) ----------

def read_text(path):
    raw = open(path, 'rb').read()
    for enc in ('utf-8-sig', 'latin-1'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass


def read_noaa(path, fmt):
    lines = read_text(path).splitlines()
    sep = '\t' if fmt == 'noaa-tab' else None
    hdr, rows, cols = [], [], None
    for l in lines:
        if fmt == 'noaa-tab' and l.startswith('#'):
            hdr.append(l)
            continue
        toks = l.split(sep) if sep else l.split()
        filled = [t for t in toks if t.strip()]
        if filled and num(toks[0]) is not None and sum(num(t) is not None for t in filled) >= len(filled) / 2:
            rows.append(toks)
        else:
            if l.strip() and not rows:
                hdr.append(l)
    # column line = last non-comment header line containing several tokens
    for l in reversed(hdr):
        if not l.startswith('#') and len(l.split(sep) if sep else l.split()) >= 3:
            cols = [c.strip() for c in (l.split(sep) if sep else re.split(r'\t|\s{2,}', l.strip()))]
            break
    return hdr, cols or [], rows


def read_pangaea(path):
    text = read_text(path)
    head, _, body = text.partition('*/')
    lines = body.strip('\n').splitlines()
    cols = lines[0].split('\t')
    rows = [l.split('\t') for l in lines[1:] if l.strip()]
    return head.splitlines(), cols, rows


def read_csv(path, skip=0):
    text = read_text(path)
    allrows = list(csv.reader(io.StringIO(text)))
    hdr = [','.join(r) for r in allrows[:skip]]
    cols = [c.strip() for c in allrows[skip]] if len(allrows) > skip else []
    rows = [r for r in allrows[skip + 1:] if any(x.strip() for x in r)]
    return hdr, cols, rows


NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'


def xlsx_sheets(path):
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall(NS + 'si'):
            ss.append(''.join(t.text or '' for t in si.iter(NS + 't')))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    for s in wb.find(NS + 'sheets'):
        tgt = rels[s.get(RID)].lstrip('/')
        tgt = tgt if tgt.startswith('xl/') else 'xl/' + tgt
        out = []
        for row in ET.fromstring(z.read(tgt)).iter(NS + 'row'):
            vals = {}
            for c in row.findall(NS + 'c'):
                ref = re.match(r'[A-Z]+', c.get('r')).group(0)
                ci = 0
                for ch in ref:
                    ci = ci * 26 + ord(ch) - 64
                v = c.find(NS + 'v')
                if v is None:
                    isel = c.find(NS + 'is')
                    val = ''.join(x.text or '' for x in isel.iter(NS + 't')) if isel is not None else ''
                else:
                    val = ss[int(v.text)] if c.get('t') == 's' else v.text
                vals[ci - 1] = val
            if vals:
                out.append([vals.get(i, '') for i in range(max(vals) + 1)])
        yield s.get('name'), out


# ---------- reporting ----------

def ages_for(rows, cols, spec, path_for):
    kind = spec[0]

    def idx(c):
        return c if isinstance(c, int) else cols.index(c)
    out = []
    if kind == 'col':
        i = idx(spec[1])
        for r in rows:
            v = num(r[i]) if len(r) > i else None
            out.append(to_ce(v, spec[2]) if v is not None else None)
    elif kind == 'mid':
        i, j = idx(spec[1]), idx(spec[2])
        for r in rows:
            a = num(r[i]) if len(r) > i else None
            b = num(r[j]) if len(r) > j else None
            if a is not None and b is not None and a not in MISSING and b not in MISSING:
                out.append(to_ce((a + b) / 2, spec[3]))
            else:
                out.append(None)
    elif kind == 'depthmap':
        # spec: ('depthmap', depthcol, agefile, agefile_format, agefile_depthcol, agefile_agecol, unit)
        _, afmt, adc, aac, unit = spec[2:]
        reader = read_pangaea if afmt == 'pangaea' else (lambda p: read_noaa(p, afmt))
        _, acols, arows = reader(path_for(spec[2]))
        di = adc if isinstance(adc, int) else acols.index(adc)
        yi = aac if isinstance(aac, int) else acols.index(aac)
        pts = sorted((num(r[di]), to_ce(num(r[yi]), unit)) for r in arows
                     if len(r) > max(di, yi) and num(r[di]) is not None and num(r[yi]) is not None)
        i = idx(spec[1])
        for r in rows:
            d = num(r[i]) if len(r) > i else None
            if d is None or d < pts[0][0] or d > pts[-1][0]:
                out.append(None)
                continue
            for (d0, y0), (d1, y1) in zip(pts, pts[1:]):
                if d0 <= d <= d1:
                    out.append(y0 + (y1 - y0) * (d - d0) / (d1 - d0) if d1 > d0 else y0)
                    break
    # discard impossible ages (missing-value codes such as -0.999 and -999)
    return [a if a is not None and -3000 < a < 2100 and a not in () else None for a in out]


def safe_row(r, age):
    if age is None or SHOW_OK[0] <= age <= SHOW_OK[1]:
        return '   [row not shown: age unknown or within %d-%d]' % SHOW_OK
    return '   ' + ' | '.join(str(x) for x in r)[:220]


def report(label, hdr, cols, rows, spec):
    print('  header lines (%d, first %d shown, target-window mentions redacted):' % (len(hdr), MAX_HDR))
    for l in hdr[:MAX_HDR]:
        if l.strip():
            print('    ' + red(l)[:200])
    print('  columns (%d): %s' % (len(cols), ' | '.join(cols)[:900]))
    print('  data rows: %d' % len(rows))
    if spec is None:
        print('  no age column (depth only or metadata table)')
        return
    ages = ages_for(rows, cols, spec, lambda p: os.path.join(DATA, p))
    good = [a for a in ages if a is not None]
    if not good:
        print('  no usable ages found')
        return
    print('  CE span: %.1f to %.1f   (rows with a valid age: %d)' % (min(good), max(good), len(good)))
    dec = collections.Counter(int(a // 10 * 10) for a in good if 1700 <= a < 2020)
    print('  rows per decade 1700-2019:', ' '.join('%d:%d' % kv for kv in sorted(dec.items())) or 'none')
    yr = collections.Counter(int(a // 1) for a in good if 1880 <= a < 1936)
    print('  rows per calendar year 1880-1935 (from age column only):')
    print('    ' + ' '.join('%d:%d' % (y, yr.get(y, 0)) for y in range(1880, 1936)))
    missing = [y for y in range(BLIND[0] - 5, BLIND[1] + 6) if yr.get(y, 0) == 0]
    if 1880 <= max(good) and min(good) <= 1935:
        print('    years 1890-1925 with no row:', missing if missing else 'none')
    print('  first row:')
    print(safe_row(rows[0], ages[0]))
    print('  last row:')
    print(safe_row(rows[-1], ages[-1]))


def main():
    filt = sys.argv[1] if len(sys.argv) > 1 else ''
    for rel, fmt, spec in FILES:
        if filt and filt not in rel:
            continue
        path = os.path.join(DATA, rel)
        print('=' * 100)
        print(rel)
        if not os.path.exists(path):
            print('  MISSING (not downloaded)')
            continue
        try:
            if fmt in ('noaa', 'noaa-tab'):
                report(rel, *read_noaa(path, fmt), spec)
            elif fmt == 'pangaea':
                report(rel, *read_pangaea(path), spec)
            elif fmt.startswith('csv'):
                skip = int(fmt[8:]) if fmt.startswith('csv-skip') else 0
                report(rel, *read_csv(path, skip), spec)
            elif fmt == 'xlsx':
                for name, rows in xlsx_sheets(path):
                    print('  -- sheet: %s' % name)
                    if not rows:
                        continue
                    hi = 0
                    if spec is None:   # free-form sheet: find the row naming the species
                        for k, r in enumerate(rows[:12]):
                            if any(str(x).strip() in ('NO3', 'NH4', 'SO4') for x in r):
                                hi = k
                    cols = [str(c).strip() for c in rows[hi]]
                    hdr = [' '.join(str(x) for x in r if str(x).strip()) for r in rows[:hi]]
                    body = [r for r in rows[hi + 1:] if any(str(x).strip() for x in r)]
                    sp = spec if (spec and spec[1] in cols) else None
                    report(rel, hdr, cols, body, sp)
        except Exception as e:  # report and carry on
            print('  ERROR reading file: %r' % (e,))


if __name__ == '__main__':
    main()
