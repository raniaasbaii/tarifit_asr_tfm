#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

BOOK_LABELS = {"matta", "markus"}


def clean_line(line: str) -> str:
    kept = []

    for char in line.lower():
        # Keep every letter exactly as written, including Tarifit characters.
        if char.isalpha() or char == "ʷ":
            kept.append(char)
        else:
            # Numbers and all punctuation become spaces.
            kept.append(" ")

    return re.sub(r"\s+", " ", "".join(kept)).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    raw_text = args.source.read_text(encoding="utf-8")
    cleaned_lines = []

    for raw_line in raw_text.splitlines():
        line = clean_line(raw_line)

        if not line:
            continue

        # Remove website-only book labels, wherever they occur.
        if line in BOOK_LABELS:
            continue

        cleaned_lines.append(line)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")

    print(f"Created: {args.output}")


if __name__ == "__main__":
    main()