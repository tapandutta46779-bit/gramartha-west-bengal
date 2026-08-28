const $ = (selector) => document.querySelector(selector);
const sectors = [
  "kirana", "poultry", "fishery", "food processing", "flour mill",
  "spice processing", "mustard oil", "household goods", "electronics", "transport",
];
let selectedLocality = null;
let searchTimer = null;
let searchSequence = 0;

initializeDistricts();

async function initializeDistricts() {
  try {
    const response = await fetch("/districts");
    if (!response.ok) throw new Error(`District service returned ${response.status}`);
    const payload = await response.json();
    $("#district").innerHTML = '<option value="">Select district…</option>' + payload.districts.map((district) => `<option value="${safe(district)}">${safe(displayDistrict(district))}</option>`).join("");
  } catch (error) {
    $("#district").innerHTML = '<option value="">Districts unavailable</option>';
    $("#status").textContent = error.message;
  }
}

$("#district").addEventListener("change", () => {
  selectedLocality = null; $("#selected-geo-id").value = ""; $("#results").replaceChildren();
  $("#identity").className = "identity empty"; $("#identity").textContent = "No canonical locality selected yet.";
  $("#analyze-button").disabled = true; $("#analyze-button").textContent = "Select your area first";
  $("#query").value = ""; $("#status").textContent = $("#district").value ? `Now type a locality inside ${displayDistrict($("#district").value)}.` : "Select a district before searching.";
});

$("#search-form").addEventListener("submit", async (event) => { event.preventDefault(); await searchLocalities(); });
$("#query").addEventListener("input", () => {
  clearTimeout(searchTimer);
  if (!$("#district").value) { $("#status").textContent = "Select a district first so duplicate locality names stay unambiguous."; return; }
  if ($("#query").value.trim().length < 2) { $("#results").replaceChildren(); $("#status").textContent = "Type at least two letters."; return; }
  $("#status").textContent = "Searching as you type…";
  searchTimer = setTimeout(searchLocalities, 250);
});

async function searchLocalities() {
  const query = $("#query").value.trim(); const district = $("#district").value;
  if (!district) { $("#status").textContent = "Select a district before searching."; return; }
  if (query.length < 2) return;
  const sequence = ++searchSequence;
  $("#status").textContent = "Searching verified locality records…"; $("#results").replaceChildren();
  try {
    const response = await fetch(`/localities/search?q=${encodeURIComponent(query)}&district=${encodeURIComponent(district)}&limit=30`);
    if (!response.ok) throw new Error(`Search failed (${response.status})`);
    const rows = await response.json(); if (sequence !== searchSequence) return;
    $("#status").textContent = rows.length ? `${rows.length} canonical matches inside ${displayDistrict(district)}.` : "No match in this district. Try the official spelling or a nearby block/municipality.";
    rows.slice(0, 15).forEach((row) => {
      const button = document.createElement("button"); button.type = "button"; button.className = "result-button";
      button.innerHTML = `<strong>${safe(row.locality)}</strong><span>${safe(hierarchy(row))}</span><em>${safe(friendlyType(row.locality_type))}</em>`;
      button.addEventListener("click", () => selectLocality(row)); const li = document.createElement("li"); li.append(button); $("#results").append(li);
    });
  } catch (error) { if (sequence === searchSequence) $("#status").textContent = error.message; }
}

function selectLocality(row) {
  selectedLocality = row; $("#selected-geo-id").value = row.geo_id;
  $("#identity").className = "identity selected";
  $("#identity").innerHTML = `<span>Selected</span><strong>${safe(row.locality)}</strong><small>${safe(hierarchy(row))} · ${safe(friendlyType(row.locality_type))}</small>`;
  $("#results").replaceChildren(); $("#status").textContent = "Canonical locality selected.";
  $("#analyze-button").disabled = false; $("#analyze-button").textContent = "Analyze my local opportunity";
}

$("#analysis-form").addEventListener("submit", async (event) => {
  event.preventDefault(); if (!selectedLocality) return;
  $("#progress-panel").classList.remove("hidden"); $("#decision").classList.add("hidden"); $("#analyze-button").disabled = true;
  const started = performance.now(); const timer = setInterval(() => { $("#elapsed").textContent = `Elapsed: ${((performance.now() - started) / 1000).toFixed(1)} seconds`; }, 100);
  const requested = $("#sector").value;
  try {
    const payloads = [];
    if (requested === "best") { for (const sector of sectors) { $("#analysis-status").textContent = `Testing ${labelSector(sector)}…`; payloads.push(await runAnalysis(sector)); } }
    else { $("#analysis-status").textContent = `Analyzing ${labelSector(requested)}…`; payloads.push(await runAnalysis(requested)); }
    const usable = payloads.filter((item) => item.selected_venture && item.digital_twin);
    const ranked = (usable.length ? usable : payloads).sort(scoreDecision);
    renderDecision(ranked[0], requested === "best" ? ranked.slice(1, 5) : []);
    $("#analysis-status").textContent = "Analysis complete";
  } catch (error) {
    $("#decision").classList.remove("hidden"); $("#decision").innerHTML = `<div class="notice"><h2>We could not complete this estimate</h2><p>${safe(error.message)}</p></div>`;
  } finally { clearInterval(timer); $("#elapsed").textContent = `Completed in ${((performance.now() - started) / 1000).toFixed(2)} seconds`; $("#progress-panel").classList.add("hidden"); $("#analyze-button").disabled = false; }
});

async function runAnalysis(sector) {
  const profile = {risk_tolerance: $("#risk-tolerance").value, minimum_monthly_income: Number($("#income-target").value || 0), experience_years: Number($("#experience").value || 0), acceptable_debt: nullableNumber($("#max-debt").value), assets: listValue($("#assets").value), skills: listValue($("#skills").value)};
  const response = await fetch("/analyze", {method: "POST", headers: {"content-type": "application/json"}, body: JSON.stringify({geo_id: $("#selected-geo-id").value, capital: Number($("#capital").value), business_category: sector, catchment_radius_km: Number($("#radius").value), language: $("#language").value, analysis_mode: $("#analysis-mode").value, profile})});
  if (!response.ok) throw new Error(`Planning service returned ${response.status}`); return response.json();
}

function scoreDecision(a, b) {
  const as = selectedScenario(a); const bs = selectedScenario(b);
  if ((bs?.scenario_survival_rate || 0) !== (as?.scenario_survival_rate || 0)) return (bs?.scenario_survival_rate || 0) - (as?.scenario_survival_rate || 0);
  return (bs?.cumulative_cash_median ?? b.digital_twin?.cumulative_cash_flow ?? -Infinity) - (as?.cumulative_cash_median ?? a.digital_twin?.cumulative_cash_flow ?? -Infinity);
}

function renderDecision(p, alternatives) {
  const venture = p.selected_venture; if (!venture) return renderInputNeeded(p);
  const primitive = venture.primitives[0]; const twin = p.digital_twin; const month12 = twin?.months?.[11] || twin?.months?.at(-1);
  const gap = Math.max(0, (p.demand?.central || 0) - (p.supply?.central || 0)); const scenario = selectedScenario(p);
  $("#decision").classList.remove("hidden");
  $("#decision").innerHTML = `
    <div class="result-head"><div><p class="eyebrow">Recommended planning case</p><h2 id="recommendation-title">${safe(labelSector(p.sector))}</h2><p>${safe(p.geography.locality)}, ${safe(displayDistrict(p.geography.district))} · ${friendlyConfidence(p.confidence)} confidence</p></div><span class="confidence ${String(p.confidence).toLowerCase()}">${safe(p.confidence)}</span></div>
    <nav class="result-tabs" aria-label="Planning report sections">${tabButton("summary","Summary",true)}${tabButton("market","Local market")}${tabButton("opportunities","Opportunities")}${tabButton("risk","Risk & SWOT")}${tabButton("plan","Business plan")}${tabButton("finance","Finance")}${tabButton("action","Action plan")}</nav>
    <div class="tab-panel active" data-panel="summary"><div class="why"><strong>Why it fits here</strong><p>The flow model found a modelled service gap and the MVV oracle selected the lowest-investment tested configuration that repairs useful flow within your capital constraint.</p></div>
      <div class="metric-grid">${metric("Project cost", moneyRange(venture.investment), "planning interval")}${metric("Monthly revenue", moneyRange(month12?.revenue), "month 12 model")}${metric("Monthly cash surplus", signedMoney(month12?.operating_cash_flow), "after operating costs")}${metric("Investment payback", twin?.investment_payback_month ? `${twin.investment_payback_month} months` : "Beyond 36 months", "not operating break-even")}${metric("Scenario survival", scenario ? percent(scenario.scenario_survival_rate) : "Quick plan", scenario ? `${scenario.scenario_count} planning scenarios` : "central estimate only")}${metric("Confidence", friendlyConfidence(p.confidence), p.demand?.status || "unknown")}</div>
      <div class="advice-grid">${adviceCard("Why it is good", gap > 0 ? `Repairs a modelled monthly service gap of ${money(gap)} within the tested network.` : "Uses a minimum-capital configuration.")}${adviceCard("Main disadvantage", scenario && scenario.scenario_survival_rate < .8 ? "Cash resilience is weak in a material share of planning scenarios." : "The locality numbers remain benchmark-adjusted rather than observed sales.")}${adviceCard("Who it suits", primitive.staff <= 2 ? "An owner-operator able to supervise daily buying, selling and cash control." : `An entrepreneur able to coordinate approximately ${primitive.staff} people.`)}${adviceCard("Who should avoid it", "Anyone unable to validate local prices and suppliers before committing capital.")}</div>
    </div>
    <div class="tab-panel" data-panel="market"><div class="two-col"><article><h3>Demand and incumbent service</h3>${rangeRow("Modelled opportunity",p.demand)}${rangeRow("Modelled incumbent service",p.supply)}<div class="gapbar"><span style="width:${Math.min(100,gap/Math.max(p.demand.central,1)*100)}%"></span></div><p class="caption">Potential service gap: ${moneyRange(gap)}. This is not measured locality turnover.</p></article><article><h3>Competition and catchment</h3>${plainRow("Likely OSM candidates",p.competition?.osm_proxy_count ?? "Not mapped")}${plainRow("Planning radius",`${p.catchment?.radius_km || $("#radius").value} km`)}${plainRow("Nearest market",p.catchment?.nearest_market?.name || "Not linked")}${plainRow("Capacity confidence",p.competition?.capacity_confidence || "Unknown")}</article></div><article class="network"><h3>Why this venture?</h3><div class="flow"><span>Suppliers</span><b>→</b><span class="bottleneck">Current service bottleneck</span><b>→</b><span class="repair">${safe(primitive.primitive_type)}</span><b>→</b><span>Additional served flow</span></div><p class="caption">Counterfactual newly served flow: ${number(p.counterfactual?.newly_served_demand)} ${safe(p.generated_graph?.unit || p.demand?.unit)}. Cannibalized existing flow: ${number(p.counterfactual?.cannibalized_existing_flow)}.</p></article></div>
    <div class="tab-panel" data-panel="opportunities"><article><h3>Options tested</h3><div class="option-table"><div class="option-row head"><span>Option</span><span>Investment</span><span>Capacity</span><span>Role</span></div>${candidateRows(p)}</div></article>${alternatives.length ? `<article><h3>Other sectors compared</h3><div class="alternatives">${alternatives.map((x,i)=>`<span><b>${i+2}</b><strong>${safe(labelSector(x.sector))}</strong><small>${moneyRange(x.selected_venture.investment)} · ${percent(selectedScenario(x)?.scenario_survival_rate)}</small></span>`).join("")}</div></article>`:""}</div>
    <div class="tab-panel" data-panel="risk"><div class="two-col"><article><h3>Computed SWOT</h3>${swot(p.swot)}</article><article><h3>Scenario resilience</h3>${plainRow("Scenarios",scenario?.scenario_count || "Quick plan")}${plainRow("Remain solvent",scenario?percent(scenario.scenario_survival_rate):"Not run")}${plainRow("Payback within 36 months",scenario?percent(scenario.payback_within_36_months_rate):"Not run")}${plainRow("10th percentile minimum cash",scenario?money(scenario.minimum_cash_p10):"Not run")}${plainRow("Worst 5% cumulative cash (CVaR)",scenario?money(-scenario.cvar95_loss):"Not run")}</article></div><article><h3>Failure boundaries — what matters most?</h3><div class="boundary-grid">${(p.failure_boundaries||[]).map(boundaryCard).join("") || "Run Deep analysis to calculate boundaries."}</div><p class="caption">Scenario rates are modelled planning survival, not probability of business success. Triangular factors are not empirically calibrated.</p></article></div>
    <div class="tab-panel" data-panel="plan"><div class="two-col"><article><h3>Minimum viable setup</h3><dl class="breakdown"><div><dt>Equipment and setup</dt><dd>${money(primitive.capex)}</dd></div><div><dt>Working capital</dt><dd>${money(primitive.working_capital)}</dd></div><div><dt>Fixed-overhead benchmark</dt><dd>${money(primitive.monthly_opex)}</dd></div><div><dt>People</dt><dd>${primitive.staff}</dd></div><div><dt>Space</dt><dd>${number(primitive.space_sqft)} sq ft</dd></div><div><dt>Service radius</dt><dd>${number(primitive.service_radius_km)} km</dd></div></dl></article><article><h3>Working-capital cycle</h3>${plainRow("Inventory days",primitive.inventory_days)}${plainRow("Receivable days",primitive.receivable_days)}${plainRow("Payable days",primitive.payable_days)}${plainRow("Cash conversion cycle",`${primitive.inventory_days+primitive.receivable_days-primitive.payable_days} days`)}<h3 class="subhead">Licences to verify</h3><ul>${(primitive.licence_assumptions||[]).map(x=>`<li>${safe(x)}</li>`).join("")}</ul></article></div></div>
    <div class="tab-panel" data-panel="finance"><div class="metric-grid">${metric("Total project cost",moneyRange(venture.investment),"CAPEX + working capital")}${metric("Your own capital",money(Number($("#capital").value)),"entered by you")}${metric("External financing",money(p.prudent_financing.illustrative_financing_requirement||0),"illustrative, not approved")}${metric("Operating break-even",twin?.operating_break_even_month?`Month ${twin.operating_break_even_month}`:"Not reached","cumulative operating cash")}${metric("Cash break-even",twin?.cash_break_even_month?`Month ${twin.cash_break_even_month}`:"Not reached","closing cash")}${metric("Payback",twin?.investment_payback_month?`Month ${twin.investment_payback_month}`:"Beyond model","owner capital recovered")}</div><article><h3>Unit economics and investment metrics</h3><div class="metric-grid">${metric("Gross margin",percent(p.prudent_financing?.financial_metrics?.gross_margin),"month 12")}${metric("Break-even volume",number(p.prudent_financing?.financial_metrics?.break_even_volume_month),"planning revenue units/month")}${metric("36-month NPV",money(p.prudent_financing?.financial_metrics?.npv_36_month_at_12pct),"12% annual discount rate")}${metric("Annualized IRR",percent(p.prudent_financing?.financial_metrics?.irr_annualized),"benchmark-adjusted assumptions")}</div><p class="caption">${safe(p.prudent_financing?.financial_metrics?.confidence_note||"")}</p></article><article><h3>36-month closing cash</h3><div class="cash-chart">${cashBars(twin)}</div></article><article><h3>Possible finance fit</h3><ul>${(p.official_finance||[]).map(x=>`<li><strong>${safe(x.scheme_name)}</strong> — ${safe(x.status_wording)}</li>`).join("")}</ul></article></div>
    <div class="tab-panel" data-panel="action"><div class="timeline">${(p.staged_plan||[]).map((x,i)=>`<div><b>${i+1}</b><p>${safe(x)}</p></div>`).join("")}</div><div class="two-col"><article><h3>Before starting</h3><ol><li>Validate two supplier quotations and the local selling price.</li><li>Confirm licences and premises suitability.</li><li>Protect the modelled working-capital buffer.</li><li>Test customer demand before buying fixed assets.</li></ol></article><article><h3>When not to start</h3><p>Do not start if the local price, supplier reliability or required cash buffer fails the boundary checks above, or if debt terms are not affordable after lender verification.</p><h3 class="subhead">Weekly metric</h3><p>Track sales volume, gross margin, inventory days and closing cash against the model.</p></article></div></div>`;
  bindTabs(); renderAudit(p);
}

function bindTabs(){ document.querySelectorAll(".result-tabs button").forEach(button=>button.addEventListener("click",()=>{document.querySelectorAll(".result-tabs button").forEach(x=>x.classList.toggle("active",x===button));document.querySelectorAll(".tab-panel").forEach(panel=>panel.classList.toggle("active",panel.dataset.panel===button.dataset.tab));})); }
function renderInputNeeded(p){const first=p.evidence_gates?.find(g=>g.blocking);$("#decision").classList.remove("hidden");$("#decision").innerHTML=`<div class="notice"><p class="eyebrow">One additional input needed</p><h2>We cannot responsibly complete this sector estimate yet.</h2><p>${safe(first?.message||"Linked evidence is insufficient.")}</p><p>Try “Find the best opportunity” while this evidence is collected.</p></div>`;renderAudit(p);}
function renderAudit(p){$("#audit-content").innerHTML=`<p><strong>Decision chain:</strong> evidence → ${safe(p.demand?.method_version)} → ${safe(p.economic_graph_summary?.builder)} → ${safe(p.baseline_flow?.solver)} → enumerated MVV → ${safe(p.digital_twin?.method_version)} → ${safe(p.robust_comparison?.method_version||"quick central estimate")}</p><p><strong>Estimate class:</strong> ${safe(p.demand?.status)}. ${safe((p.demand?.notes||[]).join(" "))}</p><p><strong>Scope:</strong> ${safe(p.robust_comparison?.scope||"No selected configuration")}. ${safe(p.robust_comparison?.calibration_status||"")}</p><p><strong>Evidence limitations:</strong> ${safe((p.evidence_gates||[]).map(g=>g.message).join(" ")||"None")}</p><details><summary>Source links</summary><ul>${p.sources.map(url=>`<li><a href="${safe(url)}" target="_blank" rel="noreferrer">${safe(url)}</a></li>`).join("")}</ul></details>`;}

function selectedScenario(p){const id=p.selected_venture?.candidate_id;return (p.robust_comparison?.candidate_summaries||[]).find(x=>x.candidate_id===id);}
function candidateRows(p){const roles={};roles[p.selected_venture.candidate_id]="Lowest viable";if(p.robust_comparison?.expected_value_winner)roles[p.robust_comparison.expected_value_winner]="Highest upside";if(p.robust_comparison?.survival_first_winner)roles[p.robust_comparison.survival_first_winner]="Survival-first";if(p.robust_comparison?.minimax_regret_winner)roles[p.robust_comparison.minimax_regret_winner]="Robust";return (p.candidate_ventures||[]).map(x=>`<div class="option-row"><span>${safe(x.candidate_id.split(":").at(-1).replace("-v1",""))}</span><span>${money(x.investment)}</span><span>${number(x.total_capacity)}</span><span>${safe(roles[x.candidate_id]||"Alternative")}</span></div>`).join("");}
function swot(data){return ["strengths","weaknesses","opportunities","threats"].map(key=>`<div class="swot-block ${key}"><strong>${key}</strong><ul>${(data?.[key]||[]).map(x=>`<li>${safe(x)}</li>`).join("")||"<li>No computed item.</li>"}</ul></div>`).join("");}
function boundaryCard(item){return `<div><strong>${safe(item.variable.replaceAll("_"," "))}</strong><span>${item.threshold==null?"No failure in tested range":`${number(item.threshold)} ${safe(item.unit)}`}</span><small>${safe(item.interpretation)}</small></div>`;}
function tabButton(id,label,active=false){return `<button type="button" data-tab="${id}" class="${active?"active":""}">${label}</button>`;}
function adviceCard(title,text){return `<article><h3>${title}</h3><p>${text}</p></article>`;}
function metric(label,value,note){return `<div class="metric"><span>${label}</span><strong>${value}</strong><small>${note}</small></div>`;}
function rangeRow(label,x){return `<div class="range-row"><span>${label}</span><strong>${money(x?.lower)}–${money(x?.upper)}</strong><small>${safe(x?.status||"unknown")}</small></div>`;}
function plainRow(label,value){return `<div class="range-row"><span>${label}</span><strong>${safe(String(value))}</strong></div>`;}
function cashBars(twin){if(!twin?.months)return"<p>No projection available.</p>";const rows=twin.months.filter((_,i)=>i%3===2);const max=Math.max(...rows.map(x=>Math.abs(x.closing_cash)),1);return rows.map(x=>`<i class="${x.closing_cash<0?"negative":""}" style="height:${Math.max(5,Math.abs(x.closing_cash)/max*100)}%" title="Month ${x.month}: ${money(x.closing_cash)}"><small>${x.month}</small></i>`).join("");}
function money(value){if(value==null||!Number.isFinite(Number(value)))return"—";return new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:0}).format(value);}
function moneyRange(value){return value==null?"—":`${money(value*.9)}–${money(value*1.1)}`;}
function signedMoney(value){return value==null?"—":`${value<0?"−":""}${money(Math.abs(value))}`;}
function percent(value){return value==null?"—":`${Math.round(value*100)}%`;}
function number(value){return value==null?"—":new Intl.NumberFormat("en-IN",{maximumFractionDigits:1}).format(value);}
function nullableNumber(value){return value===""?null:Number(value);}
function listValue(value){return value.split(",").map(x=>x.trim()).filter(Boolean);}
function hierarchy(row){return [row.ward,row.municipality,row.block,row.gram_panchayat,displayDistrict(row.district)].filter(Boolean).join(" · ");}
function friendlyType(value){return ({TOWN:"Town / municipality",WARD:"Ward",VILLAGE:"Village"})[value]||String(value||"Locality").replaceAll("_"," ").toLowerCase();}
function displayDistrict(value){return ({"North Twenty Four Parganas":"North 24 Parganas","24 Paraganas North":"North 24 Parganas","South Twenty Four Parganas":"South 24 Parganas","24 Paraganas South":"South 24 Parganas",Darjiling:"Darjeeling",Hugli:"Hooghly",Haora:"Howrah",Puruliya:"Purulia","Koch Bihar":"Cooch Behar"})[value]||value;}
function labelSector(value){return ({kirana:"Kirana / grocery",poultry:"Poultry and egg aggregation",fishery:"Fish collection and distribution","food processing":"Small food processing","flour mill":"Flour mill","spice processing":"Spice processing","mustard oil":"Mustard oil extraction","household goods":"Household-goods distribution",electronics:"Electronics / mobile retail",transport:"Rural distribution and aggregation",dairy:"Dairy / milk"})[value]||value;}
function friendlyConfidence(value){return value==="HIGH"?"High":value==="MEDIUM"?"Moderate":"Early planning";}
function safe(value){const node=document.createElement("span");node.textContent=value??"";return node.innerHTML;}
