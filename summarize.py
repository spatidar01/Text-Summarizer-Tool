#!/usr/bin/env python3
"""Summarize text using the Google AI Studio (Gemini) API."""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-2.0-flash"

# System prompt: fixes the model's role and output contract for every call.
# This is what makes the output structured and predictable instead of
# free-form text that varies call to call.
SYSTEM_PROMPT = (
    "You are a text summarization engine for a productivity tool. "
    "Given any input text, respond with a single JSON object with exactly "
    "these three keys:\n"
    '- "summary": a concise 2-4 sentence summary of the text\n'
    '- "key_points": an array of 3-6 short strings, the main points\n'
    '- "risk_flags": an array of short strings noting anything the reader '
    "should be cautious about (e.g. missing context, one-sided claims, "
    "unverified numbers, sensitive/financial advice). Return an empty "
    "array if nothing stands out.\n"
    "Only output the JSON object. No markdown, no commentary, no code fences."
)


def get_client() -> genai.Client:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "Error: GEMINI_API_KEY is not set. "
            "Copy .env.example to .env and add your Google AI Studio API key.",
            file=sys.stderr,
        )
        sys.exit(1)
    return genai.Client(api_key=api_key)


def summarize(text: str, *, model: str = DEFAULT_MODEL, style: str = "concise") -> dict:
    """Return a structured summary of the given text.

    Returns a dict with keys: summary, key_points, risk_flags.
    """
    client = get_client()

    # The style is passed as part of the user turn; the SYSTEM_PROMPT fixes
    # the output shape (JSON, same 3 keys) regardless of style.
    user_prompt = (
        f"Summary style requested: {style}.\n\n"
        f"Text to summarize:\n{text}"
    )

    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        # Fallback: model didn't return valid JSON. Surface the raw text
        # so the caller can see what went wrong instead of crashing.
        return {
            "summary": response.text,
            "key_points": [],
            "risk_flags": ["Model did not return valid JSON — raw output shown in summary."],
        }


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        path = Path(args.file)
        if not path.is_file():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        return path.read_text(encoding="utf-8")

    if args.text:
        return args.text

    if not sys.stdin.isatty():
        return sys.stdin.read()

    print("Error: provide text via --text, --file, or stdin.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize text with Gemini.")
    parser.add_argument("--text", "-t", help="Text to summarize")
    parser.add_argument("--file", "-f", help="Path to a text file to summarize")
    parser.add_argument(
        "--style",
        "-s",
        default="concise",
        choices=["concise", "detailed", "bullet"],
        help="Summary style (default: concise)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help=f"Gemini model ID (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    text = read_input(args).strip()
    if not text:
        print("Error: no text provided.", file=sys.stderr)
        sys.exit(1)

    result = summarize(text, model=args.model, style=args.style)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
