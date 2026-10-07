const catalogue = [
  { sku: "SKU001", description: "Ceramic coffee mug",                  weight_lb: 0.5,  length_in:  4, width_in:  4, height_in:  4,  origin_country: "China",  declared_value: 15.00 },
  { sku: "SKU002", description: "Wool sweater",                        weight_lb: 0.7,  length_in: 20, width_in: 10, height_in:  5,  origin_country: "China",  declared_value: 45.00 },
  { sku: "SKU003", description: "Smartphone",                          weight_lb: 0.2,  length_in:  5, width_in:  3, height_in:  1,  origin_country: "China",  declared_value: 600.00 },
  { sku: "SKU004", description: "Tea bags",                            weight_lb: 0.1,  length_in: 10, width_in:  8, height_in:  6,  origin_country: "China",  declared_value: 20.00 },
  { sku: "SKU005", description: "Desk lamp",                           weight_lb: 1.0,  length_in: 12, width_in:  8, height_in:  6,  origin_country: "USA",    declared_value: 30.00 },
  { sku: "SKU006", description: "Cotton t-shirt",                      weight_lb: 0.3,  length_in: 18, width_in: 12, height_in:  4,  origin_country: "China",  declared_value: 25.00 },
  { sku: "SKU007", description: "Pingels pot",                         weight_lb: 0.4,  length_in:  5, width_in:  5, height_in:  5,  origin_country: "China",  declared_value: 28.00 },
  { sku: "SKU008", description: "LED desk lamp",                       weight_lb: 0.1,  length_in:  8, width_in:  6, height_in:  6,  origin_country: "China",  declared_value: 35.00 },
];

const form = document.getElementById("estimate-form");
const resultCard = document.getElementById("results-card");
const resultEl = document.getElementById("result");
const resultHint = document.getElementById("result-hint");
const quickWrap = document.getElementById("quick-picks");

// Populate datalist + quick-pick chips from the catalogue.
const datalist = document.getElementById("suggestions");
catalogue.forEach((p) => {
  const opt = document.createElement("option");
  opt.value = p.description;
  datalist.appendChild(opt);

  const chip = document.createElement("button");
  chip.type = "button";
  chip.className = "chip";
  chip.textContent = p.description;
  chip.addEventListener("click", () => {
    document.getElementById("description").value = p.description;
    document.getElementById("weight_lb").value = p.weight_lb;
    document.getElementById("length_in").value = p.length_in;
    document.getElementById("width_in").value = p.width_in;
    document.getElementById("height_in").value = p.height_in;
    document.getElementById("origin_country").value = p.origin_country;
    document.getElementById("declared_value").value = p.declared_value;
  });
  quickWrap.appendChild(chip);
});

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/`/g, "&#96;");
}

function formatCurrency(value) {
  return "$" + Number(value || 0).toFixed(2);
}

function renderResult(d) {
  const {
    sku,
    description,
    origin_country,
    declared_value,
    hs_code,
    duty_rate,
    duty_estimate,
    actual_weight_lb,
    dimensional_weight_lb,
    billing_weight_lb,
    shipping_cost_est,
    total_cost_est,
    recommended_box,
    recommended_box_dims,
    notes,
  } = d;

  const o = origin_country.trim().toLowerCase();
  const domestic = o === "usa" || o === "united states" || o === "us";

  resultEl.innerHTML = `
    <div class="row"><span class="k">SKU</span><span class="v">${escapeHtml(sku)}</span></div>
    <div class="row"><span class="k">Description</span><span class="v">${escapeHtml(description)}</span></div>
    <div class="row">
      <span class="k">Origin</span>
      <span class="v ${domestic ? "muted" : ""}">${escapeHtml(origin_country)}</span>
    </div>
    <div class="row"><span class="k">Declared value</span><span class="v">${formatCurrency(declared_value)}</span></div>

    <div class="section">
      <h3 class="subsection">Harmonized System</h3>
      <div class="row"><span class="k">HS code</span><span class="v">${escapeHtml(hs_code)}</span></div>
      <div class="row"><span class="k">Duty rate</span><span class="v">${(duty_rate * 100).toFixed(1)}%</span></div>
    </div>

    <div class="section">
      <h3 class="subsection">Duty estimate</h3>
      <div class="row">
        <span class="k">Duty owed</span>
        <span class="v ${domestic ? "muted" : ""}">${domestic ? "— (domestic)" : formatCurrency(duty_estimate)}</span>
      </div>
    </div>

    <div class="section">
      <h3 class="subsection">Weight</h3>
      <div class="row"><span class="k">Actual weight</span><span class="v">${actual_weight_lb} lb</span></div>
      <div class="row"><span class="k">Dimensional weight</span><span class="v">${dimensional_weight_lb} lb</span></div>
      <div class="row"><span class="k">Billing weight</span><span class="v">${billing_weight_lb} lb</span></div>
    </div>

    <div class="section">
      <h3 class="subsection">Packaging</h3>
      <div class="row">
        <span class="k">Recommended box</span>
        <span class="v">${escapeHtml(recommended_box)} <span class="dim">(${escapeHtml(recommended_box_dims)})</span></span>
      </div>
    </div>

    <div class="section total">
      <h3 class="subsection">Estimated cost</h3>
      <div class="row"><span class="k">Shipping</span><span class="v">${formatCurrency(shipping_cost_est)}</span></div>
      <div class="row total-row"><span class="k">Total</span><span class="v">${formatCurrency(total_cost_est)}</span></div>
    </div>

    <p class="hint">${escapeHtml(notes)}</p>
  `;
}

async function estimate(e) {
  e.preventDefault();
  const payload = {
    sku: document.getElementById("sku").value.trim() || "SKU-0001",
    description: document.getElementById("description").value.trim(),
    weight_lb: parseFloat(document.getElementById("weight_lb").value),
    length_in: parseFloat(document.getElementById("length_in").value),
    width_in: parseFloat(document.getElementById("width_in").value),
    height_in: parseFloat(document.getElementById("height_in").value),
    origin_country: document.getElementById("origin_country").value.trim() || "China",
    declared_value: parseFloat(document.getElementById("declared_value").value) || 0,
  };

  if (!payload.description) {
    resultHint.textContent = "Please enter a product description.";
    resultHint.style.color = "#b00020";
    return;
  }
  const bad = [payload.weight_lb, payload.length_in, payload.width_in, payload.height_in]
    .some((n) => Number.isNaN(n) || n <= 0);
  if (bad) {
    resultHint.textContent = "Weight, length, width and height must be greater than 0.";
    resultHint.style.color = "#b00020";
    return;
  }

  try {
    const res = await fetch("/api/v1/estimate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await res.json();
    if (!res.ok) throw new Error(body.detail || "Estimate failed");
    renderResult(body.data);
    resultCard.hidden = false;
    resultHint.textContent = "";
  } catch (err) {
    resultHint.textContent = "Error: " + err.message;
    resultHint.style.color = "#b00020";
  }
}

form.addEventListener("submit", estimate);

document.getElementById("clear-btn").addEventListener("click", () => {
  form.reset();
  document.getElementById("sku").value = "SKU-0001";
  resultCard.hidden = true;
  resultHint.textContent = "";
  resultEl.innerHTML = "";
});

// Keyboard shortcut: Ctrl+Enter to estimate.
form.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    form.dispatchEvent(new Event("submit"));
  }
});
