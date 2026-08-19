# Text-Summarizer-Tool

A command-line tool that summarizes any text (pasted, from a file, or piped
in via stdin) using the Google AI Studio (Gemini) API. It returns a
structured JSON summary — not just free-form text — with a summary, key
points, and risk flags, enforced via a system prompt.

## What it does

- Takes text via `--text`, `--file`, or stdin
- Sends it to Gemini with a system prompt that forces a consistent JSON
  output shape: `summary`, `key_points`, `risk_flags`
- Supports three summary styles: `concise` (default), `detailed`, `bullet`
- Prints the structured result to the terminal

## Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
3. Copy `.env.example` to `.env` and add your key:
   ```bash
   cp .env.example .env
   # then edit .env and set GEMINI_API_KEY=your-key-here
   ```

## How to run it

```bash
# Summarize text directly
python summarize.py --text "Paste your text here"

# Summarize a file
python summarize.py --file article.txt

# Pipe text in
cat article.txt | python summarize.py

# Choose a style
python summarize.py --file article.txt --style bullet
```

Example output (real test run):
```bash
python summarize.py --text "Google Pay lets users make instant UPI payments, but its fraud warnings are often generic rather than explaining why a transaction looks risky."
```
```json
{
  "summary": "Google Pay facilitates instant UPI payments for its users. However, its security system currently issues generic fraud warnings that fail to explain the specific reasons a transaction is flagged as risky.",
  "key_points": [
    "Google Pay enables instant UPI payments.",
    "Fraud warnings on the platform are frequently generic.",
    "Users lack clear context on why specific transactions are flagged."
  ],
  "risk_flags": [
    "Generic fraud warnings may cause users to overlook actual transaction risks.",
    "Very short source text with limited broader context."
  ]
}
```

## Limitations

The `risk_flags` field relies on the model's own judgment of what's
"risky" or missing context — it's not a rules-based check, so it can miss
things a domain expert would catch (e.g. a subtly one-sided financial
claim) or flag things that aren't actually a concern. It's a starting
signal, not a substitute for review.

During testing, the Gemini API occasionally returned a `503 UNAVAILABLE`
error under high demand — a transient server-side issue, not a bug in
this tool. A simple retry resolved it. A production version of this tool
would want built-in retry/backoff logic rather than relying on the user
to re-run the command manually.
