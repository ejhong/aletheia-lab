# Amendments

Changes after the lock of 2026-11-28T03:15:52Z, newest last. Each is written before the part it affects is run.

## 1. A letter the sound table does not know, in the Tamil lists (2026-11-27, before any contest run on a new list)

Both fresh Tamil translators gave *eḵku* (steel, spear), written with the Tamil āytam, ḵ. The contest's sound
table has no such letter and would drop it. The plan's rule for this case is to map the letter to the table's
nearest sound. The āytam is a weak breathed sound, and the nearest entry in the table is ḥ. So in
`prompts/languages.json` the letter map of both fresh Tamil lists, which was empty, is now ḵ → ḥ. It applies
to name parts and picture words alike. No other language's words had a letter outside the table after its map.

The preprint's own Tamil list has no ḵ and is not affected.

## 2. A list whose name parts came as one string (2026-11-27, before any contest run on a new list)

The plan's prompt asks for each name's parts as a list. The Hebrew name compiler wrote them as one string with
the parts joined by " + ", the same mark the prompt prescribes for the glosses (for example `"ʾab + rām"`).
All 683 of its names are in that form, and in every one the number of parts so written equals the number of
glosses. Nothing is missing; only the punctuation differs.

`analysis/build_inputs.py` now splits such a string on " + ". The compiler's file is kept as it was written.
This is a change of format handling, applied by program to any list, and no list is edited by hand. The other
nine lists give their parts as lists and are not affected. The labeler session that had been started on the
unsplit Hebrew file was given single letters as "parts"; its output is discarded and the labeler is run again
on the correct file.
