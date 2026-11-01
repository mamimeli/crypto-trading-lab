#!/usr/bin/env python3
"""Check every local link and anchor in the repository's Markdown.

Nothing else catches this. The test suite never reads the README, and a link
checker that only verifies that files exist will not look inside
``#fragments`` — so renaming a heading silently breaks every link pointing at
it. That happened here: a heading rename broke two links, and three more had
pointed at an anchor that never existed, all of them invisible until clicked.

What it checks
--------------
1. **Files.** ``[text](docs/en/developers/venv-setup.md)`` must resolve
   relative to the file containing it.
2. **Anchors.** ``[text](#some-heading)`` and
   ``[text](other.md#some-heading)`` must match a heading in the target file,
   using GitHub's slug algorithm.

What it deliberately does not check
-----------------------------------
- External URLs (``http://``, ``https://``). This must stay offline: a link
  checker that reaches the network is a bug, exactly like a test that does.
  ``tools/check_external_links.py`` covers those instead, on a weekly schedule
  and never as part of this gate.
- Reference-style links (``[text][label]``), which this repository does not
  use. If one is ever introduced, extend this script rather than trusting it.
- Whether an image path resolves. Images are assets, not documentation
  navigation, and a missing one is a visual problem, not a broken reference.

Run it from anywhere:

    python3 tools/check_doc_links.py

It exits 0 when everything resolves and 1 when something does not, so it can
be used as a CI gate.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Directories that are not project documentation: dependencies, tool caches
# and the archived scratch area.
SKIP_DIRS = {".git", ".venv", ".scratch", "external", "node_modules", "__pycache__"}

# Inline links: [anything](target). The target stops at whitespace or ')'.
INLINE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

# Headings that produce anchors: ATX form only (this project uses no Setext).
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")

# Inline HTML and code spans inside a heading are not part of the slug.
HTML_TAG = re.compile(r"<[^>]+>")


def slugify(heading: str) -> str:
    """Reproduce GitHub's heading-to-anchor algorithm.

    The detail that matters, and that a naive implementation gets wrong:
    GitHub emits **one hyphen per space and does not collapse runs**, so
    ``## Contributing — bring your AI agent`` becomes
    ``#contributing--bring-your-ai-agent`` (the em dash is dropped, leaving
    two spaces, hence two hyphens). A checker that collapses whitespace
    reports false positives *and hides real breakage* in the noise.
    """
    text = HTML_TAG.sub("", heading)
    text = text.replace("`", "")
    text = text.strip().lower()
    # Keep word characters, spaces and hyphens; drop the rest (punctuation).
    text = re.sub(r"[^\w\s-]", "", text)
    # One hyphen per space, no collapsing.
    return text.replace(" ", "-")


def anchors_of(path: Path) -> set[str]:
    """Every anchor a Markdown file provides."""
    found: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = HEADING.match(line)
        if match:
            found.add(slugify(match.group(2)))
    return found


def markdown_files(root: Path) -> list[Path]:
    # Sort by the POSIX relative path: Windows compares paths
    # case-insensitively, so sorting ``Path`` objects orders the report
    # differently there than on Linux.
    return sorted(
        (
            path
            for path in root.rglob("*.md")
            if not (set(path.relative_to(root).parts) & SKIP_DIRS)
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "data:"))


def check(root: Path, verbose: bool = False) -> list[str]:
    """Return a list of human-readable problems; empty means clean."""
    files = markdown_files(root)
    anchor_cache: dict[Path, set[str]] = {}
    problems: list[str] = []
    files_checked = anchors_checked = 0

    for document in files:
        text = document.read_text(encoding="utf-8", errors="replace")
        relative = document.relative_to(root)
        for target in INLINE_LINK.findall(text):
            if is_external(target):
                continue

            path_part, _, fragment = target.partition("#")

            # Resolve the file half: empty means "this document".
            if path_part:
                destination = (document.parent / path_part).resolve()
                if not destination.exists():
                    problems.append(f"{relative}: missing file -> {target}")
                    continue
                files_checked += 1
            else:
                destination = document.resolve()

            if not fragment:
                continue

            # Resolve the anchor half against the destination document.
            if destination.suffix != ".md" or not destination.is_file():
                # Anchors only make sense in Markdown, and an anchor on a
                # non-Markdown target cannot be verified here.
                continue
            anchors_checked += 1
            if destination not in anchor_cache:
                anchor_cache[destination] = anchors_of(destination)
            if fragment.lower() not in anchor_cache[destination]:
                problems.append(f"{relative}: missing anchor -> {target}")

    if verbose:
        print(f"  Markdown files scanned : {len(files)}")
        print(f"  File links checked     : {files_checked}")
        print(f"  Anchors checked        : {anchors_checked}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check local Markdown links and anchors (offline).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (default: the parent of this script)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print what was scanned"
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not (root / "README.md").is_file():
        print(f"error: {root} does not look like the repository root", file=sys.stderr)
        return 2

    print("Documentation links")
    print("=" * 50)
    problems = check(root, verbose=args.verbose)

    if problems:
        for problem in problems:
            print(f"  [FAIL] {problem}")
        print()
        print(f"{len(problems)} broken reference(s). Nothing was changed.")
        return 1

    print("  All local links and anchors resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
