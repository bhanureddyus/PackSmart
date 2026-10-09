---
name: local-dev
description: How to bring PackSmart up locally in the sandbox and verify it is healthy.
---

# Skill: local-dev (PackSmart)

Recorded by the onboarding run on 2026-10-09.

## Environment facts

- Runtime: Python 3.13.14 present in sandbox; `uv` NOT installed (README suggests it —
  fall back to `python3 -m venv` + pip).
- No database, Redis, Docker, or env secrets required. Data is CSV on disk.
- Sandbox platform runs its own uvicorn on port 49999 from `/root/.server` — unrelated
  to this repo; never kill it and never verify against that port.
- No lint/typecheck/test tooling is configured in the repo (no pytest/ruff/mypy files).

## Steps that worked

1. `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
   → fastapi 0.143.0, uvicorn 0.54.0. Venv must be at repo root named `.venv`
   because `run.sh` sources `.venv/bin/activate`.
2. Start detached: `nohup ./run.sh > /tmp/packsmart-dev.log 2>&1 &`
   Caveat: the background process can hold the tool stream open until the
   keep-alive timeout — the server still starts fine; just re-check in a new
   command with `cat /tmp/packsmart-dev.log` and `pgrep -af uvicorn`.
3. Parse the port from startup output, do not assume it:
   `INFO: Uvicorn running on http://0.0.0.0:8000` → port 8000.
4. Verify primary flow (all against `http://localhost:8000`):
   - `GET /api/health` → 200 `{"status":"ok","service":"packsmart-web","version":"0.1.0"}`
   - `GET /api/v1/products` → 200, JSON list from products.csv
   - `POST /api/v1/estimate` (ceramic mug, China, $15) → 200 with
     `hs_code: "6911"`, `duty_estimate: 0.9`, `recommended_box: "Medium Box"`,
     `total_cost_est: 5.15`
   - `POST /api/v1/bulk` (mug + wool sweater) → 200 with
     `summary: {count: 2, total_duty_estimate: 6.75, total_shipping_cost: 11.85, total_cost: 18.6}`
   - `GET /` → 200, SPA HTML served
5. Proof commands:
   - `.venv/bin/python -m py_compile main.py core.py` → OK
   - Engine smoke assertions (in-venv python): mug → HS 6911 / $0.90;
     wool sweater → HS 6110 / $5.85; USA origin → duty waived (0). All passed.

## Known gaps

- No browser automation available in the sandbox (no chromium/playwright), so no UI
  screenshots; verification is API-level end-to-end plus served-HTML check.
- No test suite or linter configured — nothing to run beyond the smoke assertions above.

## Restart from snapshot

Snapshot `6jin6rbyy3x0dp0vt27g:default` (2026-10-09T16:22:11.849Z) contains the
installed `.venv`. After restore: `./run.sh`, then health-check as in step 4.
