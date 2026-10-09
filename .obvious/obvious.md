# PackSmart — obvious.md

Agent guidance for the **PackSmart** repo (`bhanureddyus/PackSmart`): an import duty,
packaging, and shipping cost estimator. Single FastAPI web app backed by CSV data files.
No database, no external services, no background workers.

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 (sandbox has 3.13.14) |
| Web framework | FastAPI 0.143.x + Uvicorn 0.54.x (see `requirements.txt`) |
| Data | CSV files: `hs_lookup.csv` (HS codes/duty rates), `products.csv` (sample catalogue) |
| Frontend | Vanilla JS SPA: `templates/index.html` + `static/app.js` / `static/style.css` |
| Package manager | pip in a `.venv` at repo root. README prefers `uv`; `uv` is NOT installed in the sandbox — use `python3 -m venv` + pip |
| Tests / lint | None configured (no pytest/ruff/mypy config in repo) |

## Local dev commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # install
./run.sh                                                             # start (runs uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000})
```

- App URL: `http://localhost:8000` (port comes from `$PORT`, default 8000 — confirmed in uvicorn startup output)
- `run.sh` sources `.venv/bin/activate`, so the venv must be at the repo root and named `.venv`
- To stop a stray dev server: `pkill -f 'uvicorn main:app --host 0.0.0.0 --port 8000'`
- Required env vars: none. Optional: `PORT`. The sandbox platform also runs its own
  unrelated uvicorn on port 49999 (`/root/.server`) — do not touch or confuse it with this app.

## Codebase map

Small single-app repo — full map in `.obvious/codebase-map.md`. Key files:

- `main.py` — FastAPI app, routes, Pydantic request models
- `core.py` — shared estimation engine (HS matching, box selection, cost math)
- `run.sh` — dev server entrypoint

## API surface

- `GET /` — single-page UI
- `GET /api/health` — health check → `{"status":"ok","service":"packsmart-web",...}`
- `GET /api/v1/products` — sample catalogue from `products.csv`
- `POST /api/v1/estimate` — single-product estimate
- `POST /api/v1/bulk` — multi-product shipment estimate with summary totals

## Local verification

1. Start the server (`./run.sh`), wait for `Uvicorn running on http://0.0.0.0:8000` in the log.
2. `curl http://localhost:8000/api/health` → expect HTTP 200 `{"status":"ok"}`.
3. `POST /api/v1/estimate` with a ceramic mug payload → expect `hs_code: "6911"`,
   `duty_estimate: 0.9`, `recommended_box: "Medium Box"` (values from `hs_lookup.csv`).
4. `POST /api/v1/bulk` with 2 products → expect `summary.count: 2` and non-zero totals.
5. Engine smoke test: `core.estimate_product` for a USA origin returns `duty_estimate: 0`.

Reference implementation of the smoke assertions lives in
`.obvious/skills/local-dev/SKILL.md`.

## Snapshot

- Snapshot ID: `6jin6rbyy3x0dp0vt27g:default`
- Captured: 2026-10-09T16:22:11.849Z
- State: venv installed, dev server verified healthy on port 8000
