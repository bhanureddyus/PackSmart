"""Core tariff / duty estimation + packaging logic for PackSmart MVP.

Extracted from main.py so the web app (and the CLI) can share a single source
of truth for the calculation. This is the single place the HS matching and
box/weight math live.
"""

import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HS_FILE = BASE_DIR / "hs_lookup.csv"
PRODUCT_FILE = BASE_DIR / "products.csv"

# (length, width, height, label) – smallest box that fits the product + 1" padding
BOXES = [
    (6.0, 6.0, 2.0, "Small Box"),
    (8.0, 8.0, 4.0, "Small-Medium Box"),
    (10.0, 10.0, 5.0, "Medium Box"),
    (12.0, 12.0, 8.0, "Large Box"),
    (14.0, 14.0, 10.0, "Extra Large Box"),
]

# Origins treated as domestic (import duty waived).
DOMESTIC_ORIGINS = {
    "usa",
    "united states",
    "united states of america",
    "us",
    "",
}

# Fallback illustrative duty rate when nothing in the HS lookup matches.
DEFAULT_DUTY_RATE = 0.25


def load_hs_lookup():
    """Read the HS code lookup CSV -> list of dicts."""
    hs_rows = []
    with open(HS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keywords = [kw.strip().lower() for kw in row["description_keywords"].split(",")]
            hs_rows.append({
                "hs_code": row["hs_code"],
                "keywords": keywords,
                "duty_rate": float(row["duty_rate"]),
            })
    return hs_rows


def match_hs_code(description, hs_rows):
    """Return best matching (hs_code, duty_rate) for a free-text description."""
    desc = description.lower()
    best_hs = None
    best_score = 0
    for hs in hs_rows:
        score = sum(1 for kw in hs["keywords"] if kw in desc)
        if score > best_score:
            best_score = score
            best_hs = hs
    # Only return a real match when at least one keyword overlaps.
    if best_hs is None or best_score == 0:
        return None, DEFAULT_DUTY_RATE
    return best_hs["hs_code"], best_hs["duty_rate"]


def is_domestic(origin_country):
    return origin_country.lower().strip() in DOMESTIC_ORIGINS


def recommend_box(length, width, height):
    """Recommend the smallest box that fits the product + 1" padding."""
    needed_len = length + 1.0
    needed_wid = width + 1.0
    needed_hgt = height + 1.0
    for (blen, bwid, bhgt, label) in BOXES:
        if blen >= needed_len and bwid >= needed_wid and bhgt >= needed_hgt:
            return label, blen, bwid, bhgt
    return BOXES[-1][3], BOXES[-1][0], BOXES[-1][1], BOXES[-1][2]


def calculate_shipping(billing_weight_lb):
    """Placeholder shipping cost: $4 base + $0.5 per lb."""
    return round(4.0 + 0.5 * billing_weight_lb, 2)


def estimate_product(
    sku,
    description,
    weight_lb,
    length_in,
    width_in,
    height_in,
    origin_country,
    declared_value,
):
    """Run the full estimate for a single product and return a result dict."""
    hs_code, duty_rate = match_hs_code(description, load_hs_lookup())

    domestic = is_domestic(origin_country)
    if domestic:
        duty_rate = 0.0

    volume = length_in * width_in * height_in
    dim_weight = volume / 139.0  # USPS/FedEx/UPS common divisor
    billing_weight = max(weight_lb, dim_weight)

    shipping_cost = calculate_shipping(billing_weight)
    box_label, box_len, box_wid, box_hgt = recommend_box(length_in, width_in, height_in)
    duty_estimate = round(declared_value * duty_rate, 2)
    total_cost = round(shipping_cost + duty_estimate, 2)

    return {
        "sku": sku,
        "description": description,
        "origin_country": origin_country,
        "declared_value": declared_value,
        "hs_code": hs_code or "TBD",
        "duty_rate": duty_rate,
        "duty_estimate": duty_estimate,
        "actual_weight_lb": weight_lb,
        "dimensional_weight_lb": round(dim_weight, 2),
        "billing_weight_lb": round(billing_weight, 2),
        "shipping_cost_est": shipping_cost,
        "total_cost_est": total_cost,
        "recommended_box": box_label,
        "recommended_box_dims": f"{box_len} x {box_wid} x {box_hgt} in",
        "notes": (
            "Domestic origin — import duty waived."
            if domestic
            else "Illustrative prototype. Verify HS code with a licensed broker."
        ),
    }
