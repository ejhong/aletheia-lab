# Format notes for the replication

These notes describe the files and the output wanted. They add no analysis choice; every choice is in
`protocol.md` and `analysis/METHOD.md`.

## Input files

- A settings file (JSON), as described in section 1 of the method. File names in it are relative to the
  settings file's own folder, unless they are absolute paths.
- The names file and parts file are JSON lines (one JSON object per line, UTF-8). The words file is one JSON
  object. Example lines:

      names:  {"name": "Pāṇar", "type": "group", "morphemes": ["pāṇ", "ar"], "source": "sangam", "weight": 154}
      parts:  {"m": "pāṇ", "category": "occupation_group", "stability": 2}
      words:  {"740": {"jar": ["kuṭam"], "pot": ["kalam", "pāṉai"], "vessel": [], "handle": ["kāmpu"]}, ...}

- The corpus is a CSV file with a header line, read with a standard CSV reader (fields may be quoted and may
  contain commas). Columns used: `text` (for example `+740-390-590+`), `dir.` (`R/L`, `L/R` or other values),
  `type` (for example `SEAL:S`, `TAB:B`).

Python 3.12 and its standard library only.

## The program wanted

`python replicate.py SETTINGS.json CORPUS.csv FIRST_SEED LAST_SEED OUT.json`

For every seed from FIRST_SEED to LAST_SEED inclusive, do one run in `real` mode and one in `null` mode (no sign
left unread, pictures not shuffled), and write OUT.json as one JSON object:

    {"lang": "<the settings' lang>",
     "runs": [{"seed": 0, "real": 217.05, "null": 113.22, "difference": 103.83,
               "signs_read": 30, "readings": {"220": "mīṉ", "740": "kuṭi", ...}}, ...],
     "mean_difference": 223.0, "seeds_above_zero": 10}

`real` and `null` are each run's `heldout` rounded to two decimals; `readings` are the readings chosen in the
`real` run (signs left as GAP are left out); `signs_read` is their number.

A run takes a second or two in plain Python if `lp` and `pun_cost` are cached.
