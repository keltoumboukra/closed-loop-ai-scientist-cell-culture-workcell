<p align="center"><img src="https://raw.githubusercontent.com/keltoumboukra/closed-loop-ai-scientist-cell-culture-workcell/main/.github/assets/loopy-pr-collaborative.png" width="200"/></p>

## Summary

## How to test

## Checklist

These mirror [.github/workflows/ci.yml](.github/workflows/ci.yml). Skip what does not apply.

- [ ] **Python:** `uv run ruff check .` and `uv run ruff format --check .`
- [ ] **Python:** `uv run mypy src/` (when you change typed code under `src/`)
- [ ] **Python / tests:** `uv run pytest --cov-fail-under=88`
- [ ] **Frontend:** `cd frontend && npm run lint && npm run build` (`build` runs typecheck too)

Optional if you use hooks locally: `pre-commit run --all-files`
