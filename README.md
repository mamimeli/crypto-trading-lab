<div align="center">

<img src="assets/logo.png" alt="Crypto Trading Lab logo" width="150"/>

# Crypto Trading Lab

**A specifications-first laboratory for honest crypto-trading research.**

Survive → Validate → Earn. In that order, non-negotiable.

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52?logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![Tests: 1015 passed, 2 skipped](https://img.shields.io/badge/tests-1015%20passed%2C%202%20skipped-brightgreen)](#test-baseline)
[![CI](https://github.com/wachin/crypto-trading-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/wachin/crypto-trading-lab/actions/workflows/tests.yml)
[![Platform: Debian 13](https://img.shields.io/badge/platform-Debian%2013-A81D33?logo=debian&logoColor=white)](#dependencies)
[![Method: AFML](https://img.shields.io/badge/method-L%C3%B3pez%20de%20Prado%20(2018)-purple)](docs/en/developers/afml-techniques.md)
[![Real trading: DISABLED](https://img.shields.io/badge/real%20trading-DISABLED-critical)](#safety-by-construction)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-7dd3fc.svg)](CONTRIBUTING.md)
[![Built agent-first](https://img.shields.io/badge/built-agent--first-8b5cf6.svg)](CONTRIBUTING.md)
[![Discussions](https://img.shields.io/badge/Discussions-ask%20%26%20share-6e40c9?logo=github&logoColor=white)](https://github.com/wachin/crypto-trading-lab/discussions)

</div>

---

## Contributing — bring your AI agent

<img src="assets/contributing-agents.gif" alt="An animated crypto candlestick chart drawing itself next to the words: Crypto Trading Lab — Bring your AI agent." width="100%"/>

🤝 **This repository is built agent-first and we want your agent on the team.**

Crypto Trading Lab is not a finished product; it is a *specification with
a codebase catching up to it*. `ROADMAP.md` holds 83 chapters of
requirements — 2,828 checkboxes — and **roughly two thirds of them are
still open** (its status table counts them per chapter, so the number is
always current). Each one is small enough to land in a focused pull
request. That makes it an unusually good place for an AI agent to do
real, verifiable work: the task is already written down, the test suite
runs offline in well under a minute, and honesty is a hard rule rather
than a slogan.

You bring the agent (or your own two hands). We bring the specification,
the safety rails and a green test suite that tells you the moment you
break something.

**Where things go:** a bug with a reproducible command →
[Issues](https://github.com/wachin/crypto-trading-lab/issues); questions,
ideas, research results and show-and-tell →
[Discussions](https://github.com/wachin/crypto-trading-lab/discussions).

### Read these five files, in this order

| # | File | Why it matters |
|---|---|---|
| 0 | [`CLAUDE.md`](CLAUDE.md) | Auto-loaded by Claude Code and other agent tools at session start; points to the files below |
| 1 | [`AGENT-HANDOFF.md`](AGENT-HANDOFF.md) | What exists today and the exact continuation point |
| 2 | [`AGENTS.md`](AGENTS.md) | The non-negotiable ground rules |
| 3 | [`ROADMAP.md`](ROADMAP.md) | **The specification** — find the chapter that owns your task |
| 4 | [`CONTRIBUTING.md`](CONTRIBUTING.md) | Workflow, review expectations, how to open a good PR |

### Paste this to your agent

```text
You are contributing to Crypto Trading Lab, a specifications-first
cryptocurrency research laboratory. Follow these rules exactly.

1. Read AGENT-HANDOFF.md (current state + continuation point), then
   AGENTS.md (non-negotiable rules), then the ROADMAP.md chapter that
   owns the task. Do not start before reading them.
2. ROADMAP.md is the specification. Never replace, simplify, reinterpret
   or silently omit its requirements. If something is ambiguous, stop and
   say so explicitly instead of guessing.
3. Make small changes. After every change run:
       QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q
    and check the command's EXIT CODE is 0, not only the printed count
    (baseline: 1015 passed, 2 skipped). If either changes, report it: a
    suite that prints "passed" and exits non-zero is a bug, not a detail.
4. Do NOT install dependencies. If one is genuinely needed, STOP and
   report: package name, source (Debian or PyPI), reason, and the exact
   command the human must run. Never run apt or pip yourself.
5. Safety: no real credentials, no eval()/exec(), real trading stays
   disabled, strategies never bypass the risk manager, secrets are
   redacted in every log.
6. English is the source language for code, docs and UI strings. Mark
   every visible string with self.tr() and update the documentation in the
   same change as the code.
7. Report honestly. Only claim a test passed if you actually ran it, and
   show the real command output. If something cannot be tested, say so.
   Do not leave report files at the repository root: the English
   documents under docs/en/developers/ (index: README.md there) and the
   CHANGELOG are where findings belong.
8. Work on a branch, keep commits focused, and tick a ROADMAP checkbox
   only when the requirement is implemented AND tested.
9. Verify the claims you inherit. A previous agent's report is a lead, not
   evidence: re-run the command behind every claim you depend on. In
   October 2026 a report stated "no files were deleted" after deleting
   four, and quoted a README sentence that does not exist; both were
   caught by reading the repository instead of the report.
10. Measured, not assumed. Write "verified on <platform>" only for a
    platform someone actually ran. Debian 13 and Windows 10 are verified;
    macOS is deliberately postponed to the end of development (after Linux
    and Windows), so do not treat it as the next task. The manual
    `cross-platform` workflow is what turns a platform into a result when
    its turn comes.
```

> **Working with a smaller context window?** The project is measured for it:
> the prescribed startup reading costs roughly **7,000 tokens**, no task
> needs all of `ROADMAP.md` (one chapter is 46 lines on average), and the
> test suite is offline, so verification is cheap. See
> [`docs/en/developers/small-context-contributing.md`](docs/en/developers/small-context-contributing.md).

### Ways to help — code optional

- **Research / code** — implement an open ROADMAP chapter. The "Ahead"
  list below and Part XVI mark the frontiers.
- **Documentation** — the beginner guides in `docs/en/beginners/` are the
  product's teaching arm; clarity there is a feature.
- **Translations** — English is the source; Spanish ships through Qt
  Linguist. There are ~190 new strings waiting in
  `src/crypto_trading_lab/i18n/translations/crypto_trading_lab_es.ts`.
- **Testing** — financial regression tests and property-based tests for
  the engine are always welcome; hand-verified arithmetic beats coverage
  theatre.
- **Packaging** — the Debian package (chapter 82), AppImage (chapter 83)
  and reproducible builds.
- **Accessibility & i18n** — keyboard navigation, screen-reader labels,
  translated documentation.
- **Honest bug reports** — a failing command plus its real output is worth
  more than a paragraph of description.
- **Pick up a known gap** —
  [`docs/en/developers/unwired-modules-audit.md`](docs/en/developers/unwired-modules-audit.md)
  records every module that was found unwired, with a decision and its
  evidence. All 16 are resolved, and the chapter 22 CLI now really runs
  its commands; the newest open item is the execution model in the
  backtest engine (chapter 56.5).
- **Verify another platform** — run the manual
  [`cross-platform` workflow](.github/workflows/cross-platform.yml) on
  Ubuntu, macOS or Windows; it installs the package and runs the suite on
  all three. Windows 10 is done; **macOS is deliberately left for the end
  of development**, once Linux and Windows are finished (see
  [What is verified, and what is not](#what-is-verified-and-what-is-not)).

### What you get out of it

This is not only a place to be useful. It is an unusually good place to
learn the material that most repositories only gesture at:

- **The techniques have names, definitions and tests.** Purged and
  embargoed cross-validation, the deflated Sharpe ratio, the probability of
  backtest overfitting, triple-barrier labelling and meta-labelling are
  specified in
  [`afml-techniques.md`](docs/en/developers/afml-techniques.md) and mapped
  to the chapters that implement them. You build against a written
  definition, not a blog post.
- **The hard reading is already done.** Eight major projects — freqtrade,
  hummingbot, jesse, ccxt, vectorbt, backtrader, ta-lib and the AFML
  exercises — were studied in
  [`reference-projects.md`](docs/en/developers/reference-projects.md): what
  each does, what it verifiably does **not** do, and whether its licence
  lets you adapt its code. Months of reading, compressed into one document.
- **Verification is cheap and honest.** The suite is offline, runs in well
  under a minute, and *"no edge exists"* is a legitimate result here rather
  than a failed experiment.
- **You will be told when you are wrong.** Three claims that upstream
  projects advertise were disproved by reading their code during the
  reference study, and the corrections are in the repository. The same
  standard applies to your pull request — it will be checked, not waved
  through.

**Credit and licensing.** There is no CLA and no copyright assignment: the
project is GPL-3.0, you keep the copyright of your contribution, and it is
licensed under the same terms. Your work stays attributed in the git
history and is recorded in [`CHANGELOG.md`](CHANGELOG.md).

### Good first contributions

| Task | Where |
|---|---|
| Feed the chapter-56 execution model into the backtest engine too | `backtesting/engine.py`, chapter 56.5 |
| Finish the Debian packaging (stale `debian/rules`, missing dependencies) | `debian/`, chapter 82 |
| Add the missing glossary terms (asset, blockchain, wallet, spread, liquidity, out-of-sample, walk-forward, robustness…) | `docs/en/beginners/glossary.md`, chapter 24 |
| Translate the new UI strings into Spanish | `.ts` via Qt Linguist |
| Lesson → screen links in the Learning Center | `ui/education/`, chapter 80 |
| Parameter sweep launched from the Strategy Builder | `ui/strategy_builder.py`, chapter 77 |
| Beginner chart tutorials | `docs/en/beginners/`, chapter 19.2 |

> **Not on this list on purpose: macOS.** The maintainer has decided to leave
> macOS verification until the end, once the program runs on Linux and
> Windows. Do not open a macOS PR as a priority; the manual
> `cross-platform` workflow stays available for whoever gets there.

### The rules that keep this repository honest

> A profitable backtest is **not** proof of future profitability. Capital
> protection outranks profit seeking: never risk money needed to live.

- Tests are never mocked into passing, and no dependency is installed
  without the maintainer's explicit approval.
- The program must be able to conclude *"no edge exists"* — and say so.
- The AFML book is cited by bibliographic reference only; its text and
  code are never copied into this repository.
- **The repository documents its own failures.** [`CHANGELOG.md`](CHANGELOG.md)
  records that the test suite once printed "passed" and then segfaulted,
  that CI had never been able to pass, and that a documentation audit found
  16 modules wired to nothing. A project that writes those down is a
  project whose other claims are worth reading.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full workflow.

---

## Contents

- [Contributing — bring your AI agent](#contributing--bring-your-ai-agent)
- [What this is — and what it refuses to be](#what-this-is--and-what-it-refuses-to-be)
- [Quick start](#quick-start-debianubuntu-with-system-packages)
- [Install with pip — Linux, macOS and Windows](#install-with-pip--linux-macos-and-windows)
- [System architecture](#system-architecture)
- [Illustrative run (generated by this codebase)](#illustrative-run-generated-by-this-codebase)
- [The quantitative core](#the-quantitative-core-implemented-tested)
- [Safety by construction](#safety-by-construction)
- [Current state of the build](#current-state-of-the-build)
- [The journey — from learning to risking money](#the-journey--from-learning-to-risking-money)
- [Repository map](#repository-map)
- [Test baseline](#test-baseline)
- [Dependencies](#dependencies)
- [License](#license)

---

## What this is — and what it refuses to be

Crypto Trading Lab is an educational **research, backtesting and
(paper-)trading platform** for cryptocurrency markets, built for users
with scientific standards:

| It is | It is not |
|---|---|
| A measurement instrument for trading hypotheses | A signal-selling bot |
| Exact `Decimal` arithmetic, UTC, fully auditable | Floating-point promises |
| Statistically honest: small samples are *flagged*, not celebrated | A profit-guarantee machine |
| A pipeline that can conclude *"no edge exists"* — and will say so | A tool that always finds "alpha" |

The methodological backbone follows *Advances in Financial Machine
Learning* (López de Prado, 2018) — cited by **bibliographic reference
only**. Every technique brought into the codebase is specified,
reviewed and mapped in [`docs/en/developers/afml-techniques.md`](docs/en/developers/afml-techniques.md).

---

## Quick start Debian/Ubuntu with system packages

```bash
# 1. Dependencies — Debian system packages (virtualenv route: docs/en/developers/venv-setup.md)
sudo apt install python3-pyqt6 python3-pyqtgraph python3-sqlalchemy \
                 python3-platformdirs python3-pytest python3-pytestqt \
                 python3-pypdf qt6-l10n-tools

# 2. Clone (the research submodules are optional — see below)
git clone https://github.com/wachin/crypto-trading-lab
cd crypto-trading-lab

# 3. Verify the environment, then the baseline
python3 -c "import pyqtgraph, sqlalchemy, platformdirs; print('deps OK')"
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q
# → 1015 passed, 2 skipped

# 4. Run it
PYTHONPATH=src python3 -m crypto_trading_lab
```

Run step 3 **before** you change anything. The suite is offline and takes well
under a minute, so it is the cheapest way to know your setup is sound — if it
prints anything other than `1015 passed, 2 skipped`, the problem is the
environment, not your change, and it is worth fixing first. Two of those
packages are easy to leave out and neither failure looks like a missing
dependency:

- **`python3-pytestqt`** provides the `qtbot` fixture the UI tests need. The
  suite installs it as a pytest plugin, so without it those tests **error**
  rather than skip.
- **`python3-pypdf`** renders PDF reports. Without it the chapter-41 export
  test skips, the count becomes **3 skipped**, and the difference is easy to
  mistake for a test that was never written.

`qt6-l10n-tools` is only needed for the translation tooling
(`pylupdate6`/`lrelease`), not for the suite.

**Recommended first run inside the app:** `File → Get historical data…` →
`BTC/USDT`, `1 hour`, a few years → **Download**. Then `Tools → New
research…` and read the validity dashboard before believing any number.

<details>
<summary><strong>You do <em>not</em> need <code>external/</code> — the reference studies are finished</strong></summary>

**A fresh clone creates `external/` with eight empty directories, and that is
correct.** Git makes placeholder directories for submodules, so you will see
`external/ccxt`, `external/freqtrade`, … — they contain **no files** until
you fetch them, and you never need to. The eight reference projects
(freqtrade, hummingbot, jesse, ccxt, vectorbt, backtrader, ta-lib, AFML
exercises) were studied while designing this one; the study is **concluded**
and its conclusions are written down in
[`docs/en/developers/reference-projects.md`](docs/en/developers/reference-projects.md)
(Parts A–H). They are **not needed to build, run, test or contribute to the
application** — nothing in `src/`, `tests/`, `pyproject.toml` or `Makefile`
refers to them, and both CI workflows pass `submodules: false`.

Read the conclusions, not the repositories. Only fetch one if you want to
**re-verify** a specific claim, and then fetch only that one:

```bash
git submodule update --init external/freqtrade
```

**Size warning:** the working copies are 930 MB, but a fetch downloads full
history — **11 GB** for all eight, 8 GB of it `external/ccxt`. Never run
`git submodule update --init --recursive` casually.

</details>

---

## Install with pip — Linux, macOS and Windows

The [Quick start](#quick-start-debianubuntu-with-system-packages) above is the **supported** configuration:
Debian system packages, no pip. The same code also installs as an ordinary
Python package, which is what macOS and Windows need and what a Linux user
may prefer for an isolated environment.

> **What is verified.** Debian 13 with the system packages is the supported
> stack: **1015 passed, 2 skipped**. **Windows is also verified**: on Windows
> 10 with Python 3.14.7 from PyPI (2026-10-01 — clean install, the window
> opens, identical numbers) and again on 2026-10-31 with Python 3.12, after
> two platform assumptions in the suite were fixed; see
> [What is verified, and what is not](#what-is-verified-and-what-is-not).
> **macOS is deliberately left for the end of development**: the commands
> below follow from the platform and all four packages publish wheels for it,
> but nobody has run them, and that is a scheduling decision, not a missing
> result. See [What is verified, and what is not](#what-is-verified-and-what-is-not).

Requirement: **Python 3.11 or newer** (3.13 is what the suite runs on).
`pip install .` pulls the four runtime packages; the extras add the rest:

| Extra | Adds | Needed for |
|---|---|---|
| `dev` | pytest, pytest-qt | running the test suite |
| `ccxt` | ccxt | the read-only multi-exchange adapter (chapter 26) |
| `pdf` | pypdf | PDF report export (chapter 41) |
| `credentials` | keyring | storing API keys in the system keyring (chapter 9) |
| `aiohttp`, `websockets` | both | the chapter-27 live feed |

`dev` and `pdf` are the pair that reproduces the advertised baseline. Install
`".[dev]"` alone and the chapter-41 export test skips, so the run reports
**3 skipped** instead of 2. Combine extras with commas, for example
`".[dev,pdf,ccxt]"`.

### Linux (Debian/Ubuntu) with a virtualenv

Reuse the Debian Qt stack and let the venv carry only what Debian lacks:

```bash
sudo apt install python3-venv python3-pyqt6 python3-pyqtgraph \
                 python3-sqlalchemy python3-platformdirs
cd crypto-trading-lab
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q   # → 1015 passed, 2 skipped
python -m crypto_trading_lab
```

A fully isolated venv (everything from PyPI) works too:

```bash
sudo apt install python3-venv
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev,ccxt,pdf,credentials]"
```

### macOS

No system packages are needed; Apple Silicon and Intel both have wheels.

```bash
# Python 3.11+: brew install python@3.13   (or the python.org installer)
cd crypto-trading-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,ccxt,pdf,credentials]"
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q
python -m crypto_trading_lab
```

### Windows (PowerShell)

You need python 3.12 only from: 

[https://www.python.org/downloads/release/python-3120/](https://www.python.org/downloads/release/python-3120/)

install and add to the PATH, then:

```powershell
py -3 --version
cd $HOME\Dev\crypto-trading-lab
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-all.txt
python -m pip install -e ".[dev,ccxt,pdf,credentials]"
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest tests/ -q   # → 1015 passed, 2 skipped
python -m crypto_trading_lab
```

On Windows there is no `python3`: use `py -3` or `python`. Paths use `\`,
the activation script lives in `.venv\Scripts\`, and the installed command
is `.venv\Scripts\crypto-trading-lab.exe`.

The window prints two lines that are not errors and need no action:

```text
QFontDatabase: Cannot find font directory ...\PyQt6\Qt6\lib\fonts.
This plugin does not support propagateSizeHints()
```

Qt no longer ships fonts in its wheel, so it falls back to the system font
index and says so; `propagateSizeHints()` is the offscreen platform plugin
reporting a call it ignores. The window opens and behaves normally.

`QT_QPA_PLATFORM=offscreen` is what the tests need: it runs Qt **without a
display**, so the app starts but shows no window. Clear it in the same
window before launching if you want to see the interface:

```powershell
Remove-Item Env:QT_QPA_PLATFORM
python -m crypto_trading_lab
```

#### The activation error, and the safe fix

PowerShell blocks the activation script by default:

```text
.\.venv\Scripts\Activate.ps1 : File ... cannot be loaded because running
scripts is disabled on this system.
```

Its execution policy is `Restricted`. Allow it **for this window only**:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

`-Scope Process` is the important part: the change applies to the current
PowerShell session and nothing else — no administrator rights, nothing
persisted, and it reverts when the window closes. Do **not** run
`Set-ExecutionPolicy Unrestricted` machine-wide.

If you would rather not touch the policy at all, call the interpreter
directly (this is exactly what CI does):

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest tests/ -q
.\.venv\Scripts\python.exe -m crypto_trading_lab
```

`cmd.exe` (`.venv\Scripts\activate.bat`) and Git Bash
(`source .venv/Scripts/activate`) avoid the policy entirely too.


#### Why Windows requires Python 3.12 specifically — not 3.13+, and never 3.15

On Windows, use **Python 3.12.x** to install this project. It is the version
the Windows install is measured against, and it is the one that makes the
whole dependency set install without a C++ compiler.

**Why not a newer Python (3.13, 3.14, 3.15)?**

Newer Python releases are attractive, but on Windows they turn a simple
`pip install` into a source-compilation exercise. The reason is wheels:
`pip` installs a package from a *prebuilt binary* (a `.whl`) when one exists
for your Python version, and falls back to downloading the *source tarball*
(a `.tar.gz`) and compiling it when one does not. New Python versions ship
before the ecosystem has caught up, so a large part of the dependency graph
has no wheel yet — and every package without a wheel has to be compiled
locally.

That is exactly what happens on Python 3.15. During `pip install
-r requirements-all.txt`, packages such as `cffi`, `cryptography`,
`SQLAlchemy`, `aiohttp` and `zlib-ng` arrive as source tarballs instead of
wheels. Compiling them requires **Microsoft Visual C++ Build Tools 14.0 or
greater**, and without it the install stops with:

```text
distutils.compilers.errors.PlatformError:
Microsoft Visual C++ 14.0 or greater is required.
Get it with "Microsoft C++ Build Tools":
https://visualstudio.microsoft.com/visual-cpp-build-tools/
ERROR: Failed to build 'cffi' when getting requirements to build wheel
```

Even after installing those Build Tools (several GB), the build remains
slow, fragile and easy to break on unrelated issues. It is avoidable
work.

**What Python 3.12 changes.** For 3.12, every package this project needs
publishes a wheel for Windows, so `pip` downloads binaries and never
invokes a compiler. No Visual C++ Build Tools are required, the install
finishes in seconds rather than minutes, and the failure modes above simply
do not occur. This is why the Windows instructions pin `py -3.12` and why
`requirements-all.txt` installs cleanly on a fresh Windows 10 or 11 machine.

**In short:**

| Python on Windows | Wheels for the full dependency set? | Needs C++ Build Tools? |
|---|---|---|
| **3.12.x** | ✅ Yes | ❌ No |
| 3.13.x | Mostly, occasional gaps | Sometimes |
| 3.14.x | Partial | Often |
| 3.15.x | ❌ Largely missing → source builds | ✅ Yes, and still fragile |

If you already have a newer Python installed, you do not have to remove
it: create the project's virtual environment with 3.12 explicitly
(`py -3.12 -m venv .venv`) and everything runs inside it. The Windows
tutorial above does exactly that.

> Note: Python 3.12 has entered its security-fixes-only stage, so the
> python.org downloads page no longer offers an installer for the latest
> 3.12 patch. Use **Python 3.12.10**, the last release of the 3.12 series
> that ships a Windows installer. Later 3.12.x releases are source-only.

---


### What is verified, and what is not

- **Debian 13** (Python 3.13.5, system packages): verified — `980 passed,
  2 skipped`, and the process now exits `0`.
- **Windows 10/11** (10.0.19045, AMD64, Python **3.12**, packages from PyPI):
  **verified on 2026-10-01** — clean `pip` install, the window opens, the
  CSV import / backtest / paper trading numbers are *identical* to Debian,
  `ccxt` reaches the network, and the suite reported `698 passed, 2 skipped`
  at that date. The run also exposed a real bug, now fixed — see below. (The
  PowerShell transcript was removed with the `Experiments/` kit on
  2026-10-16; the measured numbers are recorded here and in
  [`CHANGELOG.md`](CHANGELOG.md).)
- **macOS**: **not verified, on purpose.** The maintainer's decision is to
  leave macOS until the end of development, once the program works on Linux
  and Windows. The tutorial below is written from the platform, not measured;
  treat the first macOS run as an experiment, not as a regression.
- **Windows note:** the activation error is real and the fix in the tutorial
  (`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`) is what the
  Windows run used.
- The first Windows run paid for itself: the suite said `698 passed` and
  then the **process died with SIGSEGV**, so `make test` and CI would have
  reported failure. The cause was `trading.py` (chapter 68 safety logic)
  importing Qt and re-initialising a `QObject` inside `deactivate()`. Both
  are fixed, and a test now asserts the module imports without Qt.
- [`.github/workflows/cross-platform.yml`](.github/workflows/cross-platform.yml)
  is a **manual** workflow (`Actions → cross-platform → Run workflow`) that
  runs the suite on Ubuntu, macOS and Windows. It never runs on push, so the
  default CI is untouched.

---

## System architecture

```mermaid
flowchart TD
    A[Exchange adapters<br/>Mock · CCXT read-only · Binance REST] -->|validated candles| B[Market Data<br/>CSV importer · versioned datasets · SQLite]
    B --> C[Indicators<br/>SMA · EMA · RSI · BB · ATR · ROC]
    C --> D[Strategies<br/>SMA crossover · executable rules · buy-and-hold · null]
    D --> E[Backtesting Engine<br/>next-open fills · fees · spread · slippage<br/>no look-ahead by construction]
    E --> F[Performance Metrics<br/>returns · trades · risk · validity warnings]
    F --> G[Research Workflow<br/>wizard · validity dashboard · qualification]
    G --> H[Experiment Manager<br/>notebook · journal · datasets]
    B --> I[UI — PyQt6<br/>charts · Backtesting Lab · Learning Center · Paper Trading]
    E --> I
    G --> I
```

The execution pipeline every strategy must pass through:

```
        Historical market data (validated, Decimal, UTC)
                          │
                          ▼
                ┌───────────────────┐
                │ Strategy evaluates │  sees candles[:i] only —
                │ candles 0 … i      │  the future is invisible
                └─────────┬─────────┘
                          ▼
               signal at close of candle i
                          │
                          ▼
                ┌───────────────────┐
                │  Fill at the open  │  costs applied: taker fee,
                │  of candle i + 1   │  spread, slippage
                └─────────┬─────────┘
                          ▼
                ┌───────────────────┐
                │ Equity curve, full │
                │ cost attribution   │
                └─────────┬─────────┘
                          ▼
                ┌───────────────────┐
                │  Metrics + validity│  Sharpe/Drawdown/… with
                │  warnings          │  "not statistically supported"
                └─────────┬─────────┘
                          ▼
                ┌───────────────────┐
                │ Report: observed   │  never presented as proof of
                │ result, not proof  │  future profitability
                └───────────────────┘
```

---

## Illustrative run (generated by this codebase)

Both figures below were rendered by the project's own engine and
backtesting stack — **and they deliberately show a humbling case**: over
this sample the active SMA-crossover strategy *underperforms*
buy-and-hold (net P/L **+155.82 vs. +373.11**). Showing that, instead
of a cherry-picked winner, is the whole point of the laboratory.

![Equity curve and underwater plot](assets/chart-equity-drawdown.png)

![Signal mechanics](assets/chart-signals.png)

Signals are decided at a candle's **close** and filled at the **next**
candle's open — the engine cannot see the future, so neither can you.

---

## The quantitative core (implemented, tested)

All metrics are exact `Decimal` arithmetic and ship with explicit
validity flags and assumptions (ROADMAP chapter 40).

<!-- Rendering note: GitHub parses Markdown emphasis INSIDE inline math, so a
     subscript that immediately follows a brace (`\mathrm{DD}_t`) pairs with
     the next underscore and mangles the formula into <em>. Keep inline math
     in this table free of that pattern: write `DD_t`, not `\mathrm{DD}_t`.
     Verified with GitHub's markdown API; see ROADMAP chapter 40. -->

| Family | Metrics | Definitions |
|---|---|---|
| Returns | total, annualized | $R = \dfrac{E_T - E_0}{E_0}$, $\quad R_{ann} = (1+R)^{n/P} - 1$ |
| Drawdown | max, duration, average | $DD_t = \dfrac{\max_{s \le t} E_s - E_t}{\max_{s \le t} E_s}$ |
| Risk | volatility, downside | $\sigma \cdot \sqrt{n}$, $\quad \sigma^- = \sqrt{\tfrac{1}{P}\sum_{i=1}^{P} \min(r_i,0)^2}\cdot\sqrt{n}$ |
| Ratios | Sharpe, Sortino, Calmar | $SR = \dfrac{\bar r - r_f/n}{\sigma}\sqrt{n}$, $\quad Sortino = \dfrac{\bar r - r_f/n}{\sigma^-}\sqrt{n}$, $\quad Calmar = R_{ann} / DD_{max}$ |
| Trades | profit factor, expectancy | $PF = \dfrac{\sum \mathrm{wins}}{\lvert\sum \mathrm{losses}\rvert}$, $\quad \mathbb{E}[\mathrm{trade}] = \overline{\mathrm{PnL}}$ |
| Activity | turnover, fees, spread, slippage | exact per-fill attribution |

where $n$ is the number of periods per year, $P$ the number of observed
periods, $r_f$ the **annual** risk-free rate (divided by $n$ because the
ratio is computed per period), $\sigma$ the **population** standard
deviation of per-period returns, and $DD_{max}$ the worst $DD_t$. Every one
of these is implemented in
[`backtesting/metrics.py`](src/crypto_trading_lab/backtesting/metrics.py)
and pinned by tests; where a term is undefined (zero volatility, no losing
trades) the metric is reported as absent rather than as a misleading number.

**Statistical safeguards baked in:**

- annualized metrics are **suppressed** when the sample covers less
  than one year of periods;
- Sharpe/Sortino from fewer than 30 observations are labeled
  *descriptive only*;
- every report labels its **evidence level** — a single in-sample
  backtest is an *observed result*, never statistical evidence;
- the research-validity dashboard reports **liquidity realism as unmet**
  until market impact is genuinely modelled, so the laboratory never
  marks its own homework.

---

## Safety by construction

| Guard | State |
|---|---|
| Real trading | **Disabled by default**; gated behind the chapter-68 qualification pipeline |
| Money handling | `Decimal` everywhere; naive timestamps rejected; server times UTC |
| Secrets | keyring-backed storage; redacted in every log |
| Withdrawals | blocked at the adapter layer |
| Risk manager | strategies can never bypass it — paper trading included |
| Rule strategies | declarative data; no `eval`, no `exec`, no generated code |

> A profitable backtest is **not** proof of future profitability.
> Capital protection outranks profit seeking: never risk money needed
> to live.

The path from here to live data and testnet — and why real money stays
disabled — is written down in
[`docs/en/developers/live-trading-roadmap.md`](docs/en/developers/live-trading-roadmap.md).

---

## Current state of the build

✅ Implemented and tested:

- Domain models, exchange adapters (Mock + CCXT read-only), credential
  store, logging with secret redaction, SQLite persistence;
- CSV import with full validation and a pre-import summary;
- **Historical data acquisition**: download BTC/USDT (and any Binance
  Spot pair) for 1m–1d over a date range with the standard library,
  validate it (gaps, duplicates, invalid rows) and store a versioned,
  checksummed dataset;
- Indicators: SMA, EMA, RSI, Bollinger Bands, ATR, ROC;
- Deterministic backtesting engine (fees, spread, slippage, next-open);
- Performance-metric catalogue with statistical-validity warnings;
- **Research workflow**: a guided wizard (hypothesis → costs →
  backtest → benchmark → out-of-sample → robustness → walk-forward →
  qualification) that records every run as an experiment;
- **Research-validity dashboard**: an explicit checklist (dataset
  quality, look-ahead protection, costs, sample size, multiple
  testing, liquidity realism, …) before any result is trusted;
- Parameter optimization with honest multiple-testing accounting;
- Research Notebook + experiment manager (search, tags, comparison,
  export) persisted to disk;
- **Executable rule strategies**: visual builder blocks become a
  declarative rule the engine can backtest — no `eval`, no `exec`;
- **Paper trading** over a replayed real dataset with a mandatory risk
  gate and a per-trade **trading journal**;
- Strategy Complexity control and an offline Research Assistant;
- Backtesting Lab UI with beginner explanations + HTML/CSV/JSON reports;
- Candlestick charts, a **three-level Learning Center** (48 lessons with
  graded quizzes and persisted progress), bilingual UI (EN/ES);
- A **command-line interface** (chapter 22) that runs the same use cases
  as the GUI: `doctor`, `database check`, `import-csv`, `backtest`,
  `list-strategies`, `list-lessons` and `glossary search`, each doing real
  work and failing honestly (see
  [`docs/en/developers/cli.md`](docs/en/developers/cli.md)).

🚧 Ahead: everything is listed, with an honest per-item status, in
[The journey](#the-journey--from-learning-to-risking-money) below.

---

## The journey — from learning to risking money

The laboratory is built around a single path. A beginner starts at the
top; an idea only reaches the bottom if it survives **every** gate, and
the bottom is deliberately empty today.

```text
              CRYPTO TRADING LAB

                    ↓
              LEARN
                    ↓
             CHOOSE MARKET
                    ↓
              GET DATA
                    ↓
            FORM AN IDEA
                    ↓
          WRITE A HYPOTHESIS
                    ↓
              BACKTEST
                    ↓
              ANALYSE
                    ↓
           TRY TO REFUTE IT
                    ↓
          OOS / WALK-FORWARD
                    ↓
             ROBUSTNESS
                    ↓
            PAPER TRADING
                    ↓
            QUALIFICATION
                    ↓
               TESTNET
                    ↓
        ┌──────────────────┐
        │ Is there evidence │
        │ of an edge?       │
        └─────────┬─────────┘
                  ↓
            ONLY IF THERE IS
                  ↓
        CONSIDER REAL TRADING
```

**Status legend:** ✅ implemented and tested · 🟡 partial or not yet
wired · ⬜ not started.

Everything from **Learn** to **Qualification** runs today, with one
caveat: paper trading replays a downloaded dataset rather than streaming
live prices. **Testnet** and everything below it are **not built**, on
purpose — see [`docs/en/developers/live-trading-roadmap.md`](docs/en/developers/live-trading-roadmap.md).

### Phase A — "I want to sit down and learn"

1. ✅ **Finish the Learning Center** — 48 lessons across three levels
   (from zero → practical trading → quantitative research), graded
   quizzes, persisted progress, bookmarks and "continue where I left
   off". *(Remaining: lesson→screen links.)*
2. 🟡 **Improve charts and market explanation** — the candlestick chart,
   overlays and the beginner panel exist; regime analysis is implemented
   in the engine but is not surfaced in the interface.
3. ✅ **Add direct historical data** — Binance Spot public REST with the
   standard library, validated and stored as a versioned, checksummed
   dataset.
4. ✅ **Market + timeframe + period selector** — the historical-data
   screen (`BTC/USDT`, `1m`–`1d`, date range).

### Phase B — "I want to research seriously"

5. ✅ **Research Wizard** — hypothesis → costs → backtest → benchmark →
   out-of-sample → robustness → walk-forward → qualification.
6. ✅ **Strategy Builder** — block editor with validation, explanation
   and a versioned JSON rule; rules are **executable in the engine**
   without `eval`. *(Remaining: a parameter sweep launched from the
   builder itself.)*
7. ✅ **Integrated Research Notebook** — entries are full experiment
   records, not free text.
8. ✅ **Dataset versioning** — stable identity plus SHA-256 checksum per
   dataset.
9. ✅ **Experiment Manager in the GUI** — create, search, tag, annotate.
10. ✅ **Experiment comparison** — side by side, with a union of metrics.
11. ✅ **Validity / evidence dashboard** — an explicit checklist, including
    the checks that *fail*.

### Phase C — "I want to check whether an idea survives"

12. ✅ **Out-of-sample** — chronological split, degradation measured.
13. ✅ **Walk-forward** — rolling train → forward-test windows.
14. ✅ **Robustness** — Monte Carlo over trades, cost sweep, parameter
    perturbation.
15. ✅ **Multiple-testing awareness** — the number of tested
    configurations is counted and warned about.
16. ✅ **Qualification** — multi-criterion verdict, never a single number.
17. 🟡 **Paper trading with real data** — real downloaded candles are
    replayed through a mandatory risk gate with a per-trade journal. A
    **continuous** live feed (chapter 26.2) is not built yet.

### Phase D — "Maybe one day I risk money"

None of this is a promise that the day will come.

18. ⬜ **Binance WebSocket** — reconnection, rate limiting and
    stale-data detection.
19. ⬜ **Testnet** — order placement, cancellation, reconciliation.
20. 🟡 **Realistic execution** — latency, partial fills and market impact
    drive the paper-trading pipeline (chapter 56 wired 2026-09-27). The
    **backtest engine and robustness analysis still use the simple cost
    model**, so 56.5 is not complete yet.
21. ⬜ **Order and balance reconciliation**.
22. 🟡 **Kill switch** — implemented and unit-tested; never exercised
    against a live or testnet account.
23. 🟡 **Complete safety gates** — implemented and tested; the chapter-30
    pre-trade gaps remain (true tick/step size, rate limits, time
    synchronisation, idempotency, duplicate-order prevention).
24. ⬜ **Study real-trading activation** — only after 18–23 are done, and
    only through the chapter-68 flow. Until then, real trading is
    disabled by default and the application says so.

This order is the project's safety net, not a backlog. `Survive →
Validate → Earn`, and nothing skips a step: a strategy cannot jump from
`Backtested` to `Live`, and no result is presented as proof of future
profit.

---

## Repository map

| Path | Purpose |
|---|---|
| `ROADMAP.md` | **The specification** — 83 chapters, checklist-driven progress |
| `AGENT-HANDOFF.md` | Current state + exact continuation point |
| `AGENTS.md` | Non-negotiable ground rules for AI contributors |
| `CONTRIBUTING.md` | How to contribute (with or without an AI agent) |
| `CODE_OF_CONDUCT.md` | How we treat each other while we do it |
| `CHANGELOG.md` | Notable changes, newest first |
| `SECURITY.md` | Security posture and private vulnerability reporting |
| `docs/en/beginners/` | Plain-language guides (start here, glossary, indicators, metrics, paper trading) |
| `docs/en/developers/` | Indexed developer docs — ADRs, AFML specifications, threat model, live-trading roadmap ([start here](docs/en/developers/README.md)) |
| `src/crypto_trading_lab/` | Source: domain, exchanges, security, persistence, market data, indicators, backtesting, research, reporting, i18n, UI |
| `tests/` | 64 test modules — engine arithmetic is hand-verified |
| `tools/` | Asset generators (the contributor banner GIF), the ccxt evaluation script, two offline checkers (Markdown links/anchors, docstring references) and one weekly network check of the external URLs |
| `requirements-all.txt` | Every dependency for a machine without Debian packages (pip, virtualenv, Windows, macOS) |
| `Makefile` | `make test`, `make run`, `make banner`, `make translations` |
| `.github/` | CI workflow, pull-request and issue templates |
| `external/` | 8 optional reference projects as git submodules |
| `assets/` | Logo, figures and the animated contributor banner |

---

## Test baseline

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q
# → 1015 passed, 2 skipped
# → and it must exit 0
```

Do not read only the count: check the **exit code**. The suite once printed
`698 passed` and then died with a segmentation fault while the interpreter
shut down, so `make test` and CI failed while looking green.

The two skipped tests are in `tests/exchanges/contract.py:145` — they
verify the CCXT adapter contract when real trading is enabled. They are
skipped because:
- The tests require live API credentials and a network connection to
  Binance.
- The CI pipeline and local test runs are **fully offline by design** —
  no test performs real network calls (chapter 14.4).
- This keeps the suite fast, deterministic, and free of external
  dependencies.

If your count differs, **report it before changing anything** — a
drifting baseline is a bug, not a detail.

---

## Dependencies

Runtime: `python3-pyqt6`, `python3-pyqtgraph`, `python3-sqlalchemy`,
`python3-platformdirs`. The Debian package also depends on
`python3-yaml`, so YAML backtest configurations work without a virtualenv
(JSON needs nothing extra). Development adds `python3-pytest` and the Qt
Linguist tools (`qt6-l10n-tools`). Optional extras: `python3-pypdf` for
PDF reports, `python3-keyring` for credential storage, and `ccxt`
(PyPI-only) for the read-only CCXT adapter.

`pyproject.toml` declares those four runtime packages in
`[project.dependencies]`, so `pip install .` works on Linux, macOS and
Windows alike, and exposes the `dev`, `credentials`, `pdf`, `ccxt`,
`yaml`, `aiohttp` and `websockets` extras on top. On Debian the system packages
already satisfy the declared specifiers, so pip in a
`--system-site-packages` venv installs no PyPI copies of them.

The Debian-first setup above is the supported one. For the PyPI path — and
the per-platform tutorials for macOS and Windows — see
[Install with pip](#install-with-pip--linux-macos-and-windows) above and
[`docs/en/developers/venv-setup.md`](docs/en/developers/venv-setup.md),
which lists every dependency under its Debian **and** PyPI name,
troubleshoots the `pip` messages, and records the measured `ccxt`
evaluation.

The full matrix, with Debian 12/13 availability and the reasoning behind
every choice, lives in
[`docs/en/developers/debian-dependencies.md`](docs/en/developers/debian-dependencies.md).

> **Dependency stop rule:** no contributor — human or agent — installs a
> dependency. If one is needed, stop and report the package name, its
> source, the reason and the exact command for the maintainer to run.

---

## License

GPL-3.0 — see [LICENSE](LICENSE).
