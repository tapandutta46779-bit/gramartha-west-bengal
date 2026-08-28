const $ = (selector) => document.querySelector(selector);
const sectors = ["kirana", "poultry", "fishery", "food processing", "transport"];
let selectedLocality = null;

$("#search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("#status").textContent = "Searching verified locality records…";
  $("#results").replaceChildren();
  try {
    const response = await fetch(`/localities/search?q=${encodeURIComponent($("#query").value)}`);
    if (!response.ok) throw new Error(`Search failed (${response.status})`);
    const rows = await response.json();
    $("#status").textContent = rows.length ? "Choose the correct locality below." : "No match found. Try the official spelling or district.";
    rows.slice(0, 12).forEach((row) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "result-button";
      button.innerHTML = `<strong>${safe(row.locality)}</strong><span>${safe([row.block || row.municipality, row.district].filter(Boolean).join(" · "))}</span>`;
      button.addEventListener("click", () => selectLocality(row));
      const li = document.createElement("li"); li.append(button); $("#results").append(li);
    });
  } catch (error) { $("#status").textContent = error.message; }
});

function selectLocality(row) {
  selectedLocality = row;
  $("#selected-geo-id").value = row.geo_id;
  $("#identity").className = "identity selected";
  $("#identity").innerHTML = `<span>Selected</span><strong>${safe(row.locality)}</strong><small>${safe([row.block || row.municipality, row.district].filter(Boolean).join(" · "))}</small>`;
  $("#results").replaceChildren(); $("#status").textContent = "";
  $("#analyze-button").disabled = false; $("#analyze-button").textContent = "Build my plan";
}

$("#analysis-form").addEventListener("submit", async (event) => {
  event.preventDefault(); if (!selectedLocality) return;
  $("#progress-panel").classList.remove("hidden"); $("#decision").classList.add("hidden");
  $("#analyze-button").disabled = true;
  const requested = $("#sector").value;
  try {
    const payloads = [];
    if (requested === "best") {
      for (const sector of sectors) payloads.push(await runAnalysis(sector));
    } else {
      payloads.push(await runAnalysis(requested));
    }
    const usable = payloads.filter((item) => item.selected_venture && item.digital_twin);
    const ranked = (usable.length ? usable : payloads).sort(scoreDecision);
    renderDecision(ranked[0], requested === "best" ? ranked.slice(1, 3) : []);
  } catch (error) {
    $("#decision").classList.remove("hidden");
    $("#decision").innerHTML = `<div class="notice"><h2>We could not complete this estimate</h2><p>${safe(error.message)}</p></div>`;
  } finally { $("#progress-panel").classList.add("hidden"); $("#analyze-button").disabled = false; }
});

async function runAnalysis(sector) {
  const response = await fetch("/analyze", {method: "POST", headers: {"content-type": "application/json"}, body: JSON.stringify({geo_id: $("#selected-geo-id").value, capital: Number($("#capital").value), business_category: sector, catchment_radius_km: Number($("#radius").value), language: $("#language").value})});
  if (!response.ok) throw new Error(`Planning service returned ${response.status}`);
  return response.json();
}

function scoreDecision(a, b) { return (b.digital_twin?.cumulative_cash_flow ?? -Infinity) - (a.digital_twin?.cumulative_cash_flow ?? -Infinity); }

function renderDecision(p, alternatives) {
  const venture = p.selected_venture;
  if (!venture) return renderInputNeeded(p);
  const primitive = venture.primitives[0]; const twin = p.digital_twin;
  const month12 = twin?.months?.[11] || twin?.months?.at(-1);
  const gap = Math.max(0, (p.demand?.central || 0) - (p.supply?.central || 0));
  $("#decision").classList.remove("hidden");
  $("#decision").innerHTML = `
    <div class="result-head"><div><p class="eyebrow">Recommended planning case</p><h2 id="recommendation-title">${safe(labelSector(p.sector))}</h2><p>${safe(p.geography.locality)}, ${safe(p.geography.district)} · ${friendlyConfidence(p.confidence)} confidence</p></div><span class="confidence ${String(p.confidence).toLowerCase()}">${safe(p.confidence)}</span></div>
    <div class="why"><strong>Why it fits here</strong><p>A district-weighted enterprise benchmark indicates a service gap. The engine selected the smallest tested configuration that fits your own-capital limit and improves served flow.</p></div>
    <div class="metric-grid">${metric("Project cost", moneyRange(venture.investment), "planning range")}${metric("Your own capital", money(Number($("#capital").value)), "entered by you")}${metric("Financing needed", money(p.prudent_financing.illustrative_financing_requirement || 0), "illustrative")}${metric("Monthly revenue", moneyRange(month12?.revenue), "month 12 model")}${metric("Monthly cash surplus", signedMoney(month12?.operating_cash_flow), "after operating costs")}${metric("Investment payback", twin?.investment_payback_month ? `${twin.investment_payback_month} months` : "Beyond 36 months", "not operating break-even")}</div>
    <div class="two-col"><article><h3>Market opportunity</h3>${rangeRow("Modelled demand", p.demand)}${rangeRow("Modelled incumbent service", p.supply)}<div class="gapbar"><span style="width:${Math.min(100, gap / Math.max(p.demand.central, 1) * 100)}%"></span></div><p class="caption">Potential service gap: ${moneyRange(gap)}. This is a benchmark-adjusted envelope, not measured locality sales.</p></article>
      <article><h3>Minimum viable setup</h3><dl class="breakdown"><div><dt>Equipment and setup</dt><dd>${money(primitive.capex)}</dd></div><div><dt>Working capital</dt><dd>${money(primitive.working_capital)}</dd></div><div><dt>Monthly operating benchmark</dt><dd>${money(primitive.monthly_opex)}</dd></div><div><dt>People</dt><dd>${primitive.staff}</dd></div></dl></article></div>
    <article class="network"><h3>Why this venture here?</h3><div class="flow"><span>Local suppliers</span><b>→</b><span class="bottleneck">Service gap</span><b>→</b><span class="repair">Your minimum viable venture</span><b>→</b><span>More demand served</span></div></article>
    <div class="two-col"><article><h3>36-month cash plan</h3><div class="cash-chart">${cashBars(twin)}</div><p class="caption">Operating break-even: month ${twin?.operating_break_even_month || "not reached"}; cash break-even: month ${twin?.cash_break_even_month || "not reached"}.</p></article><article><h3>Start in stages</h3><ol class="stages">${p.staged_plan.map((x) => `<li>${safe(x)}</li>`).join("")}</ol></article></div>
    ${alternatives.length ? `<article><h3>Other options tested</h3><div class="alternatives">${alternatives.map((x) => `<span><strong>${safe(labelSector(x.sector))}</strong><small>${moneyRange(x.selected_venture.investment)}</small></span>`).join("")}</div></article>` : ""}`;
  renderAudit(p);
}

function renderInputNeeded(p) {
  const first = p.evidence_gates?.find((g) => g.blocking);
  $("#decision").classList.remove("hidden");
  $("#decision").innerHTML = `<div class="notice"><p class="eyebrow">One more input needed</p><h2>We can complete your estimate with one additional local input.</h2><p>${safe(first?.message || "This locality does not yet have enough linked evidence for that sector.")}</p><p>Try “Find the best opportunity” or another sector while this evidence is collected.</p></div>`;
  renderAudit(p);
}

function renderAudit(p) {
  $("#audit-content").innerHTML = `<p><strong>Method:</strong> ${safe(p.methodology_version)} · ${safe(Object.values(p.model_versions).join(" · "))}</p><p><strong>Estimate status:</strong> ${safe(p.demand?.status)}. ${safe((p.demand?.notes || []).join(" "))}</p><p><strong>Evidence gates:</strong> ${safe((p.evidence_gates || []).map((g) => g.message).join(" ") || "None")}</p><p><strong>Sources:</strong></p><ul>${p.sources.map((url) => `<li><a href="${safe(url)}" target="_blank" rel="noreferrer">${safe(url)}</a></li>`).join("")}</ul>`;
}

function metric(label, value, note) { return `<div class="metric"><span>${label}</span><strong>${value}</strong><small>${note}</small></div>`; }
function rangeRow(label, x) { return `<div class="range-row"><span>${label}</span><strong>${money(x?.lower)}–${money(x?.upper)}</strong><small>${safe(x?.status || "unknown")}</small></div>`; }
function money(value) { if (value == null || !Number.isFinite(Number(value))) return "—"; return new Intl.NumberFormat("en-IN", {style:"currency",currency:"INR",maximumFractionDigits:0}).format(value); }
function moneyRange(value) { return value == null ? "—" : `${money(value * 0.9)}–${money(value * 1.1)}`; }
function signedMoney(value) { return value == null ? "—" : `${value < 0 ? "−" : ""}${money(Math.abs(value))}`; }
function labelSector(value) { return ({kirana:"Kirana / grocery",poultry:"Poultry and egg aggregation",fishery:"Fish collection and distribution","food processing":"Small food processing",transport:"Rural distribution and aggregation",dairy:"Dairy / milk"})[value] || value; }
function friendlyConfidence(value) { return value === "HIGH" ? "High" : value === "MEDIUM" ? "Moderate" : "Early planning"; }
function cashBars(twin) { if (!twin?.months) return "<p>No projection available.</p>"; const rows = twin.months.filter((_, i) => i % 3 === 2); const max = Math.max(...rows.map((x) => Math.abs(x.closing_cash)), 1); return rows.map((x) => `<i class="${x.closing_cash < 0 ? "negative" : ""}" style="height:${Math.max(5, Math.abs(x.closing_cash) / max * 100)}%" title="Month ${x.month}: ${money(x.closing_cash)}"></i>`).join(""); }
function safe(value) { const node = document.createElement("span"); node.textContent = value ?? ""; return node.innerHTML; }
