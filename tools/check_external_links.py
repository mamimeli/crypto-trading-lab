#!/usr/bin/env python3
"""Check the external URLs written in the repository's Markdown.

`check_doc_links.py` deliberately stops at the edge of the repository: it
verifies local files and `#anchors` and skips anything starting with
`http`. That keeps the gate offline, which this project promises in several
places — but it also means nothing notices when an external reference rots.
A publisher reorganises its site, an Actions run is deleted, and the README
keeps pointing at it.

This script is the other half, and it is the only thing in the repository
that reaches the network on purpose. Three consequences, all deliberate:

* It is **not** part of `tests.yml`. A third-party outage must never turn a
  push red, so the offline gate stays offline and this runs on a schedule
  (`.github/workflows/links-external.yml`) or on demand.
* Every URL is classified. Two classes fail the run: a link that is gone
  (404/410, or a host that no longer resolves) and one whose status could not
  be determined (403, 429, 5xx, timeout). The second class can be accepted
  through `external_links_allowlist.txt`, one host per line with a reason —
  a host that refuses automated clients is a fact about that host, not about
  the document.
* Nothing here is trusted by the test suite, and no test reaches the network:
  `tests/test_external_links.py` drives the classification with a fake fetcher.

What it deliberately does not check
-----------------------------------
- URLs inside fenced code blocks or inline code. Two of them here are meant
  to be unreachable: `http://127.0.0.1:9` (the dead proxy in the offline
  proof) and `https://example.com`. Checking them would fail documentation
  that is correct.
- Loopback and `example.*` hosts anywhere, for the same reason.
- Whether the page still *says* what the document claims. This proves the
  reference resolves, not that it is still the right reference.
- `#fragments` on external URLs: verifying those means downloading and
  parsing every target, and a moved heading is not worth a weekly crawl.

Run it from anywhere:

    python3 tools/check_external_links.py [--verbose]

Exit codes: 0 clean, 1 at least one failure, 2 unusable arguments.
"""

from __future__ import annotations

import argparse
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

# Directories that are not project documentation: dependencies, tool caches
# and the archived scratch area. Same list as check_doc_links.py.
SKIP_DIRS = {
    ".git",
    ".venv",
    ".scratch",
    "external",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
# Parentheses are allowed inside the match because a link target may contain
# them; _trim() removes the link's own closing bracket afterwards.
URL = re.compile(r"https?://[^\s\]\"'<>`]+")

# Identifies the checker to the hosts it visits; a bare urllib agent is
# rejected by several documentation sites.
USER_AGENT = (
    "crypto-trading-lab-link-check/1.0 "
    "(+https://github.com/wachin/crypto-trading-lab)"
)

OK = "ok"
REDIRECTED = "redirected"
ACCEPTED = "accepted"
UNVERIFIED = "unverified"
BROKEN = "broken"

#: Outcomes that make the run fail.
FAILING = {BROKEN, UNVERIFIED}

#: HEAD is refused by some servers but GET works; retry those as GET.
_HEAD_UNSUPPORTED = {403, 405, 501}

#: The page is gone, not merely unavailable.
_ABSENT = {404, 410}

#: Hosts that can never be reached from CI and are not meant to be.
_SKIP_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]"}
_RESERVED_DOMAINS = ("example.com", "example.org", "example.net", "example")


@dataclass(frozen=True)
class FetchResult:
    """What one request produced.

    `status` is `None` when no HTTP response arrived at all;
    `transport` then says why, because a host that no longer resolves is a
    broken link while a timeout is not.
    """

    status: int | None = None
    final_url: str = ""
    detail: str = ""
    transport: str = ""  # "" | "dns" | "timeout" | "other"


@dataclass(frozen=True)
class LinkResult:
    """One URL, its outcome, and the documents that mention it."""

    url: str
    outcome: str
    detail: str
    sources: tuple[str, ...] = ()


def markdown_files(root: Path) -> list[Path]:
    """Every Markdown file that is project documentation.

    The order is the plain POSIX relative path, not the order of ``Path``
    objects: Windows compares paths case-insensitively, so sorting paths
    would put ``docs/guide.md`` before ``README.md`` there and after it on
    Linux. The report must read the same on every platform.
    """
    return sorted(
        (
            path
            for path in root.rglob("*.md")
            if not (set(path.relative_to(root).parts) & SKIP_DIRS)
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def external_urls(text: str) -> list[str]:
    """The URLs in `text` that a reader would follow.

    Code is excluded twice: whole fenced blocks, and inline spans. Both hold
    addresses this repository writes on purpose and does not expect to
    resolve.
    """
    urls: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in URL.findall(INLINE_CODE.sub(" ", line)):
            urls.append(_trim(match))
    return urls


def _trim(url: str) -> str:
    """Strip what a sentence adds to a URL, and nothing that belongs to it.

    A Markdown link may legitimately contain parentheses — a shields.io badge
    here is `.../method-L%C3%B3pez%20de%20Prado%20(2018)-8b5cf6.svg` — so
    the match runs to the end of the run of non-space characters, and the
    trailing `)` of the link syntax is removed only while it is
    unbalanced. Trimming every `)` would cut a real path; trimming none
    would append the link's own bracket to the URL.
    """
    url = url.rstrip(".,;:!?*")
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def is_checkable(url: str) -> bool:
    """False for loopback and reserved domains, which are never fetched."""
    host = (urlsplit(url).hostname or "").lower()
    if not host:
        return False
    if host in _SKIP_HOSTS:
        return False
    return not (
        host in _RESERVED_DOMAINS
        or host.endswith(tuple("." + domain for domain in _RESERVED_DOMAINS))
    )


def load_allowlist(path: Path) -> dict[str, str]:
    """Hosts whose refusal is accepted, each with the reason recorded.

    Format: one `host  # reason` per line. A reason is required — an
    unexplained exemption is how a checker quietly stops checking.
    """
    allowed: dict[str, str] = {}
    if not path.is_file():
        return allowed
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        body, _, comment = raw.partition("#")
        host = body.strip().lower()
        reason = comment.strip()
        if not host:
            continue
        if not reason:
            raise ValueError(f"{path}:{number}: {host} needs a reason after '#'")
        allowed[host] = reason
    return allowed


def _request(url: str, method: str, timeout: float) -> FetchResult:
    headers = {"User-Agent": USER_AGENT}
    if method == "GET":
        headers["Range"] = "bytes=0-0"
    request = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return FetchResult(status=response.status, final_url=response.geturl())
    except urllib.error.HTTPError as error:
        return FetchResult(
            status=error.code,
            final_url=url,
            detail=str(error.reason or f"HTTP {error.code}"),
        )
    except urllib.error.URLError as error:
        reason = error.reason
        if isinstance(reason, socket.gaierror):
            return FetchResult(transport="dns", detail=str(reason))
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return FetchResult(transport="timeout", detail=str(reason))
        return FetchResult(transport="other", detail=str(reason))
    except (TimeoutError, socket.timeout) as error:
        return FetchResult(transport="timeout", detail=str(error))
    except OSError as error:  # TLS failures, resets, malformed URLs
        return FetchResult(transport="other", detail=str(error))


def fetch_url(url: str, *, timeout: float = 10.0) -> FetchResult:
    """One attempt: HEAD, confirmed by a one-byte GET when HEAD is doubtful.

    Both refusals and "gone" are re-asked as GET, because HEAD is widely
    implemented badly: www.workbuddy.ai answered 404 to HEAD and 200 to GET
    for the same path, which would have been reported as a dead link. A link
    is only called broken once the method a reader uses agrees.
    """
    result = _request(url, "HEAD", timeout)
    if result.status in _HEAD_UNSUPPORTED or result.status in _ABSENT:
        return _request(url, "GET", timeout)
    return result


def classify(result: FetchResult, url: str) -> tuple[str, str]:
    """Map one fetch to an outcome and a human reason. Pure by design."""
    if result.status is None:
        if result.transport == "dns":
            return BROKEN, f"host does not resolve: {result.detail}"
        transport = result.transport or "transport"
        return UNVERIFIED, f"no response ({transport}): {result.detail}"
    if 200 <= result.status < 300:
        if result.final_url and result.final_url != url:
            return REDIRECTED, f"redirected to {result.final_url}"
        return OK, f"HTTP {result.status}"
    if 300 <= result.status < 400:
        # urllib follows redirects, so a bare 3xx here means it could not:
        # no Location header, or a chain it refused. Reported, not failed.
        return REDIRECTED, f"HTTP {result.status}: not followed"
    if result.status in _ABSENT:
        return BROKEN, f"HTTP {result.status}: gone"
    if result.status == 403:
        return UNVERIFIED, "HTTP 403: the host refuses automated clients"
    if result.status == 429:
        return UNVERIFIED, "HTTP 429: rate limited"
    if result.status == 451:
        return UNVERIFIED, "HTTP 451: unavailable for legal reasons"
    if 500 <= result.status < 600:
        return UNVERIFIED, f"HTTP {result.status}: server error"
    return UNVERIFIED, f"HTTP {result.status}"


def _worth_retrying(result: FetchResult) -> bool:
    if result.status is None:
        # A missing DNS record will not heal in the next four seconds.
        return result.transport != "dns"
    return result.status == 429 or 500 <= result.status < 600


def check_url(
    url: str,
    *,
    fetch: Callable[..., FetchResult] = fetch_url,
    timeout: float = 10.0,
    retries: int = 2,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[str, str]:
    """Fetch `url` with backoff, then classify what came back."""
    result = fetch(url, timeout=timeout)
    attempt = 0
    while _worth_retrying(result) and attempt < retries:
        attempt += 1
        sleep(float(2**attempt))
        result = fetch(url, timeout=timeout)
    return classify(result, url)


def check(
    root: Path,
    *,
    fetch: Callable[..., FetchResult] = fetch_url,
    timeout: float = 10.0,
    retries: int = 2,
    allowlist: dict[str, str] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> list[LinkResult]:
    """Check every external URL in the documentation under `root`."""
    allowed = allowlist or {}
    sources: dict[str, list[str]] = {}
    for document in markdown_files(root):
        relative = document.relative_to(root).as_posix()
        text = document.read_text(encoding="utf-8", errors="replace")
        for url in external_urls(text):
            if not is_checkable(url):
                continue
            if relative not in sources.setdefault(url, []):
                sources[url].append(relative)

    results: list[LinkResult] = []
    for url in sorted(sources):
        outcome, detail = check_url(
            url, fetch=fetch, timeout=timeout, retries=retries, sleep=sleep
        )
        host = (urlsplit(url).hostname or "").lower()
        if outcome == UNVERIFIED and host in allowed:
            outcome = ACCEPTED
            detail = f"{detail} (allowlisted: {allowed[host]})"
        results.append(
            LinkResult(
                url=url, outcome=outcome, detail=detail, sources=tuple(sources[url])
            )
        )
    return results


def _print(result: LinkResult) -> None:
    print(f"  [{result.outcome.upper()}] {result.url}")
    print(f"           {result.detail}")
    print(f"           in: {', '.join(result.sources)}")


def main(argv: list[str] | None = None) -> int:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Check the external URLs in the Markdown (reaches the network).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="repository root (default: the parent of this tool's directory)",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=None,
        help="hosts whose refusal is accepted (default: tools/external_links_allowlist.txt)",
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="seconds per request (default: 10)"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="retries for transient failures (default: 2)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="also print the links that passed"
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not (root / "README.md").is_file():
        print(f"error: {root} does not look like the repository root", file=sys.stderr)
        return 2

    allowlist_path = args.allowlist or root / "tools" / "external_links_allowlist.txt"
    try:
        allowlist = load_allowlist(allowlist_path)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print("External links")
    print("=" * 50)
    results = check(
        root,
        timeout=args.timeout,
        retries=args.retries,
        allowlist=allowlist,
    )

    failures = [result for result in results if result.outcome in FAILING]
    accepted = [result for result in results if result.outcome == ACCEPTED]
    passed = [result for result in results if result.outcome in {OK, REDIRECTED}]

    for result in failures + accepted:
        _print(result)
    if args.verbose:
        for result in passed:
            _print(result)

    counts: dict[str, int] = {}
    for result in results:
        counts[result.outcome] = counts.get(result.outcome, 0) + 1
    summary = ", ".join(f"{count} {name}" for name, count in sorted(counts.items()))
    print()
    print(f"{len(results)} external URL(s) checked: {summary or 'none'}.")

    if failures:
        print("Nothing was changed. Fix the link, or allowlist the host with a reason.")
        return 1
    if accepted:
        print("Allowlisted hosts are reported, not silently skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
