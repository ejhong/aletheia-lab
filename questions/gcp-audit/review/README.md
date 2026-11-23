# Review of the plan before it is locked

Before the lock, models from two other vendors (OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`) read
`protocol.md` and criticise it. Run `python3 review/run_review.py round1` from `questions/gcp-audit` (add `--narrow`
for an errors-only round, and a vendor name to ask only one); keys come from `OPENAI_API_KEY` and `GEMINI_API_KEY`.
Each round's replies land in `review/<round>/<vendor>.md` and `.json`, with the text they saw in
`protocol_as_reviewed.md`.
