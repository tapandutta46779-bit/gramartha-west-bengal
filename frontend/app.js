const form = document.querySelector("#search-form");
const query = document.querySelector("#query");
const status = document.querySelector("#status");
const results = document.querySelector("#results");
const evidence = document.querySelector("#evidence");
const identity = document.querySelector("#identity");
const recordCount = document.querySelector("#record-count");

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

function escapeText(value) {
  const node = document.createElement("span");
  node.textContent = value ?? "";
  return node.innerHTML;
}
