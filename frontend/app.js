const form = document.querySelector("#search-form");
const query = document.querySelector("#query");
const status = document.querySelector("#status");
const results = document.querySelector("#results");
const evidence = document.querySelector("#evidence");
const identity = document.querySelector("#identity");
const recordCount = document.querySelector("#record-count");
const analysisForm = document.querySelector("#analysis-form");
const selectedGeoId = document.querySelector("#selected-geo-id");
const analyzeButton = document.querySelector("#analyze-button");
const analysisStatus = document.querySelector("#analysis-status");
const decision = document.querySelector("#decision");
const decisionState = document.querySelector("#decision-state");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.textContent = "Searching verified locality records…";
  results.replaceChildren();
  try {
    const response = await fetch(`/localities/search?q=${encodeURIComponent(query.value)}`);
    if (!response.ok) throw new Error(`Search failed (${response.status})`);
    const localities = await response.json();
    status.textContent = localities.length
      ? `${localities.length} matching localities.`
      : "No verified locality match. Try a source spelling or district name.";
    for (const locality of localities) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "result-button";
      button.innerHTML = `<strong>${escapeText(locality.locality)}</strong><span>${escapeText(
        [locality.block || locality.municipality, locality.district].filter(Boolean).join(" · "),
      )}</span>`;
      button.addEventListener("click", () => showEvidence(locality));
      const item = document.createElement("li");
      item.append(button);
      results.append(item);
    }
  } catch (error) {
    status.textContent = error.message;
  }
});

async function showEvidence(locality) {
  selectedGeoId.value = locality.geo_id;
  analyzeButton.disabled = false;
  analyzeButton.textContent = "Run analysis";
  identity.classList.remove("empty");
  identity.innerHTML = `<strong>${escapeText(locality.locality)}</strong><span>${escapeText(
    locality.geo_id,
  )}</span><span>${escapeText(locality.locality_type)} · ${escapeText(locality.district)}</span>`;
  evidence.replaceChildren();
  recordCount.textContent = "Loading…";
  const response = await fetch(`/evidence/${encodeURIComponent(locality.geo_id)}`);
  const payload = await response.json();
  recordCount.textContent = `${payload.records.length} records`;
  for (const record of payload.records) {
    const card = document.createElement("article");
    card.className = "evidence-card";
    card.innerHTML = `
      <p>${escapeText(record.variable.replaceAll("_", " "))}</p>
      <strong>${escapeText(String(record.value))} ${escapeText(record.unit)}</strong>
      <dl>
        <div><dt>Type</dt><dd>${escapeText(record.evidence_type)}</dd></div>
        <div><dt>Confidence</dt><dd>${escapeText(record.confidence)}</dd></div>
        <div><dt>Source</dt><dd>${escapeText(record.source_id)}</dd></div>
      </dl>`;
    evidence.append(card);
  }
}

analysisForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selectedGeoId.value) return;
  analysisStatus.textContent = "Resolving evidence and running deterministic engines…";
  analyzeButton.disabled = true;
  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        geo_id: selectedGeoId.value,
        capital: Number(document.querySelector("#capital").value),
        business_category: document.querySelector("#sector").value,
        catchment_radius_km: Number(document.querySelector("#radius").value),
        language: document.querySelector("#language").value,
      }),
    });
    if (!response.ok) throw new Error(`Analysis failed (${response.status})`);
    const payload = await response.json();
    renderDecision(payload);
    analysisStatus.textContent = `Analysis ${payload.analysis_id} completed without hiding evidence gates.`;
  } catch (error) {
    analysisStatus.textContent = error.message;
  } finally {
    analyzeButton.disabled = false;
  }
});

function renderDecision(payload) {
  decision.classList.remove("empty");
  decisionState.textContent = payload.status;
  const gates = payload.evidence_gates.length
    ? payload.evidence_gates
        .map(
          (gate) =>
            `<li><strong>${escapeText(gate.code)}</strong><span>${escapeText(gate.message)}</span></li>`,
        )
        .join("")
    : "<li>No blocking evidence gate.</li>";
  const catchment = payload.catchment?.entity_count
    ? `${payload.catchment.entity_count} OSM proxy entities in ${payload.catchment.radius_km} km`
    : "Not computed";
  const finance = payload.official_finance?.[0];
  decision.innerHTML = `
    <div class="decision-summary">
      <div><span>Status</span><strong>${escapeText(payload.status)}</strong></div>
      <div><span>Confidence</span><strong>${escapeText(payload.confidence)}</strong></div>
      <div><span>Catchment</span><strong>${escapeText(catchment)}</strong></div>
      <div><span>OSM competitor proxy</span><strong>${escapeText(String(payload.competition?.osm_proxy_count ?? "Unknown"))}</strong></div>
    </div>
    <h3>Explanation</h3><p>${escapeText(payload.explanation.summary)}</p>
    <h3>Evidence gates</h3><ul class="gate-list">${gates}</ul>
    <h3>Demand / supply / price</h3>
    <pre>${escapeText(JSON.stringify({ demand: payload.demand, supply: payload.supply, price: payload.price }, null, 2))}</pre>
    <h3>Graph and decision</h3>
    <pre>${escapeText(JSON.stringify({ graph: payload.economic_graph_summary, bottlenecks: payload.bottlenecks, selected_mvv: payload.selected_venture }, null, 2))}</pre>
    <h3>Official finance screening</h3>
    <p>${finance ? `${escapeText(finance.scheme_name)} · ${escapeText(finance.category || "outside category")} · ${escapeText(finance.status_wording)}` : "No scheme screening."}</p>
    <h3>Limitations and sources</h3>
    <ul>${payload.limitations.map((item) => `<li>${escapeText(item)}</li>`).join("")}</ul>
    <ul>${payload.sources.map((item) => `<li><a href="${escapeText(item)}" target="_blank" rel="noreferrer">${escapeText(item)}</a></li>`).join("")}</ul>`;
}

function escapeText(value) {
  const node = document.createElement("span");
  node.textContent = value ?? "";
  return node.innerHTML;
}
