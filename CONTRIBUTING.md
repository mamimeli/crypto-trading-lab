# Contributing to Crypto Trading Lab

First: thank you. This project exists to give ordinary people an honest
research instrument instead of a hype machine, and every careful
contribution — a fix, a test, a clearer paragraph, a translation — moves
it closer to that.

**You do not need to be a quant, and you do not need to write code by
hand.** The repository is built *agent-first*: the specification is
written down chapter by chapter, the tests run offline in about thirty
seconds, and an AI agent can do verifiable work here without guessing.
Bring your agent; we bring the rails.

---

## 1. The five-minute orientation

Read these, in this order, before touching anything:

| # | File | What it gives you |
|---|---|---|
| 0 | [`CLAUDE.md`](CLAUDE.md) | Auto-loaded by Claude Code and other agent tools at session start; points to the files below |
| 1 | [`AGENT-HANDOFF.md`](AGENT-HANDOFF.md) | What is already built and the exact continuation point |
| 2 | [`AGENTS.md`](AGENTS.md) | The non-negotiable ground rules |
| 3 | [`ROADMAP.md`](ROADMAP.md) | **The specification.** Find the chapter that owns your task |
| 4 | [`docs/en/developers/architecture-proposal.md`](docs/en/developers/architecture-proposal.md) | How the layers fit together |

`ROADMAP.md` is the source of truth. A checkbox is ticked only when the
requirement is **implemented and tested**, never when it is "mostly
done".

**Where things go.** [Discussions](https://github.com/wachin/crypto-trading-lab/discussions)
is for questions ("how do I…"), ideas, research results and show-and-tell.
[Issues](https://github.com/wachin/crypto-trading-lab/issues) are for
things that are **broken**, and must include a reproducible command and
its real output.

---

## 2. Set up

```bash
sudo apt install python3-pyqt6 python3-pyqtgraph python3-sqlalchemy \
                 python3-platformdirs python3-pytest qt6-l10n-tools

git clone https://github.com/wachin/crypto-trading-lab
cd crypto-trading-lab

python3 -c "import pyqtgraph, sqlalchemy, platformdirs; print('deps OK')"
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q   # → 1102 passed, 2 skipped
PYTHONPATH=src python3 -m crypto_trading_lab            # run the app
```

- **Debian first.** Every runtime dependency is a Debian system package and
  that is the supported setup; the default workflow needs no virtualenv. A
  virtualenv exists for **PyPI-only extras** (`ccxt`, `pypdf`, `aiohttp`,
  `websockets`) and for an isolated environment — see
  [`docs/en/developers/venv-setup.md`](docs/en/developers/venv-setup.md)
  and [`docs/en/developers/debian-dependencies.md`](docs/en/developers/debian-dependencies.md).
- **You do not need `external/`.** The eight reference projects there were
  studied once; the study is concluded and its conclusions live in
  [`docs/en/developers/reference-projects.md`](docs/en/developers/reference-projects.md).
  A fresh clone creates `external/` as eight **empty** placeholder
  directories — git makes those for submodules — and the application builds,
  tests and runs without filling them. Fetch one **only** to re-verify a
  specific claim, and only that one —
  `git submodule update --init external/freqtrade`. Never `--recursive` by
  reflex: their working copies are 930 MB but a fetch pulls full history,
  about **11 GB**, 8 GB of it `external/ccxt`.
- GUI tests run headless with `QT_QPA_PLATFORM=offscreen`.

---

## 3. Workflow

1. **Pick a task.** Choose an open ROADMAP chapter or a
   [good first contribution](#6-good-first-contributions). If the task is
   not in the roadmap and is not a bug fix, open an issue first so the
   specification can grow with it.
2. **Branch.** `git checkout -b feat/chapter-XX-short-name`.
3. **Change small.** One requirement per pull request. If you find an
   unrelated bug, fix it in its own branch.
4. **Test after every change.**
   ```bash
   QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q
   ```
5. **Document in the same change.** If behaviour changes, docs change.
   If you complete a requirement, tick its `[x]` in `ROADMAP.md`.
6. **Commit** with a plain, conventional message:
   ```text
   feat(backtesting): add intrabar ambiguity policy  (chapter 37.5)
   fix(ui): notebook no longer crashes on open
   docs(beginners): explain R-multiples with an example
   test(metrics): hand-verify annualised return suppression
   ```
7. **Open a pull request** using the template. Describe what you changed,
   why, the exact test command you ran, and its real output.

### Definition of done

A change is done when:

- [ ] the requirement it implements is named (chapter + item),
- [ ] the full suite is green, with the real command output quoted,
- [ ] if the change touched Markdown, `python3 tools/check_doc_links.py` is
      green too,
- [ ] if the change touched a docstring, `python3 tools/check_docstring_refs.py`
      is green too,
- [ ] new behaviour has tests that fail without the change,
- [ ] documentation is updated in the same commit,
- [ ] visible UI strings are wrapped in `self.tr()`,
- [ ] no new dependency was installed,
- [ ] real trading is still disabled.

The link check exists because nothing else can catch this class of mistake.
The test suite never reads the documentation, and renaming a heading
silently breaks every link pointing at its anchor — three such links lived in
the README undetected until the check was written. It needs no dependency and
no network: `python3 tools/check_doc_links.py`, also run by CI.

The same reasoning applies one layer in. Docstrings carry Sphinx roles
(`:class:`, `:func:`, `:meth:`) and repository paths, and nothing reads
those either — a rename leaves them pointing at nothing.
`check_docstring_refs.py`
resolves both against the AST (no imports, so no optional dependency is
needed), reports how many references it checked, and fails when it finds
none, because a scanner that matches nothing is broken too.

The third checker goes the other way and reaches the network:
`python3 tools/check_external_links.py` visits every
`http(s)://` URL in the Markdown and reports what came back. It is **not**
part of the offline gate and never runs on a push — a third-party outage must
not turn a commit red — so it runs weekly
(`.github/workflows/links-external.yml`) and on demand. Two
outcomes fail it: a link that is gone (404/410, or a host that no longer
resolves) and one whose status could not be determined (403, 429, 5xx,
timeout). The second kind can be accepted in
`tools/external_links_allowlist.txt`, one host per line with a reason;
a 404 is never excused. If your change adds an external link, run the checker
once by hand before opening the pull request.

---

## 4. The non-negotiable rules

These come from [`AGENTS.md`](AGENTS.md) and apply to humans and agents
alike.

1. **The roadmap is the specification.** Never replace, simplify,
   reinterpret or silently omit its requirements. If something is
   ambiguous, say so instead of guessing.
2. **Dependency stop rule.** Do not run `apt`, `pip`, or `python3 -m venv`
   yourself. If a dependency is genuinely required, stop and report the
   package name, its source (Debian or PyPI), the reason and the exact
   command for the maintainer.
3. **Safety posture.** No real credentials in code or tests; no
   `eval()`/`exec()`; real trading stays disabled; strategies never bypass
   the risk manager; secrets are redacted in every log.
4. **Vision and mission.** Survive → validate → earn. The program never
   promises profits and must say *"no edge exists"* when that is the
   truth. Never encourage trading money needed to live.
5. **Honesty in reporting.** Only claim a test passed if you ran it. Show
   real command output. If a tool is missing, say so.
6. **The AFML book rule.** *Advances in Financial Machine Learning*
   (López de Prado, 2018) is cited by bibliographic reference only. Never
   copy its text, code, figures or tables into the repository, and never
   commit the book itself. Record technique mappings in
   [`docs/en/developers/afml-techniques.md`](docs/en/developers/afml-techniques.md).
7. **English first.** Code, primary docs, UI source strings and ADRs are
   written in English. Spanish follows through Qt Linguist
   (`pylupdate6` → `.ts` → `lrelease` → `.qm`).
8. **Small changes, tests always run, docs evolve with the code.**

---

## 5. Quality bar

- **Money is `Decimal`, time is UTC.** Naive datetimes are rejected on
  purpose. Never introduce `float` into a price, quantity or balance path.
- **No look-ahead.** A strategy sees `candles[:i]` and nothing more;
  signals fill at the **next** candle's open.
- **Statistics stay honest.** Small samples are flagged, not celebrated.
  A single in-sample backtest is an *observed result*, never evidence.
- **Fail loudly.** A silent `except: pass` that hides a bug is a
  regression (there is a test in `tests/test_optimization.py` born from
  exactly that mistake).
- **Prefer explicit over clever.** Readable, boring code that a beginner
  can follow beats a dense one-liner.
- **Beginner explanations ship with user-facing features.**

---

## 6. Good first contributions

| Task | Where |
|---|---|
| Add the missing glossary terms (asset, blockchain, wallet, spread, liquidity, out-of-sample, walk-forward, robustness…) | `docs/en/beginners/glossary.md`, chapter 24 |
| Translate the ~190 new UI strings into Spanish | `src/crypto_trading_lab/i18n/translations/crypto_trading_lab_es.ts` |
| Lesson → screen links (open the related tool from a lesson) | `src/crypto_trading_lab/ui/education/`, chapter 80 |
| Parameter sweep launched from the Strategy Builder | `src/crypto_trading_lab/ui/strategy_builder.py`, chapter 77 |
| Realistic execution (partial fills, market impact) in the paper pipeline | `paper_session.py`, chapters 56/79 |
| Beginner chart tutorials | `docs/en/beginners/`, chapter 19.2 |
| Debian package and AppImage | chapters 82, 83 |
| Property-based tests for the engine arithmetic | `tests/backtesting/` |

---

## 7. Translating (Spanish)

English is the source language; Spanish is the second. Strings are
extracted from `self.tr()` calls, so **never** hard-code a visible string.

```bash
# Refresh the .ts from the source
pylupdate6 $(find src -name '*.py') \
    -ts src/crypto_trading_lab/i18n/translations/crypto_trading_lab_es.ts

# Translate it (Qt Linguist), then compile
lrelease src/crypto_trading_lab/i18n/translations/crypto_trading_lab_es.ts
```

Untranslated entries fall back to English at runtime, so partial work is
still useful and safe.

---

## 8. Using an AI agent

If you contribute with an agent, paste
[the prompt in the README](README.md#paste-this-to-your-agent) as its
system or first message. It encodes the rules above so the agent does not
have to rediscover them.

A few practical notes:

- Give the agent the **chapter number**, not just a description.
- Ask it to **run the suite and quote the output** before it claims
  success; everything else is narration.
- Ask it to **stop** when a dependency or an ambiguity appears, rather
  than improvising.
- Review its diff as if a junior colleague wrote it. Agents are
  confidently wrong in exactly the places where a project is vague — so
  when you find one, tighten the specification too.

---

## 9. Review process

- One maintainer review is required.
- Reviewers check, in order: **correctness → tests → honesty of the
  claims → documentation → style**.
- A pull request that reports a passing suite it did not run will be
  closed. That is the one thing this project cannot tolerate.
- Disagreements about design are resolved by writing the requirement into
  `ROADMAP.md` first, then implementing it. The specification wins over
  individual preference.

---

## 10. Reporting bugs

Include:

1. the exact command you ran,
2. the real output (not a summary),
3. what you expected and what happened,
4. your Debian version, Python version and whether you are offscreen,
5. the ROADMAP chapter or file you believe owns the behaviour.

A reproducible command is worth a thousand words.

---

## 11. License

By contributing you agree that your work is released under the
**GPL-3.0** that covers this repository (see [`LICENSE`](LICENSE)).
