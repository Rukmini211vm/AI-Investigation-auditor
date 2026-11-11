/**
 * AI Investigation Auditor — Chronology & Conflict Visualizer
 * Renders investigative events, CCTV surveillance captures, and witness testimony
 * along a high-precision chronological track with conflict badges and footage previews.
 */

class TimelineVisualizer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
  }

  render(timeline, flags = [], caseData = null) {
    const fullCase = caseData || (window.AppState && window.AppState.currentCase) || { timeline: timeline || [] };
    this.setData(fullCase, flags);
  }

  setData(caseData, auditFlags = []) {
    if (!this.container) return;
    this.container.innerHTML = "";

    // 1. Gather explicit timeline events
    const rawEvents = [...(caseData.timeline || [])];

    // 2. Weave in CCTV footage records if not already represented
    const cctvRecords = caseData.cctv || [];
    cctvRecords.forEach((c, idx) => {
      const alreadyPresent = rawEvents.some(e => 
        (e.source && (e.source.includes(c.cctv_id) || c.cctv_id.includes(e.source))) ||
        (e.description && e.description.includes(c.cctv_id))
      );
      if (!alreadyPresent && c.timestamp) {
        rawEvents.push({
          event_id: `EVT-${c.cctv_id}`,
          time: c.timestamp,
          date: c.date || caseData.incident_date,
          description: `Surveillance capture on ${c.camera_name || c.cctv_id}: ${c.description || 'Footage archived'}`,
          source: c.cctv_id,
          isCctvNative: true,
          cctvItem: c
        });
      }
    });

    if (rawEvents.length === 0) {
      this.container.innerHTML = `
        <div style="padding: 32px; text-align: center; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-lg); border: 1px dashed var(--border-subtle);">
          <div style="font-size: 28px; margin-bottom: 8px;">⏱️</div>
          <div style="font-weight: 700;">No timeline events recorded</div>
          <div style="font-size: 12px; margin-top: 4px;">Add chronological records or CCTV surveillance entries in the Case Dossier Editor.</div>
        </div>
      `;
      return;
    }

    // 3. Sort chronologically by minutes from midnight
    const parseTime = (t) => {
      if (!t) return 9999;
      const parts = t.split(":");
      return parseInt(parts[0] || 0) * 60 + parseInt(parts[1] || 0);
    };

    const sorted = rawEvents.sort((a, b) => parseTime(a.time) - parseTime(b.time));

    // 4. Identify conflict timestamps from audit flags
    const conflictTimes = new Set();
    auditFlags.forEach(f => {
      if (f.category && f.category.includes('Timeline') && f.timestamps) {
        f.timestamps.forEach(t => conflictTimes.add(t));
      }
    });

    const track = document.createElement('div');
    track.className = 'timeline-track';

    sorted.forEach((evt, idx) => {
      const isConflict = conflictTimes.has(evt.time) || auditFlags.some(f => 
        f.source_records && f.source_records.some(src => 
          src.includes(evt.source || '') || (evt.event_id && src.includes(evt.event_id))
        )
      );

      // Check if source references FIR or CCTV
      let sourceHtml = evt.source || 'Investigation Record';
      let cctvPreviewHtml = '';

      if (evt.source && evt.source.toUpperCase().includes('FIR')) {
        sourceHtml = `<span class="fir-pill-clickable" onclick="window.openFirModal()" title="Click to open official FIR format">📑 ${evt.source}</span>`;
      } else {
        // Robust CCTV matching: by ID, camera number, or closest timestamp
        let cctvMatch = evt.cctvItem || null;
        if (!cctvMatch && cctvRecords.length > 0) {
          if (evt.source && evt.source.toUpperCase().includes('CCTV')) {
            const m = evt.source.match(/CCTV[-_ ]?(\d+)/i);
            const num = m ? m[1] : '';
            cctvMatch = cctvRecords.find(c => 
              (num && c.cctv_id.includes(num)) ||
              evt.source.includes(c.cctv_id) ||
              c.cctv_id.includes(evt.source)
            );
          }
          if (!cctvMatch && evt.time) {
            cctvMatch = cctvRecords.find(c => c.timestamp === evt.time);
          }
        }

        if (cctvMatch) {
          const imgUrl = cctvMatch.image_url || `/static/cctv/cctv_${caseData.case_id || 'CASE-001'}_${cctvMatch.cctv_id}.jpg`;
          sourceHtml = `<span style="color: #38bdf8; font-weight: 700; cursor: pointer;" onclick="window.openCctvModalById('${cctvMatch.cctv_id}')" title="Click to view live CCTV player">📹 ${cctvMatch.cctv_id} (${cctvMatch.camera_name || 'Camera'})</span>`;

          cctvPreviewHtml = `
            <div style="display: flex; align-items: center; gap: 12px; margin-top: 10px; background: rgba(8, 12, 22, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.28);">
              <div class="cctv-thumb-box" style="width: 128px; height: 72px; flex-shrink: 0; cursor: pointer;" onclick="window.openCctvModalById('${cctvMatch.cctv_id}')">
                <img src="${imgUrl}" alt="${cctvMatch.cctv_id}" onerror="this.src='/static/cctv/cctv_CASE-001_CCTV-001.jpg'">
                <div class="cctv-hud-top" style="padding: 2px 4px; font-size: 8px;">
                  <span><span class="cctv-rec-dot" style="width: 5px; height: 5px;"></span>REC</span>
                  <span>1080P</span>
                </div>
                <span class="cctv-zoom-badge" style="font-size: 9px; padding: 2px 6px;">🔍 Full Screen</span>
              </div>
              <div style="flex: 1; min-width: 0;">
                <div style="font-weight: 800; color: #38bdf8; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                  📹 ${cctvMatch.camera_name || cctvMatch.cctv_id}
                </div>
                <div style="color: var(--text-muted); font-size: 11px; margin-top: 2px; font-family: var(--font-mono);">
                  Timecode: ${cctvMatch.timestamp || evt.time} hrs • Lossless Archive
                </div>
                <button type="button" class="btn btn-secondary btn-sm" style="padding: 3px 10px; font-size: 11px; margin-top: 6px; display: inline-flex; align-items: center; gap: 5px;" onclick="window.openCctvModalById('${cctvMatch.cctv_id}')">
                  <span>📹</span> Inspect Video Feed
                </button>
              </div>
            </div>
          `;
        }
      }

      const item = document.createElement('div');
      item.className = 'timeline-item';

      item.innerHTML = `
        <div class="timeline-dot ${isConflict ? 'dot-conflict' : ''}"></div>
        <div class="timeline-card" style="${isConflict ? 'border-color: rgba(244, 63, 94, 0.6); box-shadow: 0 4px 16px rgba(244, 63, 94, 0.15);' : ''}">
          <div class="timeline-time">
            <span style="font-family: var(--font-mono); font-weight: 700; color: var(--accent-blue-bright, #38bdf8);">
              ⏱️ ${evt.time || 'Unspecified'} hrs (${evt.date || caseData.incident_date || 'Date N/A'})
            </span>
            ${isConflict ? '<span class="flag-badge badge-crit" style="font-size: 10px; padding: 2px 8px;">⚠️ Discrepancy Flagged</span>' : ''}
          </div>
          <div class="timeline-desc" style="font-size: 13px; line-height: 1.5; margin-top: 4px;">
            ${evt.description || 'No description recorded'}
          </div>
          ${cctvPreviewHtml}
          <div class="timeline-source" style="margin-top: 8px; font-size: 11px; border-top: 1px dashed var(--border-subtle); padding-top: 6px;">
            <strong>Evidentiary Source:</strong> ${sourceHtml} | <strong style="font-family: var(--font-mono);">Ref:</strong> ${evt.event_id || 'EVT-' + (idx + 1)}
          </div>
        </div>
      `;
      track.appendChild(item);
    });

    this.container.appendChild(track);
  }
}

window.TimelineVisualizer = TimelineVisualizer;
