#!/usr/bin/env python3
"""Summarize text using the Google AI Studio (Gemini) API."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai

DEFAULT_MODEL = "gemini-2.0-flash"


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


def summarize(text: str, *, model: str = DEFAULT_MODEL, style: str = "concise") -> str:
    """Return a summary of the given text."""
    client = get_client()

    prompt = (
        f"Summarize the following text in a {style} way. "
        "Preserve the key points and main conclusions.\n\n"
        f"{text}"
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return response.text


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

    summary = summarize(text, model=args.model, style=args.style)
    print(summary)


if __name__ == "__main__":
    main()
