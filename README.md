# PackSmart — Duty & Packaging Estimator

Import duty (HS code), packaging, and shipping cost estimator. A web-first MVP
that reuses the shared calculation engine in `core.py`.

## Run locally

    cd /opt/data/PackSmart
    uv venv .venv
    uv pip install --python .venv/bin/python -r requirements.txt
    ./run.sh

Open http://localhost:8000

## API

- `GET /` — the single-page UI
- `GET /api/health` — health check
- `GET /api/v1/products` — sample product catalogue (products.csv) as JSON
- `POST /api/v1/estimate` — estimate a single product
- `POST /api/v1/bulk` — estimate a list of products in one call (shipment-level)

### `POST /api/v1/estimate` request

```json
{
  "sku": "SKU-0001",
  "description": "Ceramic coffee mug",
  "weight_lb": 0.5,
  "length_in": 4,
  "width_in": 4,
  "height_in": 4,
  "origin_country": "China",
  "declared_value": 15.00
}
```

### `POST /api/v1/bulk` request

```json
{
  "products": [
    { "description": "Ceramic coffee mug", "weight_lb": 0.5, "length_in": 4,
      "width_in": 4, "height_in": 4, "origin_country": "China", "declared_value": 15.00 },
    { "description": "Wool sweater", "weight_lb": 0.7, "length_in": 20, "width_in": 10,
      "height_in": 5, "origin_country": "China", "declared_value": 45.00 }
  ]
}
```

Response: `{ "results": [...], "summary": { "count", "total_duty_estimate",
"total_shipping_cost", "total_cost" } }`.

## Notes

- HS lookup is keyword-based against `hs_lookup.csv` (illustrative only).
- Dimensional weight divisor = 139 (USPS/FedEx/UPS common).
- Shipping = $4 base + $0.5/lb (placeholder).
- Domestic origin (USA) import duty is waived.
