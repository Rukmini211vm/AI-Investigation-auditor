/**
 * AI Investigation Auditor - Frontend Controller
 * Single Page Application managing case workspaces, dynamic audit execution,
 * RAG inspection, human reviews, multi-language switching, and report exports.
 */

const API_BASE = window.location.protocol === 'file:' ? 'http://127.0.0.1:8000' : '';

const AppState = {
  cases: [],
  currentCaseId: "CASE-001",
  currentCase: null,
  auditResult: null,
  humanReviews: {},
  currentLang: "en",
  languages: {},
  activeTab: "overview",
  graphInstance: null,
  timelineInstance: null
};
window.AppState = AppState;

document.addEventListener("DOMContentLoaded", async () => {
  initTabs();
  initLanguageSelector();
  initEventHandlers();

  // Restore saved theme
  const savedTheme = localStorage.getItem("theme");
  const isLight = (savedTheme === "light");
  if (isLight) {
    document.body.classList.add("light-theme");
    const icon = document.getElementById("themeToggleIcon");
    const text = document.getElementById("themeToggleText");
    if (icon) icon.textContent = "☀️";
    if (text) text.textContent = "Light";
  }

  // Initialize visualizers
  AppState.graphInstance = new RelationshipGraph("graphCanvas");
  if (AppState.graphInstance && isLight) {
    AppState.graphInstance.setTheme(false);
  }
  AppState.timelineInstance = new TimelineVisualizer("timelineContainer");

  // Load initial cases and default case
  await loadCasesList();
  await loadCase("CASE-001");
});

// ---------------- Tab Navigation ----------------

function initTabs() {
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  AppState.activeTab = tabId;
  document.querySelectorAll(".nav-tab").forEach(t => {
    t.classList.toggle("active", t.dataset.tab === tabId);
  });
  document.querySelectorAll(".tab-content").forEach(c => {
    c.classList.toggle("active", c.id === `tab-${tabId}`);
  });

  // Trigger resize or redraw when visual tabs become active
  if (tabId === "graph" && AppState.graphInstance && AppState.currentCase) {
    setTimeout(() => {
      AppState.graphInstance.resize();
      AppState.graphInstance.setData(AppState.currentCase, AppState.auditResult ? AppState.auditResult.flags : []);
    }, 50);
  }
  if (tabId === "timeline" && AppState.timelineInstance && AppState.currentCase) {
    AppState.timelineInstance.render(
      AppState.currentCase.timeline || [],
      AppState.auditResult ? AppState.auditResult.flags : [],
      AppState.currentCase
    );
  }
  if (tabId === "report") {
    renderReportPreview();
  }
}

// ---------------- Language Management ----------------

async function initLanguageSelector() {
  try {
    const res = await fetch(`${API_BASE}/api/languages`);
    const data = await res.json();
    AppState.languages = data.languages || {};
    const select = document.getElementById("langSelect");
    if (select) {
      select.innerHTML = "";
      for (const [code, name] of Object.entries(AppState.languages)) {
        const opt = document.createElement("option");
        opt.value = code;
        opt.textContent = name;
        select.appendChild(opt);
      }
      select.value = AppState.currentLang;
      select.addEventListener("change", async (e) => {
        AppState.currentLang = e.target.value;
        if (AppState.currentCaseId) {
          await runAudit(false);
        }
      });
    }
  } catch (err) {
    console.error("Language init failed:", err);
  }
}

// ---------------- Cases & Data Fetching ----------------

async function loadCasesList() {
  try {
    const res = await fetch(`${API_BASE}/api/cases`);
    const data = await res.json();
    AppState.cases = data.cases || [];
    renderCasesTable(AppState.cases);
  } catch (err) {
    showNotification("Failed to fetch cases list: " + err.message, "danger");
  }
}

async function loadCase(caseId) {
  try {
    const res = await fetch(`${API_BASE}/api/cases/${caseId}`);
    const data = await res.json();
    if (data.status === "success" && data.case) {
      AppState.currentCaseId = caseId;
      AppState.currentCase = data.case.data;
      
      // Update header badges
      document.getElementById("currentCaseBadge").textContent = `CASE: ${caseId} (${AppState.currentCase.crime_type})`;
      
      // Populate case workspace form
      populateWorkspace(AppState.currentCase);

      // Load human reviews
      await loadReviews(caseId);

      // Automatically run audit to have up-to-date findings
      await runAudit(false);
    }
  } catch (err) {
    showNotification("Failed to load case details: " + err.message, "danger");
  }
}

async function loadReviews(caseId) {
  try {
    const res = await fetch(`${API_BASE}/api/cases/${caseId}/reviews`);
    const data = await res.json();
    AppState.humanReviews = data.reviews || {};
  } catch (err) {
    AppState.humanReviews = {};
  }
}

// ---------------- Case Workspace & Dynamic Editor ----------------

function populateWorkspace(c) {
  document.getElementById("caseIdInput").value = c.case_id || "";
  document.getElementById("caseTitleInput").value = c.title || "";
  
  // Crime Type selection & custom option
  const crimeSelect = document.getElementById("crimeTypeSelect");
  const customCrimeInput = document.getElementById("crimeTypeCustom");
  
  const knownTypes = ["Murder", "Robbery", "Kidnapping / Abduction", "Theft", "Assault", "Cybercrime", "Fraud", "Other"];
  if (knownTypes.includes(c.crime_type)) {
    crimeSelect.value = c.crime_type;
    customCrimeInput.style.display = "none";
  } else {
    crimeSelect.value = "Other";
    customCrimeInput.style.display = "block";
    customCrimeInput.value = c.crime_type || "";
  }

  document.getElementById("incidentDateInput").value = c.incident_date || "";
  document.getElementById("incidentTimeInput").value = c.incident_time || "";
  document.getElementById("locationInput").value = c.location || "";
  document.getElementById("victimInput").value = c.victim || "";
  document.getElementById("suspectsInput").value = (c.suspects || []).join(", ");
  document.getElementById("summaryInput").value = c.summary || "";

  // FIR details
  const fir = c.fir || {};
  document.getElementById("firNumberInput").value = fir.fir_number || "";
  document.getElementById("firPsInput").value = fir.ps || "";
  document.getElementById("firSectionsInput").value = fir.sections || "";
  document.getElementById("firDetailsInput").value = fir.details || "";

  // Update FIR interactive summary banner
  const firBadge = document.getElementById("firCardBadge");
  if (firBadge) firBadge.textContent = fir.fir_number || `FIR-${c.case_id || 'RECORD'}`;
  const firSub = document.getElementById("firCardSubtitle");
  if (firSub) firSub.textContent = `${fir.ps || 'Central District Police Station'} | ${fir.sections || 'Section 302 IPC / Section 103 BNS'}`;

  // Dynamic Lists: Witnesses, CCTV, Evidence, Timeline, Custody, Notes
  renderWitnessesEditor(c.witnesses || []);
  renderCctvEditor(c.cctv || []);
  renderEvidenceEditor(c.evidence || []);
  renderTimelineEditor(c.timeline || []);
  renderCustodyEditor(c.chain_of_custody || []);
  document.getElementById("notesInput").value = (c.notes || []).join("\n");
}

function collectWorkspaceData() {
  const caseId = document.getElementById("caseIdInput").value.trim();
  const crimeSelect = document.getElementById("crimeTypeSelect");
  let crimeType = crimeSelect.value;
  if (crimeType === "Other") {
    crimeType = document.getElementById("crimeTypeCustom").value.trim() || "Other";
  }

  const suspectsStr = document.getElementById("suspectsInput").value.trim();
  const suspects = suspectsStr ? suspectsStr.split(",").map(s => s.trim()).filter(Boolean) : [];

  const notesStr = document.getElementById("notesInput").value.trim();
  const notes = notesStr ? notesStr.split("\n").map(n => n.trim()).filter(Boolean) : [];

  return {
    case_id: caseId,
    title: document.getElementById("caseTitleInput").value.trim(),
    crime_type: crimeType,
    incident_date: document.getElementById("incidentDateInput").value.trim(),
    incident_time: document.getElementById("incidentTimeInput").value.trim(),
    location: document.getElementById("locationInput").value.trim(),
    victim: document.getElementById("victimInput").value.trim(),
    suspects: suspects,
    summary: document.getElementById("summaryInput").value.trim(),
    fir: {
      fir_number: document.getElementById("firNumberInput").value.trim(),
      ps: document.getElementById("firPsInput").value.trim(),
      date: document.getElementById("incidentDateInput").value.trim(),
      time: document.getElementById("incidentTimeInput").value.trim(),
      sections: document.getElementById("firSectionsInput").value.trim(),
      details: document.getElementById("firDetailsInput").value.trim()
    },
    witnesses: collectWitnessesFromEditor(),
    cctv: collectCctvFromEditor(),
    evidence: collectEvidenceFromEditor(),
    timeline: collectTimelineFromEditor(),
    chain_of_custody: collectCustodyFromEditor(),
    notes: notes
  };
}

// ---------------- Editor Rows Builders ----------------

function renderWitnessesEditor(witnesses) {
  const container = document.getElementById("witnessesList");
  container.innerHTML = "";
  witnesses.forEach((w, idx) => {
    const row = document.createElement("div");
    row.className = "card";
    row.style.marginBottom = "10px";
    row.style.padding = "12px";
    row.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-weight: 700; color: #38bdf8;">Witness #${idx + 1} (${w.witness_id || 'WS'})</span>
        <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.card').remove()">Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Witness ID</label><input class="form-input witness-id" value="${w.witness_id || ''}"></div>
        <div class="form-group"><label class="form-label">Name & Relation</label><input class="form-input witness-name" value="${w.name || ''}"></div>
        <div class="form-group"><label class="form-label">Observed Time</label><input class="form-input witness-time" value="${w.claimed_time || ''}"></div>
        <div class="form-group"><label class="form-label">Observation Location</label><input class="form-input witness-loc" value="${w.location || ''}"></div>
      </div>
      <div class="form-group">
        <label class="form-label">Recorded Statement (Section 161 CrPC)</label>
        <textarea class="form-textarea witness-stmt" rows="2">${w.statement || ''}</textarea>
      </div>
    `;
    container.appendChild(row);
  });
}

function addWitnessRow() {
  const container = document.getElementById("witnessesList");
  const count = container.children.length + 1;
  const row = document.createElement("div");
  row.className = "card";
  row.style.marginBottom = "10px";
  row.style.padding = "12px";
  row.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <span style="font-weight: 700; color: #38bdf8;">New Witness #${count}</span>
      <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.card').remove()">Remove</button>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Witness ID</label><input class="form-input witness-id" value="WS-${String(count).padStart(3, '0')}"></div>
      <div class="form-group"><label class="form-label">Name & Relation</label><input class="form-input witness-name" placeholder="Full name"></div>
      <div class="form-group"><label class="form-label">Observed Time</label><input class="form-input witness-time" placeholder="e.g. 21:10"></div>
      <div class="form-group"><label class="form-label">Observation Location</label><input class="form-input witness-loc" placeholder="Location"></div>
    </div>
    <div class="form-group">
      <label class="form-label">Recorded Statement</label>
      <textarea class="form-textarea witness-stmt" rows="2" placeholder="Testimony details..."></textarea>
    </div>
  `;
  container.appendChild(row);
}

function collectWitnessesFromEditor() {
  const rows = document.querySelectorAll("#witnessesList .card");
  const list = [];
  rows.forEach(r => {
    list.push({
      witness_id: r.querySelector(".witness-id")?.value.trim() || "",
      name: r.querySelector(".witness-name")?.value.trim() || "",
      claimed_time: r.querySelector(".witness-time")?.value.trim() || "",
      location: r.querySelector(".witness-loc")?.value.trim() || "",
      statement: r.querySelector(".witness-stmt")?.value.trim() || ""
    });
  });
  return list;
}

function getFallbackCctvImage(cctvId = '', caseId = '') {
  const cid = caseId || AppState.currentCaseId || 'CASE-001';
  // 1. If currentCase has a matching CCTV item with an image_url, return it
  if (AppState.currentCase && AppState.currentCase.cctv) {
    const match = AppState.currentCase.cctv.find(c => 
      c.cctv_id === cctvId || (cctvId && (cctvId.includes(c.cctv_id) || c.cctv_id.includes(cctvId)))
    );
    if (match && match.image_url) return match.image_url;
  }
  // 2. Direct case and ID pattern
  if (cctvId && cctvId.startsWith('CCTV-')) {
    return `/static/cctv/cctv_${cid}_${cctvId}.jpg`;
  }
  // 3. Fallback to valid surveillance image
  return `/static/cctv/cctv_CASE-001_CCTV-001.jpg`;
}

function renderCctvEditor(cctvs) {
  const container = document.getElementById("cctvList");
  container.innerHTML = "";

  if (!cctvs || cctvs.length === 0) {
    container.innerHTML = `
      <div style="padding: 18px; text-align: center; color: var(--text-muted); border: 1px dashed var(--border-subtle); border-radius: 8px;">
        No CCTV surveillance logs cataloged for this case. Click "+ Add CCTV Record" above to add footage.
      </div>
    `;
    return;
  }

  cctvs.forEach((c, idx) => {
    const imgUrl = c.image_url || getFallbackCctvImage(c.cctv_id, AppState.currentCaseId);
    const row = document.createElement("div");
    row.className = "cctv-card-modern";
    row.innerHTML = `
      <div class="cctv-card-layout">
        <!-- Visual CCTV Footage Snapshot -->
        <div>
          <div class="cctv-thumb-box" onclick="openCctvModalById('${c.cctv_id || 'CCTV-' + (idx+1)}')">
            <div class="cctv-hud-top">
              <span><span class="cctv-rec-dot"></span>[${c.cctv_id || 'CAM'}] REC</span>
              <span>1080P</span>
            </div>
            <img class="cctv-preview-img" src="${imgUrl}" alt="${c.camera_name || c.cctv_id}" onerror="this.src='/static/cctv/cctv_CASE-001_CCTV-001.jpg'">
            <div class="cctv-hud-bottom">
              <span>CH-0${(idx % 4) + 1}</span>
              <span>${c.date || ''} ${c.timestamp || ''}</span>
            </div>
            <div class="cctv-zoom-badge">🔍 Inspect Feed</div>
          </div>
          <button type="button" class="btn btn-secondary btn-sm" style="width: 100%; margin-top: 8px; font-size: 11px; display: flex; justify-content: center; align-items: center; gap: 4px;" onclick="openCctvModalById('${c.cctv_id || 'CCTV-' + (idx+1)}')">
            <span>📹</span> Full CCTV Player
          </button>
        </div>

        <!-- Camera Metadata & Form Inputs -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; color: #06b6d4; font-size: 14px;">
              📹 CCTV Record #${idx + 1}: ${c.cctv_id || 'CAM'} — ${c.camera_name || 'Surveillance Channel'}
            </span>
            <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.cctv-card-modern').remove()">Remove</button>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">CCTV ID</label><input class="form-input cctv-id" value="${escapeHtml(c.cctv_id || '')}"></div>
            <div class="form-group"><label class="form-label">Camera Name / Channel</label><input class="form-input cctv-name" value="${escapeHtml(c.camera_name || '')}"></div>
            <div class="form-group"><label class="form-label">Footage Timestamp</label><input class="form-input cctv-time" value="${escapeHtml(c.timestamp || '')}"></div>
            <div class="form-group"><label class="form-label">Date</label><input class="form-input cctv-date" value="${escapeHtml(c.date || '')}"></div>
          </div>
          <div class="form-group" style="margin-bottom: 8px;">
            <label class="form-label">Surveillance Snapshot Image URL / Path</label>
            <input class="form-input cctv-img-url" value="${escapeHtml(c.image_url || imgUrl)}" onchange="this.closest('.cctv-card-layout').querySelector('.cctv-preview-img').src = this.value">
          </div>
          <div class="form-group">
            <label class="form-label">Surveillance Footage Observation</label>
            <textarea class="form-textarea cctv-desc" rows="2">${escapeHtml(c.description || '')}</textarea>
          </div>
        </div>
      </div>
    `;
    container.appendChild(row);
  });
}

function addCctvRow() {
  const container = document.getElementById("cctvList");
  const count = container.querySelectorAll(".cctv-card-modern").length + 1;
  const cctvId = `CCTV-${String(count).padStart(3, '0')}`;
  const imgUrl = getFallbackCctvImage(cctvId, AppState.currentCaseId);
  const incDate = document.getElementById("incidentDateInput")?.value || new Date().toISOString().split("T")[0];

  const row = document.createElement("div");
  row.className = "cctv-card-modern";
  row.innerHTML = `
    <div class="cctv-card-layout">
      <div>
        <div class="cctv-thumb-box" onclick="openCctvModalById('${cctvId}')">
          <div class="cctv-hud-top">
            <span><span class="cctv-rec-dot"></span>[${cctvId}] REC</span>
            <span>1080P</span>
          </div>
          <img class="cctv-preview-img" src="${imgUrl}" alt="${cctvId}" onerror="this.src='/static/cctv/cctv_CASE-001_CCTV-001.jpg'">
          <div class="cctv-hud-bottom">
            <span>CH-0${(count % 4) + 1}</span>
            <span>${incDate} 20:00</span>
          </div>
          <div class="cctv-zoom-badge">🔍 Inspect Feed</div>
        </div>
        <button type="button" class="btn btn-secondary btn-sm" style="width: 100%; margin-top: 8px; font-size: 11px;" onclick="openCctvModalById('${cctvId}')">
          📹 Full CCTV Player
        </button>
      </div>

      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="font-weight: 700; color: #06b6d4; font-size: 14px;">
            📹 New CCTV Record #${count}: ${cctvId}
          </span>
          <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.cctv-card-modern').remove()">Remove</button>
        </div>
        <div class="form-row">
          <div class="form-group"><label class="form-label">CCTV ID</label><input class="form-input cctv-id" value="${cctvId}"></div>
          <div class="form-group"><label class="form-label">Camera Name / Channel</label><input class="form-input cctv-name" placeholder="Channel / Camera location name"></div>
          <div class="form-group"><label class="form-label">Footage Timestamp</label><input class="form-input cctv-time" placeholder="e.g. 20:40"></div>
          <div class="form-group"><label class="form-label">Date</label><input class="form-input cctv-date" value="${incDate}"></div>
        </div>
        <div class="form-group" style="margin-bottom: 8px;">
          <label class="form-label">Surveillance Snapshot Image URL / Path</label>
          <input class="form-input cctv-img-url" value="${imgUrl}" onchange="this.closest('.cctv-card-layout').querySelector('.cctv-preview-img').src = this.value">
        </div>
        <div class="form-group">
          <label class="form-label">Surveillance Footage Observation</label>
          <textarea class="form-textarea cctv-desc" rows="2" placeholder="Visible persons, movement directions, vehicle plates, or actions..."></textarea>
        </div>
      </div>
    </div>
  `;
  container.appendChild(row);
}

function collectCctvFromEditor() {
  const rows = document.querySelectorAll("#cctvList .cctv-card-modern, #cctvList .card");
  const list = [];
  rows.forEach(r => {
    list.push({
      cctv_id: r.querySelector(".cctv-id")?.value.trim() || "",
      camera_name: r.querySelector(".cctv-name")?.value.trim() || "",
      timestamp: r.querySelector(".cctv-time")?.value.trim() || "",
      date: r.querySelector(".cctv-date")?.value.trim() || "",
      image_url: r.querySelector(".cctv-img-url")?.value.trim() || r.querySelector(".cctv-preview-img")?.src || "",
      description: r.querySelector(".cctv-desc")?.value.trim() || ""
    });
  });
  return list;
}

function renderEvidenceEditor(evidences) {
  const container = document.getElementById("evidenceList");
  container.innerHTML = "";
  evidences.forEach((e, idx) => {
    const row = document.createElement("div");
    row.className = "card";
    row.style.marginBottom = "10px";
    row.style.padding = "12px";
    row.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-weight: 700; color: #10b981;">Evidence Item #${idx + 1} (${e.evidence_id || 'E'})</span>
        <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.card').remove()">Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Evidence ID</label><input class="form-input ev-id" value="${e.evidence_id || ''}"></div>
        <div class="form-group"><label class="form-label">Type / Category</label><input class="form-input ev-type" value="${e.type || ''}"></div>
        <div class="form-group"><label class="form-label">Recovery Location</label><input class="form-input ev-loc" value="${e.recovery_location || ''}"></div>
        <div class="form-group"><label class="form-label">Recovery Time</label><input class="form-input ev-time" value="${e.recovery_time || ''}"></div>
      </div>
      <div class="form-group">
        <label class="form-label">Physical Description & Seizure Memo Notes</label>
        <textarea class="form-textarea ev-desc" rows="2">${e.description || ''}</textarea>
      </div>
    `;
    container.appendChild(row);
  });
}

function addEvidenceRow() {
  const container = document.getElementById("evidenceList");
  const count = container.children.length + 1;
  const row = document.createElement("div");
  row.className = "card";
  row.style.marginBottom = "10px";
  row.style.padding = "12px";
  row.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <span style="font-weight: 700; color: #10b981;">New Evidence Item #${count}</span>
      <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.card').remove()">Remove</button>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Evidence ID</label><input class="form-input ev-id" value="E-${String(count).padStart(3, '0')}"></div>
      <div class="form-group"><label class="form-label">Type</label><input class="form-input ev-type" placeholder="Weapon / Digital / Fabric"></div>
      <div class="form-group"><label class="form-label">Recovery Location</label><input class="form-input ev-loc" placeholder="Spot"></div>
      <div class="form-group"><label class="form-label">Recovery Time</label><input class="form-input ev-time" placeholder="e.g. 22:15"></div>
    </div>
    <div class="form-group">
      <label class="form-label">Description</label>
      <textarea class="form-textarea ev-desc" rows="2" placeholder="Item details..."></textarea>
    </div>
  `;
  container.appendChild(row);
}

function collectEvidenceFromEditor() {
  const rows = document.querySelectorAll("#evidenceList .card");
  const list = [];
  rows.forEach(r => {
    list.push({
      evidence_id: r.querySelector(".ev-id")?.value.trim() || "",
      type: r.querySelector(".ev-type")?.value.trim() || "",
      recovery_location: r.querySelector(".ev-loc")?.value.trim() || "",
      recovery_time: r.querySelector(".ev-time")?.value.trim() || "",
      description: r.querySelector(".ev-desc")?.value.trim() || ""
    });
  });
  return list;
}

function renderTimelineEditor(events) {
  const container = document.getElementById("timelineList");
  container.innerHTML = "";
  events.forEach((t, idx) => {
    const row = document.createElement("div");
    row.className = "card";
    row.style.marginBottom = "10px";
    row.style.padding = "12px";
    row.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-weight: 700; color: #a855f7;">Timeline Event #${idx + 1} (${t.event_id || 'EVT'})</span>
        <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.card').remove()">Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Event ID</label><input class="form-input tm-id" value="${t.event_id || ''}"></div>
        <div class="form-group"><label class="form-label">Timestamp</label><input class="form-input tm-time" value="${t.time || ''}"></div>
        <div class="form-group"><label class="form-label">Source Document</label><input class="form-input tm-src" value="${t.source || ''}"></div>
      </div>
      <div class="form-group">
        <label class="form-label">Event Description</label>
        <textarea class="form-textarea tm-desc" rows="2">${t.description || ''}</textarea>
      </div>
    `;
    container.appendChild(row);
  });
}

function addTimelineRow() {
  const container = document.getElementById("timelineList");
  const count = container.children.length + 1;
  const row = document.createElement("div");
  row.className = "card";
  row.style.marginBottom = "10px";
  row.style.padding = "12px";
  row.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <span style="font-weight: 700; color: #a855f7;">New Timeline Event #${count}</span>
      <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.card').remove()">Remove</button>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Event ID</label><input class="form-input tm-id" value="EVT-${String(count).padStart(3, '0')}"></div>
      <div class="form-group"><label class="form-label">Timestamp</label><input class="form-input tm-time" placeholder="e.g. 21:00"></div>
      <div class="form-group"><label class="form-label">Source Document</label><input class="form-input tm-src" placeholder="FIR / CCTV / Witness"></div>
    </div>
    <div class="form-group">
      <label class="form-label">Event Description</label>
      <textarea class="form-textarea tm-desc" rows="2" placeholder="Description of occurrence..."></textarea>
    </div>
  `;
  container.appendChild(row);
}

function collectTimelineFromEditor() {
  const rows = document.querySelectorAll("#timelineList .card");
  const list = [];
  rows.forEach(r => {
    list.push({
      event_id: r.querySelector(".tm-id")?.value.trim() || "",
      time: r.querySelector(".tm-time")?.value.trim() || "",
      source: r.querySelector(".tm-src")?.value.trim() || "",
      description: r.querySelector(".tm-desc")?.value.trim() || ""
    });
  });
  return list;
}

function renderCustodyEditor(logs) {
  const container = document.getElementById("custodyList");
  container.innerHTML = "";
  logs.forEach((c, idx) => {
    const row = document.createElement("div");
    row.className = "card";
    row.style.marginBottom = "10px";
    row.style.padding = "12px";
    row.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-weight: 700; color: #f59e0b;">Custody Transfer #${idx + 1} (${c.evidence_id || 'E'})</span>
        <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.card').remove()">Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Evidence ID</label><input class="form-input coc-id" value="${c.evidence_id || ''}"></div>
        <div class="form-group"><label class="form-label">Collected By</label><input class="form-input coc-col-by" value="${c.collected_by || ''}"></div>
        <div class="form-group"><label class="form-label">Collected Time</label><input class="form-input coc-col-time" value="${c.collected_time || ''}"></div>
        <div class="form-group"><label class="form-label">Sealed Time</label><input class="form-input coc-seal-time" value="${c.sealed_time || ''}"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Transferred To</label><input class="form-input coc-trans-to" value="${c.transferred_to || ''}"></div>
        <div class="form-group"><label class="form-label">Transfer Time</label><input class="form-input coc-trans-time" value="${c.transfer_time || ''}"></div>
        <div class="form-group"><label class="form-label">Storage Location</label><input class="form-input coc-loc" value="${c.stored_location || ''}"></div>
      </div>
    `;
    container.appendChild(row);
  });
}

function addCustodyRow() {
  const container = document.getElementById("custodyList");
  const count = container.children.length + 1;
  const row = document.createElement("div");
  row.className = "card";
  row.style.marginBottom = "10px";
  row.style.padding = "12px";
  row.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <span style="font-weight: 700; color: #f59e0b;">New Custody Entry #${count}</span>
      <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.card').remove()">Remove</button>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Evidence ID</label><input class="form-input coc-id" placeholder="e.g. E-001"></div>
      <div class="form-group"><label class="form-label">Collected By</label><input class="form-input coc-col-by" placeholder="Officer name"></div>
      <div class="form-group"><label class="form-label">Collected Time</label><input class="form-input coc-col-time" placeholder="e.g. 14:15"></div>
      <div class="form-group"><label class="form-label">Sealed Time</label><input class="form-input coc-seal-time" placeholder="e.g. 14:30"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label class="form-label">Transferred To</label><input class="form-input coc-trans-to" placeholder="Malkhana / FSL"></div>
      <div class="form-group"><label class="form-label">Transfer Time</label><input class="form-input coc-trans-time" placeholder="e.g. 16:00"></div>
      <div class="form-group"><label class="form-label">Storage Location</label><input class="form-input coc-loc" placeholder="Locker / Vault"></div>
    </div>
  `;
  container.appendChild(row);
}

function collectCustodyFromEditor() {
  const rows = document.querySelectorAll("#custodyList .card");
  const list = [];
  rows.forEach(r => {
    list.push({
      evidence_id: r.querySelector(".coc-id")?.value.trim() || "",
      collected_by: r.querySelector(".coc-col-by")?.value.trim() || "",
      collected_time: r.querySelector(".coc-col-time")?.value.trim() || "",
      sealed_time: r.querySelector(".coc-seal-time")?.value.trim() || "",
      transferred_to: r.querySelector(".coc-trans-to")?.value.trim() || "",
      transfer_time: r.querySelector(".coc-trans-time")?.value.trim() || "",
      stored_location: r.querySelector(".coc-loc")?.value.trim() || ""
    });
  });
  return list;
}

// ---------------- Audit Execution & Dynamic Feedback ----------------

async function runAudit(switchTabOnComplete = true) {
  if (!AppState.currentCaseId) return;

  // First save current workspace state so user edits take immediate effect
  const updatedData = collectWorkspaceData();
  try {
    await fetch(`${API_BASE}/api/cases`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedData)
    });
    AppState.currentCase = updatedData;
  } catch (e) {
    console.warn("Auto-save prior to audit warning:", e);
  }

  try {
    const res = await fetch(`${API_BASE}/api/cases/${AppState.currentCaseId}/audit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang: AppState.currentLang })
    });
    const data = await res.json();
    if (data.status === "success") {
      AppState.auditResult = data;
      AppState.humanReviews = data.human_reviews || {};

      // Render scores & findings
      renderAuditScores(data.scores);
      renderAuditFlags(data.flags, data.rag_evidence);

      // Update badge count
      document.getElementById("flagsCountBadge").textContent = data.flags.length;

      // Update visualizations
      if (AppState.graphInstance) {
        AppState.graphInstance.setData(AppState.currentCase, data.flags);
      }
      if (AppState.timelineInstance) {
        AppState.timelineInstance.render(
          AppState.currentCase.timeline || [],
          data.flags,
          AppState.currentCase
        );
      }

      if (switchTabOnComplete) {
        switchTab("audit");
        showNotification(`AI Audit Complete: ${data.flags.length} potential items identified for human review.`, "info");
      }
    }
  } catch (err) {
    showNotification("Audit execution error: " + err.message, "danger");
  }
}

// ---------------- Rendering Audit Dashboard ----------------

function renderAuditScores(scores = {}) {
  const overall = scores.overall || 100;
  const consistency = scores.consistency || 100;
  const completeness = scores.completeness || 100;
  const linking = scores.linking || 100;
  const custody = scores.custody || 100;

  const getScoreClass = (val) => val >= 85 ? "score-good" : (val >= 65 ? "score-warn" : "score-crit");

  document.getElementById("scoreOverallVal").textContent = `${overall}%`;
  document.getElementById("scoreOverallBox").className = `score-box ${getScoreClass(overall)}`;

  document.getElementById("scoreConsistencyVal").textContent = `${consistency}%`;
  document.getElementById("scoreConsistencyBox").className = `score-box ${getScoreClass(consistency)}`;

  document.getElementById("scoreCompletenessVal").textContent = `${completeness}%`;
  document.getElementById("scoreCompletenessBox").className = `score-box ${getScoreClass(completeness)}`;

  document.getElementById("scoreLinkingVal").textContent = `${linking}%`;
  document.getElementById("scoreLinkingBox").className = `score-box ${getScoreClass(linking)}`;

  document.getElementById("scoreCustodyVal").textContent = `${custody}%`;
  document.getElementById("scoreCustodyBox").className = `score-box ${getScoreClass(custody)}`;
}

function renderAuditFlags(flags = [], ragMap = {}) {
  const container = document.getElementById("auditFlagsList");
  container.innerHTML = "";

  if (!flags || flags.length === 0) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 36px; border-color: rgba(16, 185, 129, 0.4);">
        <div style="font-size: 36px; margin-bottom: 10px;">🛡️</div>
        <h3 style="color: #34d399; margin-bottom: 6px;">Records Corroborate Consistently</h3>
        <p style="color: var(--text-muted); font-size: 13px; max-width: 500px; margin: 0 auto;">
          No active timeline discrepancies, missing evidence tokens, or chain-of-custody documentation gaps were detected based on the current case records.
        </p>
      </div>
    `;
    return;
  }

  flags.forEach((f, idx) => {
    const fid = f.flag_id;
    const sevClass = f.severity === "CRITICAL" ? "flag-critical" : (f.severity === "WARNING" ? "flag-warning" : "flag-info");
    const badgeClass = f.severity === "CRITICAL" ? "badge-crit" : (f.severity === "WARNING" ? "badge-warn" : "badge-inf");
    
    // Check human review status
    const rev = AppState.humanReviews[fid] || {};
    const revStatus = rev.status || "Pending";
    const statusClass = revStatus === "Reviewed" ? "status-reviewed" : (revStatus === "Needs Further Investigation" ? "status-further" : (revStatus === "False Positive" ? "status-falsepos" : "status-pending"));

    // RAG retrieved chunks
    const retrievedChunks = ragMap[fid] || f.retrieved_sources || [];
    let ragHtml = "";
    if (retrievedChunks.length > 0) {
      ragHtml = `
        <div class="rag-drawer">
          <div class="rag-drawer-title">
            <span>🔍 Case-Isolated RAG Evidence Retrieval (${retrievedChunks.length} Chunks Matched)</span>
          </div>
          ${retrievedChunks.map(c => `
            <div class="rag-chunk">
              <strong>[${c.title}] (Score: ${c.score}):</strong> ${escapeHtml(c.text.substring(0, 160))}...
            </div>
          `).join("")}
        </div>
      `;
    }

    // Format source records with clickable FIR and CCTV inspection
    const sourcesFormatted = (f.source_records || []).map(src => {
      if (src.toUpperCase().includes("FIR")) {
        return `<span class="fir-pill-clickable" onclick="openFirModal()" title="Click to view official FIR format">📑 ${src}</span>`;
      }
      if (src.toUpperCase().includes("CCTV")) {
        const match = src.match(/CCTV[-_ ]?(\d+)/i);
        const cctvParam = match ? match[0] : src;
        return `<span style="color: #38bdf8; font-weight: 700; cursor: pointer;" onclick="openCctvModalById('${cctvParam}')" title="Click to inspect CCTV footage">📹 ${src}</span>`;
      }
      return `<span>${src}</span>`;
    }).join(", ") || "Case Records";

    // Check if there is an associated CCTV to show visual footage thumbnail directly in the flag
    let cctvBannerHtml = "";
    const citedCctvStr = (f.source_records || []).find(s => s.toUpperCase().includes("CCTV"));
    if (citedCctvStr && AppState.currentCase) {
      const match = citedCctvStr.match(/CCTV[-_ ]?(\d+)/i);
      const cId = match ? match[0].toUpperCase() : "";
      const cctvMatch = (AppState.currentCase.cctv || []).find(c => 
        (cId && c.cctv_id.toUpperCase().includes(cId)) ||
        citedCctvStr.includes(c.cctv_id) ||
        c.cctv_id.includes(citedCctvStr)
      ) || (AppState.currentCase.cctv.length > 0 ? AppState.currentCase.cctv[0] : null);

      if (cctvMatch) {
        const imgUrl = cctvMatch.image_url || getFallbackCctvImage(cctvMatch.cctv_id, AppState.currentCaseId);
        cctvBannerHtml = `
          <div style="margin-top: 10px; display: flex; align-items: center; gap: 14px; background: rgba(8, 12, 22, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.28);">
            <div class="cctv-thumb-box" style="width: 140px; height: 80px; flex-shrink: 0; cursor: pointer;" onclick="openCctvModalById('${cctvMatch.cctv_id}')">
              <img src="${imgUrl}" alt="${cctvMatch.cctv_id}" onerror="this.src='/static/cctv/cctv_CASE-001_CCTV-001.jpg'">
              <span class="cctv-zoom-badge" style="font-size: 10px; padding: 2px 6px;">🔍 View Feed</span>
            </div>
            <div style="flex: 1; min-width: 0;">
              <div style="font-size: 12px; font-weight: 800; color: #38bdf8;">📹 Surveillance Still: ${cctvMatch.camera_name || cctvMatch.cctv_id} (${cctvMatch.timestamp} hrs)</div>
              <div style="font-size: 11px; color: var(--text-muted); margin: 2px 0;">${cctvMatch.description || ''}</div>
              <button type="button" class="btn btn-secondary btn-sm" style="padding: 2px 8px; font-size: 10px; margin-top: 4px; display: inline-flex; align-items: center; gap: 4px;" onclick="openCctvModalById('${cctvMatch.cctv_id}')">📹 Open Full CCTV Player</button>
            </div>
          </div>
        `;
      }
    }

    const card = document.createElement("div");
    card.className = `flag-card ${sevClass}`;
    card.innerHTML = `
      <div class="flag-header">
        <div>
          <span class="flag-badge ${badgeClass}">${f.severity}</span>
          <span style="font-size: 11px; color: var(--text-muted); margin-left: 8px; font-weight: 600;">
            ${f.category_translated || f.category} | Flag ID: ${fid}
          </span>
          <div class="flag-title">${f.title}</div>
        </div>
        <span class="review-status-tag ${statusClass}" id="statusTag_${fid}">${revStatus}</span>
      </div>

      <div class="flag-explanation">${f.explanation}</div>

      <div class="flag-sources">
        <strong>Source Records Cited:</strong> ${sourcesFormatted}
        ${f.timestamps && f.timestamps.length ? ` | <strong>Timestamps:</strong> ${f.timestamps.join(" vs ")}` : ""}
      </div>

      ${cctvBannerHtml}

      ${ragHtml}

      ${f.llm_assessment ? `
        <div style="margin-top: 10px; padding: 10px 14px; background: rgba(59, 130, 246, 0.07); border-radius: 6px; font-size: 12px; color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.2);">
          <strong>🤖 AI Second-Checker Assessment:</strong> ${f.llm_assessment}
        </div>
      ` : ""}

      <!-- Human Review Interaction Bar -->
      <div class="review-bar">
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
          <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Review Action:</span>
          <button type="button" class="btn btn-success btn-sm" onclick="saveReviewAction('${fid}', 'Reviewed')">✓ Mark Reviewed</button>
          <button type="button" class="btn btn-secondary btn-sm" onclick="saveReviewAction('${fid}', 'Needs Further Investigation')" style="color: #fbbf24;">🔍 Needs Further Investigation</button>
          <button type="button" class="btn btn-secondary btn-sm" onclick="saveReviewAction('${fid}', 'False Positive')">🚫 False Positive</button>
        </div>
        <div style="display: flex; gap: 8px; align-items: center; flex: 1; max-width: 380px;">
          <input class="form-input" id="noteInput_${fid}" placeholder="Investigator note (e.g., Camera clock offset by 30 min)..." value="${escapeHtml(rev.notes || '')}" style="font-size: 11px; padding: 4px 8px;">
          <button type="button" class="btn btn-primary btn-sm" onclick="saveReviewNote('${fid}')">Save Note</button>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

// ---------------- Human Review Action ----------------

async function saveReviewAction(flagId, status) {
  const noteInput = document.getElementById(`noteInput_${flagId}`);
  const notes = noteInput ? noteInput.value.trim() : "";
  await submitReview(flagId, status, notes);
}

async function saveReviewNote(flagId) {
  const noteInput = document.getElementById(`noteInput_${flagId}`);
  const notes = noteInput ? noteInput.value.trim() : "";
  const existingStatus = (AppState.humanReviews[flagId] && AppState.humanReviews[flagId].status) || "Needs Further Investigation";
  await submitReview(flagId, existingStatus, notes);
}

async function submitReview(flagId, status, notes) {
  try {
    const res = await fetch(`${API_BASE}/api/cases/${AppState.currentCaseId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        flag_id: flagId,
        status: status,
        reviewer_name: "Investigating Officer",
        notes: notes
      })
    });
    const data = await res.json();
    if (data.status === "success") {
      AppState.humanReviews[flagId] = { status, notes, updated_at: new Date().toISOString() };
      
      // Update UI tag
      const tag = document.getElementById(`statusTag_${flagId}`);
      if (tag) {
        tag.textContent = status;
        tag.className = `review-status-tag ${status === "Reviewed" ? "status-reviewed" : (status === "Needs Further Investigation" ? "status-further" : (status === "False Positive" ? "status-falsepos" : "status-pending"))}`;
      }
      showNotification(`Human Review saved for flag ${flagId}: [${status}]`, "success");
    }
  } catch (err) {
    showNotification("Error saving review: " + err.message, "danger");
  }
}

// ---------------- Case Table & Search ----------------

function renderCasesTable(cases) {
  const tbody = document.getElementById("casesTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  cases.forEach(c => {
    const tr = document.createElement("tr");
    tr.style.cursor = "pointer";
    tr.innerHTML = `
      <td style="font-weight: 700; color: #38bdf8;">${c.case_id}</td>
      <td style="font-weight: 600;">${c.title}</td>
      <td><span class="flag-badge badge-inf">${c.crime_type}</span></td>
      <td>${c.incident_date} ${c.incident_time ? '@ ' + c.incident_time : ''}</td>
      <td>${c.location || 'N/A'}</td>
      <td>${c.victim || 'N/A'}</td>
      <td>
        <div style="display: flex; gap: 6px;">
          <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); openFirForCase('${c.case_id}')" style="padding: 3px 8px; font-size: 11px;">📑 FIR</button>
          <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); selectCase('${c.case_id}')" style="padding: 3px 8px; font-size: 11px;">Open Case</button>
        </div>
      </td>
    `;
    tr.addEventListener("click", () => selectCase(c.case_id));
    tbody.appendChild(tr);
  });
}

function filterCases() {
  const q = document.getElementById("caseSearchInput").value.toLowerCase();
  const filtered = AppState.cases.filter(c => {
    return (
      c.case_id.toLowerCase().includes(q) ||
      (c.title || "").toLowerCase().includes(q) ||
      (c.crime_type || "").toLowerCase().includes(q) ||
      (c.victim || "").toLowerCase().includes(q) ||
      (c.location || "").toLowerCase().includes(q)
    );
  });
  renderCasesTable(filtered);
}

function selectCase(caseId) {
  loadCase(caseId);
  switchTab("workspace");
}

// ---------------- Report Preview ----------------

function renderReportPreview() {
  const container = document.getElementById("reportPreviewContainer");
  if (!container || !AppState.currentCaseId) return;

  const url = `${API_BASE}/api/cases/${AppState.currentCaseId}/report?format=html`;

  container.innerHTML = `
    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-bottom: 14px;">
      <button type="button" class="btn btn-secondary btn-sm" onclick="downloadCaseReportMarkdown()">⬇️ Export Markdown</button>
      <button type="button" class="btn btn-secondary btn-sm" onclick="printReportIframe()">🖨️ Print Report</button>
      <a class="btn btn-primary btn-sm" href="${url}" target="_blank" rel="noopener">🔗 Open Full Screen</a>
    </div>
    <iframe
      id="reportFrame"
      src="${url}"
      style="width: 100%; height: 870px; border: 1px solid var(--border-card); border-radius: var(--radius-md); background: #ffffff; display: block;"
      onload="this.style.opacity='1'"
      style="opacity:0; transition: opacity 0.4s;"
    ></iframe>
  `;
}

function printReportIframe() {
  const frame = document.getElementById("reportFrame");
  if (frame && frame.contentWindow) {
    frame.contentWindow.focus();
    frame.contentWindow.print();
  }
}

function downloadCaseReportMarkdown() {
  const cid = AppState.currentCaseId || "CASE-001";
  window.open(`${API_BASE}/api/cases/${cid}/report?format=markdown`, "_blank");
}

window.renderReportPreview = renderReportPreview;
window.printReportIframe = printReportIframe;
window.downloadCaseReportMarkdown = downloadCaseReportMarkdown;

// ---------------- Event Handlers ----------------

function initEventHandlers() {
  // Case search input
  const searchInput = document.getElementById("caseSearchInput");
  if (searchInput) searchInput.addEventListener("input", filterCases);

  // Crime type dropdown change
  const crimeSelect = document.getElementById("crimeTypeSelect");
  const customCrimeInput = document.getElementById("crimeTypeCustom");
  if (crimeSelect) {
    crimeSelect.addEventListener("change", (e) => {
      customCrimeInput.style.display = e.target.value === "Other" ? "block" : "none";
    });
  }

  // Save changes button in Workspace
  const saveBtn = document.getElementById("saveCaseBtn");
  if (saveBtn) {
    saveBtn.addEventListener("click", async () => {
      const data = collectWorkspaceData();
      try {
        const res = await fetch(`${API_BASE}/api/cases`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data)
        });
        const resp = await res.json();
        if (resp.status === "success") {
          showNotification("Case changes saved successfully to database.", "success");
          await loadCasesList();
        }
      } catch (e) {
        showNotification("Failed to save: " + e.message, "danger");
      }
    });
  }

  // Run AI Audit button
  const runAuditBtn = document.getElementById("runAuditBtn");
  if (runAuditBtn) {
    runAuditBtn.addEventListener("click", () => runAudit(true));
  }

  // File Uploader & Dropzone
  initDocumentIngestion();
}

// ---------------- Document Ingestion & Sample Files Controller ----------------

async function loadSampleFiles() {
  const grid = document.getElementById("sampleDocsGrid");
  if (!grid) return;

  try {
    const res = await fetch(`${API_BASE}/api/sample-files`);
    const data = await res.json();
    const files = data.sample_files || [];
    renderSampleFilesGrid(files);
  } catch (err) {
    console.warn("Could not load sample files dynamically, using fallback data:", err);
    // Fallback data if server is starting
    renderSampleFilesGrid([
      {
        id: "sample-1",
        filename: "sample_1_forensic_ballistics_report.txt",
        format: "TXT",
        badge_class: "badge-txt",
        title: "SFSL Ballistics & Firearms Analysis",
        description: "Microscopic striation & firing pin comparison confirming 9mm casing E-001 matches seized pistol E-003.",
        size: "1.4 KB",
        category: "Forensic Laboratory Report"
      },
      {
        id: "sample-2",
        filename: "sample_2_cctv_surveillance_analysis.json",
        format: "JSON",
        badge_class: "badge-json",
        title: "Traffic CCTV & ANPR Surveillance Log",
        description: "Automated camera detections, vehicle speed & route tracking (KA-03-HA-9821), and FASTag toll timestamp.",
        size: "2.1 KB",
        category: "Digital Surveillance Record"
      },
      {
        id: "sample-3",
        filename: "sample_3_call_detail_records_cdr.csv",
        format: "CSV",
        badge_class: "badge-csv",
        title: "Call Detail Records (CDR) Tower Dump",
        description: "Multi-cell tower logs mapping suspect mobile device location, call durations, and associate contacts.",
        size: "1.1 KB",
        category: "Telecom Intelligence"
      },
      {
        id: "sample-4",
        filename: "sample_4_eyewitness_supplementary_statement.txt",
        format: "TXT",
        badge_class: "badge-txt",
        title: "Eyewitness Supplementary Statement (Sec 161 CrPC)",
        description: "Security supervisor statement correcting timeline from 20:30 to 21:05 hrs based on guard logbook.",
        size: "1.8 KB",
        category: "Witness Deposition"
      }
    ]);
  }
}

let activeModalDocFilename = "";

function renderSampleFilesGrid(files) {
  const grid = document.getElementById("sampleDocsGrid");
  if (!grid) return;

  grid.innerHTML = files.map(f => `
    <div class="sample-doc-card" onclick="openDocViewer('${f.filename}', '${escapeHtml(f.title)}', '${f.format}')" style="cursor: pointer;">
      <div>
        <div class="sample-doc-header">
          <span class="badge-format ${f.badge_class || 'badge-txt'}">${f.format}</span>
          <span class="sample-doc-meta">${f.size || ''}</span>
        </div>
        <div style="font-size: 11px; color: var(--accent-blue-bright); font-weight: 700; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.4px;">
          ${escapeHtml(f.category || 'Case Evidence')}
        </div>
        <div class="sample-doc-title" style="margin-top: 4px;">
          ${escapeHtml(f.title)}
        </div>
        <div class="sample-doc-desc" style="margin-top: 6px;">
          ${escapeHtml(f.description)}
        </div>
      </div>
      <div class="sample-doc-actions" style="margin-top: 12px; display: flex; gap: 6px; flex-wrap: wrap;">
        <button type="button" class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); openDocViewer('${f.filename}', '${escapeHtml(f.title)}', '${f.format}')" title="Open and read document contents">
          📖 Open & Read
        </button>
        <button type="button" class="btn btn-primary btn-sm" onclick="event.stopPropagation(); ingestSampleFile('${f.filename}')" title="Directly ingest into active case record">
          ⚡ 1-Click Ingest
        </button>
        <a class="btn btn-secondary btn-sm" href="${API_BASE}/api/sample-files/${f.filename}" download="${f.filename}" onclick="event.stopPropagation();" title="Download to your machine">
          ⬇️
        </a>
      </div>
    </div>
  `).join("");
}

async function openDocViewer(filename, title, format) {
  activeModalDocFilename = filename;
  const modal = document.getElementById("docViewerModal");
  const titleEl = document.getElementById("docViewerTitle");
  const metaEl = document.getElementById("docViewerMeta");
  const contentEl = document.getElementById("docViewerContent");
  const downloadBtn = document.getElementById("docViewerDownloadBtn");

  if (!modal) return;

  if (titleEl) titleEl.textContent = title || filename;
  if (metaEl) metaEl.textContent = `Filename: ${filename} | Format: ${format || 'Document'}`;
  if (contentEl) contentEl.textContent = `⏳ Loading document content from ${filename}...`;
  if (downloadBtn) {
    downloadBtn.href = `${API_BASE}/api/sample-files/${filename}`;
    downloadBtn.download = filename;
  }

  modal.classList.add("active");

  try {
    const res = await fetch(`${API_BASE}/api/sample-files/${filename}/content`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (contentEl) {
      contentEl.textContent = data.content || "(Empty document)";
    }
  } catch (err) {
    if (contentEl) {
      contentEl.textContent = `Could not fetch document via API. Attempting direct download preview...\nError: ${err.message}`;
    }
  }
}

function closeDocViewerModal() {
  const modal = document.getElementById("docViewerModal");
  if (modal) modal.classList.remove("active");
}

async function ingestCurrentModalDoc() {
  if (!activeModalDocFilename) return;
  await ingestSampleFile(activeModalDocFilename);
  closeDocViewerModal();
}

async function ingestSampleFile(filename) {
  const currentId = AppState.currentCaseId || "CASE-001";
  const statusBox = document.getElementById("uploadStatusBox");

  if (statusBox) {
    statusBox.style.display = "block";
    statusBox.style.background = "rgba(56, 189, 248, 0.12)";
    statusBox.style.color = "#38bdf8";
    statusBox.style.border = "1px solid rgba(56, 189, 248, 0.35)";
    statusBox.innerHTML = `⏳ Ingesting sample document <b>${escapeHtml(filename)}</b> into case <b>${currentId}</b>...`;
  }

  try {
    const res = await fetch(`${API_BASE}/api/cases/${currentId}/ingest-sample/${filename}`, {
      method: "POST"
    });
    const data = await res.json();
    if (data.status === "success") {
      showNotification(`Sample document ${filename} ingested successfully into ${currentId}!`, "success");
      if (statusBox) {
        statusBox.style.background = "rgba(16, 185, 129, 0.15)";
        statusBox.style.color = "#34d399";
        statusBox.style.border = "1px solid rgba(16, 185, 129, 0.4)";
        statusBox.innerHTML = `✅ Successfully ingested <b>${escapeHtml(filename)}</b> into case records! Vector RAG index updated.`;
      }
      await loadCase(currentId);
    } else {
      throw new Error(data.detail || "Server returned non-success status");
    }
  } catch (err) {
    showNotification("Failed to ingest sample: " + err.message, "danger");
    if (statusBox) {
      statusBox.style.background = "rgba(244, 63, 94, 0.15)";
      statusBox.style.color = "#fb7185";
      statusBox.style.border = "1px solid rgba(244, 63, 94, 0.4)";
      statusBox.innerHTML = `❌ Ingestion failed: ${escapeHtml(err.message)}`;
    }
  }
}

function initDocumentIngestion() {
  loadSampleFiles();

  const fileInput = document.getElementById("caseFileInput");
  const directInput = document.getElementById("caseFileInputDirect");
  const browseBtn = document.getElementById("browseFilesBtn");
  const dropzone = document.getElementById("uploadDropzone");
  const fileNameDisplay = document.getElementById("uploadSelectedFileName");

  // Wire explicit browse button
  if (browseBtn && fileInput) {
    browseBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      fileInput.click();
    });
  }

  // Handle hidden file select
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        if (fileNameDisplay) {
          fileNameDisplay.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
          fileNameDisplay.style.display = "block";
        }
        handleUploadFile(file);
      }
    });
  }

  // Handle direct file select
  if (directInput) {
    directInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        if (fileNameDisplay) {
          fileNameDisplay.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
          fileNameDisplay.style.display = "block";
        }
        handleUploadFile(file);
      }
    });
  }

  // Drag and drop handlers on dropzone
  if (dropzone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("dragover");
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("dragover");
      }, false);
    });

    dropzone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      const file = dt.files[0];
      if (file) {
        if (fileNameDisplay) {
          fileNameDisplay.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
          fileNameDisplay.style.display = "block";
        }
        handleUploadFile(file);
      }
    });
  }
}

async function handleUploadFile(file) {
  if (!file) return;
  const currentId = AppState.currentCaseId || "CASE-001";
  const statusBox = document.getElementById("uploadStatusBox");

  if (statusBox) {
    statusBox.style.display = "block";
    statusBox.style.background = "rgba(56, 189, 248, 0.12)";
    statusBox.style.color = "#38bdf8";
    statusBox.style.border = "1px solid rgba(56, 189, 248, 0.35)";
    statusBox.innerHTML = `⏳ Uploading and parsing <b>${escapeHtml(file.name)}</b>...`;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/api/cases/${currentId}/upload-doc`, {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (data.status === "success") {
      showNotification(`Document ${file.name} ingested successfully!`, "success");
      if (statusBox) {
        statusBox.style.background = "rgba(16, 185, 129, 0.15)";
        statusBox.style.color = "#34d399";
        statusBox.style.border = "1px solid rgba(16, 185, 129, 0.4)";
        statusBox.innerHTML = `✅ Successfully uploaded and indexed <b>${escapeHtml(file.name)}</b>. Notes and vector knowledge base updated!`;
      }
      await loadCase(currentId);
    } else {
      throw new Error(data.detail || "Server error");
    }
  } catch (err) {
    showNotification("File upload failed: " + err.message, "danger");
    if (statusBox) {
      statusBox.style.background = "rgba(244, 63, 94, 0.15)";
      statusBox.style.color = "#fb7185";
      statusBox.style.border = "1px solid rgba(244, 63, 94, 0.4)";
      statusBox.innerHTML = `❌ Upload failed: ${escapeHtml(err.message)}`;
    }
  }
}

  // Create Case Modal
  const createModal = document.getElementById("createCaseModal");
  const openCreateBtn = document.getElementById("openCreateCaseBtn");
  const closeCreateBtn = document.getElementById("closeCreateCaseBtn");
  const submitCreateBtn = document.getElementById("submitCreateCaseBtn");

  if (openCreateBtn) openCreateBtn.addEventListener("click", () => createModal.classList.add("active"));
  if (closeCreateBtn) closeCreateBtn.addEventListener("click", () => createModal.classList.remove("active"));

  if (submitCreateBtn) {
    submitCreateBtn.addEventListener("click", async () => {
      const cid = document.getElementById("newCaseId").value.trim();
      const title = document.getElementById("newCaseTitle").value.trim();
      const crime = document.getElementById("newCaseCrimeType").value;
      if (!cid) {
        alert("Case ID is required");
        return;
      }

      const newCaseObj = {
        case_id: cid,
        title: title || `Investigation ${cid}`,
        crime_type: crime,
        incident_date: new Date().toISOString().split("T")[0],
        incident_time: "20:00",
        location: "Under Investigation",
        victim: "Victim (Pending)",
        suspects: [],
        summary: "New investigation file opened.",
        fir: { fir_number: `FIR-${cid}`, ps: "Main PS", date: new Date().toISOString().split("T")[0], time: "20:00", details: "Initial complaint", sections: "IPC / BNS" },
        witnesses: [],
        cctv: [],
        evidence: [],
        timeline: [],
        chain_of_custody: [],
        notes: []
      };

      try {
        await fetch(`${API_BASE}/api/cases`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newCaseObj)
        });
        createModal.classList.remove("active");
        await loadCasesList();
        selectCase(cid);
        showNotification(`Created case ${cid}`, "success");
      } catch (e) {
        alert("Failed to create case: " + e.message);
      }
    });
  }
}

// ---------------- Helpers ----------------

function showNotification(msg, type = "info") {
  const bar = document.getElementById("toastBar");
  if (!bar) return;
  bar.textContent = msg;
  bar.style.display = "block";
  bar.style.background = type === "danger" ? "#e11d48" : (type === "success" ? "#059669" : "#2563eb");
  setTimeout(() => { bar.style.display = "none"; }, 4500);
}

function escapeHtml(str) {
  if (!str) return "";
  const d = document.createElement("div");
  d.textContent = String(str);
  return d.innerHTML;
}

// ================= FIR MODAL CONTROLLER =================

async function openFirForCase(caseId) {
  try {
    const res = await fetch(`${API_BASE}/api/cases/${caseId}`);
    const data = await res.json();
    if (data.status === "success" && data.case) {
      openFirModal(data.case.data);
    } else {
      showNotification("Could not load case for FIR view", "danger");
    }
  } catch (err) {
    showNotification("Error loading FIR: " + err.message, "danger");
  }
}

function openFirModal(caseData = null) {
  const c = caseData || AppState.currentCase;
  if (!c) {
    showNotification("No active case selected to view FIR", "warning");
    return;
  }

  const fir = c.fir || {};
  const firNumber = fir.fir_number || `FIR-${c.case_id || '2024'}`;
  const firPs = fir.ps || "Central District Police Station";
  const dateStr = fir.date || c.incident_date || "2024-10-12";
  const timeStr = fir.time || c.incident_time || "20:00";
  const sections = fir.sections || (c.crime_type === "Murder" ? "Section 302 IPC / Section 103 BNS" : "Section 379 IPC / Section 303 BNS");
  const locationStr = c.location || "Scene of Occurrence";
  const complainant = fir.complainant || "Officer S. Rawat (SI, Duty Officer)";
  const suspectsStr = (c.suspects && c.suspects.length) ? c.suspects.join(", ") : "Unknown / Under Ongoing Identification";
  
  // Format evidence items
  let evidenceStr = "Secured per seizure memo register.";
  if (c.evidence && c.evidence.length) {
    evidenceStr = c.evidence.map(e => `[${e.evidence_id}: ${e.description || e.type}]`).join(", ");
  }

  // Calculate day of week
  let dayName = "Saturday";
  try {
    if (dateStr) {
      const d = new Date(dateStr);
      dayName = d.toLocaleDateString("en-US", { weekday: "long" });
    }
  } catch(e) {}

  // Populate modal fields
  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl("firDocDistrict", "CENTRAL METROPOLITAN DISTRICT");
  setEl("firDocPs", firPs);
  setEl("firDocYear", dateStr.split("-")[0] || "2024");
  setEl("firDocNumber", firNumber);
  setEl("firDocDateTime", `${dateStr} @ ${timeStr} hrs`);
  setEl("firDocSections", sections);
  setEl("firDocDay", dayName);
  setEl("firDocDate", dateStr);
  setEl("firDocTime", `${timeStr} hrs`);
  setEl("firDocReportedDate", dateStr);
  setEl("firDocLocation", locationStr);
  setEl("firDocComplainant", complainant);
  setEl("firDocComplainantSign", complainant.split("(")[0].trim());
  setEl("firDocSignDate1", dateStr);
  setEl("firDocStampPs", firPs.toUpperCase().replace("POLICE STATION", "PS"));
  setEl("firDocSuspects", suspectsStr);
  setEl("firDocEvidence", evidenceStr);
  setEl("firDocNarrative", fir.details || c.summary || "Incident reported as per police record.");

  const modal = document.getElementById("firModal");
  if (modal) modal.classList.add("active");
}

function closeFirModal() {
  const modal = document.getElementById("firModal");
  if (modal) modal.classList.remove("active");
}

function printFirDocument() {
  window.print();
}

// ================= CCTV MONITOR CONTROLLER =================

function openCurrentCaseCctv() {
  if (AppState.currentCase && AppState.currentCase.cctv && AppState.currentCase.cctv.length > 0) {
    openCctvModal(AppState.currentCase.cctv[0]);
  } else {
    openCctvModalById("CCTV-001");
  }
}

function openCctvModalById(cctvId) {
  if (!AppState.currentCase) return;
  const cctvs = AppState.currentCase.cctv || [];
  let found = null;

  if (cctvId) {
    // 1. Direct match
    found = cctvs.find(item => item.cctv_id === cctvId);
    // 2. Case-insensitive
    if (!found) {
      found = cctvs.find(item => item.cctv_id.toUpperCase() === cctvId.toUpperCase());
    }
    // 3. Extract digits or CCTV-xxx pattern
    if (!found) {
      const m = cctvId.match(/CCTV[-_ ]?(\d+)/i);
      if (m) {
        const num = m[1];
        found = cctvs.find(item => item.cctv_id.includes(num));
      }
    }
    // 4. Substring in either direction
    if (!found) {
      found = cctvs.find(item => cctvId.includes(item.cctv_id) || item.cctv_id.includes(cctvId));
    }
  }

  // If still not found, pick first camera of current case
  if (!found && cctvs.length > 0) {
    found = cctvs[0];
  }

  if (found) {
    openCctvModal(found);
  } else {
    const cleanId = (cctvId && cctvId.length < 15) ? cctvId : "CCTV-001";
    openCctvModal({
      cctv_id: cleanId,
      camera_name: `Security Camera Feed (${cleanId})`,
      timestamp: AppState.currentCase.incident_time || "20:40",
      date: AppState.currentCase.incident_date || "2024-10-12",
      description: "Visual security footage archived in case property room.",
      image_url: "/static/cctv/cctv_CASE-001_CCTV-001.jpg"
    });
  }
}

function openCctvModal(cctv) {
  if (!cctv) return;
  const imgUrl = cctv.image_url || getFallbackCctvImage(cctv.cctv_id, AppState.currentCaseId);

  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl("cctvModalTitle", `${(cctv.cctv_id || 'CAM').toUpperCase()} — ${(cctv.camera_name || 'SECURITY CAMERA').toUpperCase()}`);
  setEl("cctvModalSubtitle", `NVR Storage Channel | 1080P FHD 30FPS | H.264 Lossless Archive`);
  setEl("cctvHudLeft", `[${cctv.cctv_id || 'CAM'}] [REC]`);
  setEl("cctvHudRight", `${cctv.date || AppState.currentCase?.incident_date || '2024-10-12'} ${cctv.timestamp || '20:00'}:15`);
  
  // Dynamic Camera Channel Selector Strip
  const channelsBar = document.getElementById("cctvChannelsBar");
  if (channelsBar) {
    channelsBar.innerHTML = "";
    const caseCctvs = (AppState.currentCase && AppState.currentCase.cctv && AppState.currentCase.cctv.length > 0)
      ? AppState.currentCase.cctv
      : [cctv];

    caseCctvs.forEach((cam, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      const isActive = (cam.cctv_id === cctv.cctv_id);
      btn.className = `btn btn-sm ${isActive ? 'btn-primary' : 'btn-secondary'}`;
      btn.style.cssText = "font-size: 11px; padding: 4px 10px; font-family: var(--font-mono); display: inline-flex; align-items: center; gap: 5px;";
      btn.innerHTML = `<span>📹</span> CH-0${idx + 1}: ${cam.cctv_id}`;
      btn.onclick = () => openCctvModal(cam);
      channelsBar.appendChild(btn);
    });
  }

  const imgEl = document.getElementById("cctvModalImg");
  if (imgEl) {
    // Clear previous error flag so the new image gets a fresh load attempt
    delete imgEl.dataset.errored;
    imgEl.onerror = () => {
      if (!imgEl.dataset.errored) {
        imgEl.dataset.errored = "1";
        imgEl.src = "/static/cctv/cctv_CASE-001_CCTV-001.jpg";
      }
    };
    imgEl.src = imgUrl;
  }

  setEl("cctvModalDesc", cctv.description || "Footage recorded by automated digital surveillance recording system.");
  setEl("cctvModalTime", `${cctv.timestamp || '20:00'} hrs`);
  setEl("cctvModalDate", cctv.date || AppState.currentCase?.incident_date || "2024-10-12");

  // Reset filter
  const container = document.getElementById("cctvScreenContainer");
  if (container) container.className = "cctv-monitor-screen cctv-mode-normal";
  document.querySelectorAll(".cctv-filter-btn").forEach(b => b.classList.toggle("active", b.textContent.includes("Original")));

  // Start live ticking HUD timecode
  if (window.cctvTimeInterval) clearInterval(window.cctvTimeInterval);
  let seconds = 15;
  window.cctvTimeInterval = setInterval(() => {
    seconds++;
    const sStr = String(seconds % 60).padStart(2, '0');
    const hudR = document.getElementById("cctvHudRight");
    if (hudR) {
      hudR.textContent = `${cctv.date || AppState.currentCase?.incident_date || '2024-10-12'} ${cctv.timestamp || '20:00'}:${sStr}`;
    }
  }, 1000);

  const modal = document.getElementById("cctvModal");
  if (modal) modal.classList.add("active");
}

function closeCctvModal() {
  if (window.cctvTimeInterval) clearInterval(window.cctvTimeInterval);
  const modal = document.getElementById("cctvModal");
  if (modal) modal.classList.remove("active");
}

function toggleCctvScanlines(btn) {
  const overlay = document.getElementById("cctvScanlinesOverlay");
  if (!overlay) return;
  const isShown = overlay.style.display !== "none";
  overlay.style.display = isShown ? "none" : "block";
  if (btn) btn.textContent = isShown ? "📺 Scanlines: OFF" : "📺 Scanlines: ON";
}

function setCctvFilter(mode, btn) {
  const container = document.getElementById("cctvScreenContainer");
  if (container) container.className = `cctv-monitor-screen cctv-mode-${mode}`;
  document.querySelectorAll(".cctv-filter-btn").forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
}

function downloadCctvSnapshot() {
  const img = document.getElementById("cctvModalImg");
  if (img && img.src) {
    window.open(img.src, "_blank");
  }
}

// ================= THEME & GRAPH INTERACTION HELPERS =================

function toggleTheme() {
  const isLight = document.body.classList.toggle("light-theme");
  const icon = document.getElementById("themeToggleIcon");
  const text = document.getElementById("themeToggleText");
  if (icon) icon.textContent = isLight ? "☀️" : "🌙";
  if (text) text.textContent = isLight ? "Light" : "Dark";
  localStorage.setItem("theme", isLight ? "light" : "dark");
  if (AppState.graphInstance) {
    AppState.graphInstance.setTheme(!isLight);
  }
}

function setGraphFilter(category, btn) {
  if (AppState.graphInstance) {
    AppState.graphInstance.setFilter(category);
  }
  document.querySelectorAll(".graph-filter-btn").forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
}

function toggleGraphPhysics(btn) {
  if (!AppState.graphInstance) return;
  const running = AppState.graphInstance.togglePhysics();
  if (btn) {
    btn.textContent = running ? "⏸ Pause Force" : "▶ Resume Force";
  }
}

// Global functions for inline HTML calls
window.selectCase = selectCase;
window.saveReviewAction = saveReviewAction;
window.saveReviewNote = saveReviewNote;
window.addWitnessRow = addWitnessRow;
window.addCctvRow = addCctvRow;
window.addEvidenceRow = addEvidenceRow;
window.addTimelineRow = addTimelineRow;
window.addCustodyRow = addCustodyRow;
window.openFirModal = openFirModal;
window.closeFirModal = closeFirModal;
window.printFirDocument = printFirDocument;
window.openFirForCase = openFirForCase;
window.openCurrentCaseCctv = openCurrentCaseCctv;
window.openCctvModal = openCctvModal;
window.openCctvModalById = openCctvModalById;
window.closeCctvModal = closeCctvModal;
window.toggleCctvScanlines = toggleCctvScanlines;
window.setCctvFilter = setCctvFilter;
window.downloadCctvSnapshot = downloadCctvSnapshot;
window.toggleTheme = toggleTheme;
window.setGraphFilter = setGraphFilter;
window.toggleGraphPhysics = toggleGraphPhysics;
window.graphZoomIn = () => { if (AppState.graphInstance) AppState.graphInstance.zoomIn(); };
window.graphZoomOut = () => { if (AppState.graphInstance) AppState.graphInstance.zoomOut(); };
window.graphResetView = () => { if (AppState.graphInstance) AppState.graphInstance.resetView(); };
window.ingestSampleFile = ingestSampleFile;
window.loadSampleFiles = loadSampleFiles;
window.openDocViewer = openDocViewer;
window.closeDocViewerModal = closeDocViewerModal;
window.ingestCurrentModalDoc = ingestCurrentModalDoc;


