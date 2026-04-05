# Closed-loop AI scientist — cell culture workcell

**Data parser** — turns per-well OD CSVs + a well-to-design mapping into **`growth_metrics.json`**.  
**Webapp** — FastAPI serves that data over HTTP; a React UI browses iterations, plates, and charts.

**More detail:** [`src/parser/README.md`](src/parser/README.md) (formats, metrics, layout), [`src/webapp/README.md`](src/webapp/README.md) (API routes, frontend structure).

---

## Quick start

Minimal path from zero to dashboard (see **What you need installed** below if anything is missing):

```bash
# 1) Repo root: Python + frontend deps
uv sync
cd frontend && npm ci && cd ..

# 2) Sample data + parse (skip if you already have data/iterations/…)
uv run python scripts/generate_mock_data.py
uv run python -m src.parser data/iterations/iter_001

# 3) API (leave running)
uv run uvicorn src.webapp.main:app --reload --port 8000

# 4) In another terminal — UI
cd frontend && npm run dev
```

- **Reagent LHS design for Monomer:** run `uv sync` first (Python deps; `matplotlib` is included for `--plots`). Then from the repo root: `uv run python scripts/generate_iter_001_design.py` (the filename is legacy; the CLI is not limited to `iter_001`). **Which iteration** is chosen by the optional first argument: omit it to use `data/iterations/iter_001`, pass `iter_NNN` to use `data/iterations/iter_NNN`, or pass a path to any `iter_*` folder. Under that folder, `input/` gets `well_to_design_mapping.json`, `transfer_array.json` (validated before save), `<folder>_design_summary.md`, and with **`--plots`** the `<folder>_lhs_*.png` figures. **`--seed N`** (default `42`) fixes the Latin hypercube and well shuffle for reproducibility; change `N` for a new layout.

Open **http://localhost:5173** (UI) and **http://localhost:8000/docs** (API). The next sections spell out the same steps with options and notes.

---

## What you need installed

| Tool | Role |
|------|------|
| **Python 3.10+** | Parser + API + tests |
| **[uv](https://docs.astral.sh/uv/)** | Installs Python deps from this repo (`uv sync`, `uv run …`) |
| **Node.js 18+** and **npm** | Frontend only (`npm ci`, `npm run dev`) |

Clone the repo and work from the **repository root** (the directory that contains `pyproject.toml` and `frontend/`).

---

## Install everything (one time)

```bash
cd /path/to/closed-loop-ai-scientist-cell-culture-workcell

# Python: runtime + dev tools (pytest, ruff, mypy, httpx, …)
uv sync

# JavaScript: React app (reproducible lockfile)
cd frontend && npm ci && cd ..
```

Optional:

```bash
uv run pre-commit install   # run lint/tests on git commit
```

---

## Run the data parser

Writes **`analysis/growth_metrics.json`** under an `iter_*` folder. Input/output layout: [parser README](src/parser/README.md).

```bash
# Optional: create mock iter_* trees with CSVs + mapping (good for first try)
uv run python scripts/generate_mock_data.py

# Parse one iteration (argument = path to that iter_* directory)
uv run python -m src.parser data/iterations/iter_001

# More log output
uv run python -m src.parser data/iterations/iter_001 -v
```

Use your own `data/iterations/…` data instead of the mock script when you have it.

---

## Run the dashboard (API + UI)

Uses the same **`data/iterations/`** tree by default (or set **`WEBAPP_DATA_DIR`** — see [webapp README](src/webapp/README.md)). Open **two terminals**, both starting from the **repo root**.

**Terminal 1 — API (FastAPI + Uvicorn)**

```bash
uv run uvicorn src.webapp.main:app --reload --port 8000
```

**Terminal 2 — frontend (Vite)**

```bash
cd frontend && npm run dev
```

Then:

| URL | What |
|-----|------|
| http://localhost:5173 | React app (`/api` requests are proxied to port 8000) |
| http://localhost:8000/docs | OpenAPI / try-it UI |

---

## Tests

| Goal | Command |
|------|---------|
| Full suite + coverage report (no fail-under) | `uv run pytest` |
| Full suite + **enforce ≥88%** coverage (same as CI / pre-commit) | `uv run pytest --cov-fail-under=88` |
| Webapp API tests only (fast, no coverage noise) | `uv run pytest tests/test_webapp_api.py -q --no-cov` |
| Verbose | `uv run pytest -v` |

**Why `--no-cov` for webapp-only?** Default pytest options measure both `src/parser` and `src/webapp`. Webapp-only runs do not execute the parser, so combined coverage looks low even when tests pass. Use the full suite + `--cov-fail-under=88` for a real gate.

**From `frontend/`:** Pytest discovers tests only when the working directory is the repo root. Use:

```bash
npm run test:api      # webapp API tests, no cov
npm run test:python   # full suite + cov-fail-under=88
# or:
uv run --directory .. pytest tests/test_webapp_api.py -q --no-cov
```

Thresholds: [`pyproject.toml`](pyproject.toml).

---

## Lint & types (Python)

```bash
uv run ruff check .
uv run ruff check --fix .
uv run ruff format .
uv run ruff format --check .
uv run mypy src/
```

---

## Frontend (lint / production build)

Dev server: see **Run the dashboard** above.

```bash
cd frontend
npm run lint
npm run build    # Typecheck + production bundle
```

---

## Pre-commit & CI

After `uv run pre-commit install`: Ruff, Ruff format, mypy, full pytest with `--cov-fail-under=88`, and ESLint when you change files under `frontend/`.

```bash
uv run pre-commit run --all-files
```

**CI** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)): Python lint, format, mypy, pytest with coverage gate, and `frontend` (`npm ci`, `npm run lint`, `npm run build`) on pushes/PRs to `main`.
