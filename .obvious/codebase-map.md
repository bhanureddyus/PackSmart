# PackSmart codebase map

Single FastAPI app, no sub-apps. Depth capped at 2.

| Path | Type | Purpose |
|---|---|---|
| `main.py` | file | FastAPI app: routes (`/`, `/api/health`, `/api/v1/products`, `/api/v1/estimate`, `/api/v1/bulk`), Pydantic request models, static mount |
| `core.py` | file | Shared estimation engine: HS-code keyword matching (`hs_lookup.csv`), box selection (5 box sizes), dimensional weight (divisor 139), shipping/duty math, domestic-origin waiver |
| `run.sh` | file | Dev entrypoint: activates `.venv`, runs `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}` |
| `requirements.txt` | file | Dependencies: `fastapi`, `uvicorn` (unpinned) |
| `hs_lookup.csv` | data | HS code lookup: 5 rows of keyword → hs_code → duty_rate |
| `products.csv` | data | Sample product catalogue served by `GET /api/v1/products` |
| `templates/index.html` | file | Single-page UI (form, quick picks, results) served by `GET /` |
| `static/` | dir | Frontend assets: `app.js` (form logic, API calls), `style.css` |
| `preview/` | dir | `prototype_preview.html` — static prototype preview, not served by the app |
