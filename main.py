import os
import csv
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import core

app = FastAPI(title="PackSmart MVP", version="0.1.0")

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)


class EstimateRequest(BaseModel):
    sku: str = "SKU-0001"
    description: str = Field(..., min_length=1, description="Free-text product description")
    weight_lb: float = Field(..., gt=0, description="Actual weight in pounds")
    length_in: float = Field(..., gt=0, description="Length in inches")
    width_in: float = Field(..., gt=0, description="Width in inches")
    height_in: float = Field(..., gt=0, description="Height in inches")
    origin_country: str = "China"
    declared_value: float = Field(..., ge=0, description="Declared value in USD")


class BulkEstimateRequest(BaseModel):
    products: list[EstimateRequest]


@app.get("/")
def read_root():
    return FileResponse(Path(__file__).resolve().parent / "templates" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "packsmart-web", "version": "0.1.0"}


@app.post("/api/v1/estimate")
def estimate(req: EstimateRequest):
    try:
        result = core.estimate_product(
            sku=req.sku,
            description=req.description,
            weight_lb=req.weight_lb,
            length_in=req.length_in,
            width_in=req.width_in,
            height_in=req.height_in,
            origin_country=req.origin_country,
            declared_value=req.declared_value,
        )
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "data": result}


@app.get("/api/v1/products")
def list_products():
    """Serve the sample product catalogue (products.csv) as JSON for bulk upload."""
    products = []
    with open(core.PRODUCT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)
    return {"ok": True, "products": products}

@app.post("/api/v1/bulk")
def bulk_estimate(req: BulkEstimateRequest):
    """Estimate a list of products in one call (shipment-level)."""
    results = []
    for p in req.products:
        try:
            results.append(core.estimate_product(
                sku=p.sku,
                description=p.description,
                weight_lb=p.weight_lb,
                length_in=p.length_in,
                width_in=p.width_in,
                height_in=p.height_in,
                origin_country=p.origin_country,
                declared_value=p.declared_value,
            ))
        except Exception as exc:  # pragma: no cover - defensive
            results.append({"error": str(exc), "sku": p.sku})

    total_duty = round(sum(r.get("duty_estimate", 0.0) for r in results if "error" not in r), 2)
    total_shipping = round(sum(r.get("shipping_cost_est", 0.0) for r in results if "error" not in r), 2)
    total_cost = round(sum(r.get("total_cost_est", 0.0) for r in results if "error" not in r), 2)

    return {
        "ok": True,
        "results": results,
        "summary": {
            "count": len(results),
            "total_duty_estimate": total_duty,
            "total_shipping_cost": total_shipping,
            "total_cost": total_cost,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
