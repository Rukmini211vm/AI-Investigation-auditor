/**
 * AI Investigation Auditor — Interactive Evidence Relationship Matrix Graph
 * High-performance HTML5 Canvas Force-Directed Graph with:
 * - High-contrast luminous lines & directional arrows
 * - Entity-type distinctive icons (🏛️ Case, 🛡️ Victim, 👤 Suspect, 👁️ Witness, 📹 CCTV, 🔬 Evidence, ⚠️ Missing)
 * - Spring-charge physics simulation with damping and drag-to-position
 * - Interactive Pan & Zoom (mouse wheel + buttons)
 * - Hover path highlighting & Rich Tactical HUD inspection card
 * - Click-to-inspect CCTV Surveillance feeds and Official FIR
 * - Category filtering & Zoom controls
 */

class RelationshipGraph {
  constructor(canvasId) {
    this.canvasId = canvasId;
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    this.nodes = [];
    this.links = [];
    this.activeFilter = 'all';

    // Viewport transform (Pan & Zoom)
    this.scale = 1.0;
    this.panX = 0;
    this.panY = 0;
    this.isPanning = false;
    this.panStartX = 0;
    this.panStartY = 0;

    // Interaction states
    this.draggedNode = null;
    this.hoveredNode = null;
    this.connectedNodeIds = new Set();
    this.physicsRunning = true;
    this.animationId = null;

    // Theme detection
    this.isDark = true;

    this.resize();
    this.initEvents();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    // Fallback if tab is hidden (getBoundingClientRect returns 0)
    const w = rect.width > 0 ? rect.width : (this.canvas.parentElement?.clientWidth || 1100);
    const h = rect.height > 0 ? rect.height : 560;

    // Set display buffer resolution
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;

    // Physical logical dimensions
    this.width = w;
    this.height = h;

    // Reset transform and set DPR scale
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.scale(dpr, dpr);
  }

  setTheme(isDark) {
    this.isDark = isDark;
    this.draw();
  }

  setData(caseData, auditFlags = []) {
    if (!this.canvas || !caseData) return;
    this.resize();
    this.nodes = [];
    this.links = [];

    // Reset pan & zoom to center
    this.scale = 1.0;
    this.panX = 0;
    this.panY = 0;

    const caseId = caseData.case_id || "CASE-001";
    const centerX = this.width / 2;
    const centerY = this.height / 2;

    // 1. Center Case Node (Executive Statutory Gold)
    const rootNode = {
      id: caseId,
      label: caseId,
      sublabel: caseData.crime_type || "Incident",
      type: 'case',
      icon: '🏛️',
      color: '#f59e0b',
      glowColor: 'rgba(245, 158, 11, 0.45)',
      x: centerX,
      y: centerY,
      vx: 0, vy: 0,
      radius: 34,
      fixed: true,
      details: `${caseData.crime_type || 'CrPC/BNSS Investigation'} • ${caseData.title || ''} (${caseData.incident_date || ''})`
    };
    this.nodes.push(rootNode);

    // 2. Victim Node (Amethyst Violet)
    if (caseData.victim) {
      const vName = caseData.victim.split('(')[0].trim();
      const vNode = {
        id: 'victim',
        label: vName,
        sublabel: 'Victim / Complainant',
        type: 'victim',
        icon: '🛡️',
        color: '#a855f7',
        glowColor: 'rgba(168, 85, 247, 0.45)',
        x: centerX - 200,
        y: centerY - 140,
        vx: 0, vy: 0,
        radius: 25,
        details: `Victim: ${caseData.victim}`
      };
      this.nodes.push(vNode);
      this.links.push({
        source: rootNode,
        target: vNode,
        label: 'Subject of Crime',
        type: 'subject',
        color: '#a855f7'
      });
    }

    // 3. Suspect Nodes (Vivid Amber-Orange)
    const suspectNodes = [];
    (caseData.suspects || []).forEach((s, idx) => {
      const sName = s.split('(')[0].trim();
      const sNode = {
        id: `suspect_${idx}`,
        label: sName,
        sublabel: `Suspect #${idx + 1}`,
        type: 'suspect',
        icon: '👤',
        color: '#f97316',
        glowColor: 'rgba(249, 115, 22, 0.45)',
        x: centerX + 200 + (idx * 50),
        y: centerY - 140 + (idx * 55),
        vx: 0, vy: 0,
        radius: 24,
        details: `Accused/Named: ${s}`
      };
      this.nodes.push(sNode);
      suspectNodes.push(sNode);
      this.links.push({
        source: rootNode,
        target: sNode,
        label: 'Named in FIR',
        type: 'accused',
        color: '#f97316'
      });
    });

    // 4. Witness Nodes (Surveillance Cyan)
    const witnessNodes = [];
    const witnessList = caseData.witnesses || [];
    witnessList.forEach((w, idx) => {
      const totalW = Math.max(1, witnessList.length);
      const angle = (idx / totalW) * Math.PI * 0.75 + Math.PI * 0.6;
      const dist = 240;
      const wNode = {
        id: w.witness_id || `WS-${idx + 1}`,
        label: w.witness_id || `WS-${idx + 1}`,
        sublabel: w.name ? w.name.split(' ')[0] : 'Witness',
        type: 'witness',
        icon: '👁️',
        color: '#06b6d4',
        glowColor: 'rgba(6, 182, 212, 0.45)',
        x: centerX + Math.cos(angle) * dist,
        y: centerY + Math.sin(angle) * dist - 30,
        vx: 0, vy: 0,
        radius: 23,
        details: `${w.witness_id}: ${w.name || 'Witness'} • Claimed Time: ${w.claimed_time || 'N/A'} • ${w.statement || ''}`
      };
      this.nodes.push(wNode);
      witnessNodes.push(wNode);
      this.links.push({
        source: rootNode,
        target: wNode,
        label: 'Sec 161 CrPC',
        type: 'testimony',
        color: '#06b6d4'
      });

      // If witness mentions suspect, link them
      if (suspectNodes.length > 0 && w.statement) {
        const stmt = w.statement.toLowerCase();
        suspectNodes.forEach(sNode => {
          if (stmt.includes(sNode.label.toLowerCase()) || stmt.includes('saw') || stmt.includes('identify')) {
            this.links.push({
              source: wNode,
              target: sNode,
              label: 'Eyewitness ID',
              type: 'identification',
              color: '#38bdf8',
              dashed: false
            });
          }
        });
      }
    });

    // 5. CCTV Camera Nodes (Electric Sky Blue)
    const cctvNodes = [];
    const cctvList = caseData.cctv || [];
    cctvList.forEach((c, idx) => {
      const totalC = Math.max(1, cctvList.length);
      const angle = (idx / totalC) * Math.PI * 0.75 - Math.PI * 0.4;
      const dist = 250;
      const cNode = {
        id: c.cctv_id || `CCTV-${idx + 1}`,
        label: c.cctv_id || `CAM-${idx + 1}`,
        sublabel: c.camera_name ? c.camera_name.split('(')[0].trim().slice(0, 16) : 'Surveillance',
        type: 'cctv',
        icon: '📹',
        color: '#38bdf8',
        glowColor: 'rgba(56, 189, 248, 0.5)',
        x: centerX + Math.cos(angle) * dist,
        y: centerY + Math.sin(angle) * dist - 20,
        vx: 0, vy: 0,
        radius: 24,
        cctvData: c,
        details: `${c.cctv_id}: ${c.camera_name || 'Channel'} • Recorded: ${c.timestamp || ''} • ${c.description || ''}`
      };
      this.nodes.push(cNode);
      cctvNodes.push(cNode);
      this.links.push({
        source: rootNode,
        target: cNode,
        label: 'Surveillance DVR',
        type: 'footage',
        color: '#38bdf8'
      });

      // Link CCTV to suspects if camera description references suspect or departure
      if (suspectNodes.length > 0 && c.description) {
        const desc = c.description.toLowerCase();
        if (desc.includes('suspect') || desc.includes('individual') || desc.includes('exit') || desc.includes('enter')) {
          this.links.push({
            source: cNode,
            target: suspectNodes[idx % suspectNodes.length],
            label: 'Footage Match',
            type: 'footage_capture',
            color: '#60a5fa',
            dashed: false
          });
        }
      }
    });

    // 6. Physical Evidence Items (Forensic Emerald or Amber Unresolved)
    const evidenceList = caseData.evidence || [];
    const missingEvidenceIds = new Set();
    auditFlags.forEach(f => {
      if (f.category && f.category.includes('Missing Evidence')) {
        const match = f.title.match(/E-\d+/);
        if (match) missingEvidenceIds.add(match[0]);
      }
    });

    const evidenceNodes = [];
    evidenceList.forEach((e, idx) => {
      const isUnresolved = auditFlags.some(f => 
        (f.category && f.category.includes('Unresolved') && f.title.includes(e.evidence_id)) ||
        (f.source_records && f.source_records.some(sr => sr.includes(e.evidence_id)))
      );
      const eNode = {
        id: e.evidence_id || `E-${idx + 1}`,
        label: e.evidence_id || `E-${idx + 1}`,
        sublabel: e.type ? e.type.slice(0, 14) : 'Property',
        type: 'evidence',
        icon: '🔬',
        color: isUnresolved ? '#eab308' : '#10b981',
        glowColor: isUnresolved ? 'rgba(234, 179, 8, 0.45)' : 'rgba(16, 185, 129, 0.45)',
        x: centerX - 130 + (idx * 90),
        y: centerY + 180 + ((idx % 2) * 35),
        vx: 0, vy: 0,
        radius: 23,
        details: `${e.evidence_id}: ${e.type} • ${e.description} • Recovered at: ${e.recovered_from || 'Scene'}`
      };
      this.nodes.push(eNode);
      evidenceNodes.push(eNode);
      this.links.push({
        source: rootNode,
        target: eNode,
        label: isUnresolved ? 'Unresolved Link' : 'Seized / Sealed',
        type: isUnresolved ? 'unresolved' : 'seizure',
        color: isUnresolved ? '#eab308' : '#10b981',
        dashed: isUnresolved
      });

      // Link evidence to suspect if recovered from suspect
      if (suspectNodes.length > 0 && e.recovered_from) {
        const rec = e.recovered_from.toLowerCase();
        suspectNodes.forEach(sNode => {
          if (rec.includes(sNode.label.toLowerCase()) || rec.includes('suspect') || rec.includes('person')) {
            this.links.push({
              source: eNode,
              target: sNode,
              label: 'Recovered From',
              type: 'seized_from',
              color: '#34d399'
            });
          }
        });
      }
    });

    // 7. Ghost / Critical Missing Evidence (Neon Crimson Pulsing)
    missingEvidenceIds.forEach((mid, idx) => {
      const mNode = {
        id: mid,
        label: `MISSING: ${mid}`,
        sublabel: 'Audit Gap Alert',
        type: 'missing_evidence',
        icon: '⚠️',
        color: '#f43f5e',
        glowColor: 'rgba(244, 63, 94, 0.6)',
        x: centerX + 140 + (idx * 80),
        y: centerY + 200,
        vx: 0, vy: 0,
        radius: 25,
        isAlert: true,
        details: `CRITICAL GAP: ${mid} is cited in witness/interrogation statements but completely absent from the official Evidence Register!`
      };
      this.nodes.push(mNode);
      this.links.push({
        source: rootNode,
        target: mNode,
        label: 'Unregistered Reference',
        type: 'missing',
        color: '#f43f5e',
        dashed: true
      });

      if (witnessNodes.length > 0) {
        this.links.push({
          source: witnessNodes[0],
          target: mNode,
          label: 'Mentioned in Statement',
          type: 'unrecorded_ref',
          color: '#fb7185',
          dashed: true
        });
      }
    });

    this.startSimulation();
  }

  setFilter(category) {
    this.activeFilter = category;
    this.draw();
  }

  initEvents() {
    if (!this.canvas) return;

    // Mouse Down: Node Drag or Canvas Pan
    this.canvas.addEventListener('mousedown', (e) => {
      const pos = this.getCanvasPos(e);
      const clicked = this.getNodeAt(pos.x, pos.y);

      if (clicked) {
        this.draggedNode = clicked;
        this.draggedNode.fixed = true;
      } else {
        this.isPanning = true;
        this.panStartX = e.clientX - this.panX;
        this.panStartY = e.clientY - this.panY;
        this.canvas.style.cursor = 'grabbing';
      }
    });

    // Mouse Move: Dragging, Panning, or Hovering
    this.canvas.addEventListener('mousemove', (e) => {
      if (this.draggedNode) {
        const pos = this.getCanvasPos(e);
        this.draggedNode.x = pos.x;
        this.draggedNode.y = pos.y;
        this.draggedNode.vx = 0;
        this.draggedNode.vy = 0;
        return;
      }

      if (this.isPanning) {
        this.panX = e.clientX - this.panStartX;
        this.panY = e.clientY - this.panStartY;
        return;
      }

      const pos = this.getCanvasPos(e);
      const hovered = this.getNodeAt(pos.x, pos.y);

      if (hovered !== this.hoveredNode) {
        this.hoveredNode = hovered;
        this.updateConnectedSet();
        this.canvas.style.cursor = hovered ? 'pointer' : 'default';
      }
    });

    // Mouse Up: End drag or pan
    window.addEventListener('mouseup', () => {
      if (this.draggedNode) {
        if (this.draggedNode.type !== 'case') {
          this.draggedNode.fixed = false;
        }
        this.draggedNode = null;
      }
      if (this.isPanning) {
        this.isPanning = false;
        if (this.canvas) this.canvas.style.cursor = 'default';
      }
    });

    // Wheel: Smooth Zoom towards mouse cursor
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const rect = this.canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
      const newScale = Math.max(0.4, Math.min(2.8, this.scale * zoomFactor));

      this.panX = mouseX - (mouseX - this.panX) * (newScale / this.scale);
      this.panY = mouseY - (mouseY - this.panY) * (newScale / this.scale);
      this.scale = newScale;
    }, { passive: false });

    // Click: Node inspection actions
    this.canvas.addEventListener('click', (e) => {
      if (Math.abs(e.movementX) > 4 || Math.abs(e.movementY) > 4) return;

      const pos = this.getCanvasPos(e);
      const clicked = this.getNodeAt(pos.x, pos.y);
      if (clicked) {
        if (clicked.type === 'cctv') {
          if (window.openCctvModalById) window.openCctvModalById(clicked.id);
        } else if (clicked.type === 'case') {
          if (window.openFirModal) window.openFirModal();
        } else if (clicked.type === 'missing_evidence') {
          const auditTab = document.querySelector('.nav-tab[data-tab="audit"]');
          if (auditTab) auditTab.click();
        }
      }
    });

    window.addEventListener('resize', () => {
      this.resize();
    });
  }

  getCanvasPos(e) {
    const rect = this.canvas.getBoundingClientRect();
    const rawX = e.clientX - rect.left;
    const rawY = e.clientY - rect.top;
    return {
      x: (rawX - this.panX) / this.scale,
      y: (rawY - this.panY) / this.scale
    };
  }

  getNodeAt(x, y) {
    for (let i = this.nodes.length - 1; i >= 0; i--) {
      const n = this.nodes[i];
      if (!this.isNodeVisible(n)) continue;
      const dist = Math.hypot(n.x - x, n.y - y);
      if (dist <= n.radius + 6) return n;
    }
    return null;
  }

  isNodeVisible(node) {
    if (!node) return false;
    if (this.activeFilter === 'all') return true;
    if (this.activeFilter === 'suspects' && (node.type === 'suspect' || node.type === 'witness' || node.type === 'victim' || node.type === 'case')) return true;
    if (this.activeFilter === 'cctv' && (node.type === 'cctv' || node.type === 'case')) return true;
    if (this.activeFilter === 'evidence' && (node.type === 'evidence' || node.type === 'missing_evidence' || node.type === 'case')) return true;
    if (this.activeFilter === 'conflicts' && (node.isAlert || node.color === '#eab308' || node.type === 'missing_evidence' || node.type === 'case')) return true;
    return false;
  }

  updateConnectedSet() {
    this.connectedNodeIds.clear();
    if (!this.hoveredNode) return;

    this.connectedNodeIds.add(this.hoveredNode.id);
    this.links.forEach(l => {
      if (l.source.id === this.hoveredNode.id) {
        this.connectedNodeIds.add(l.target.id);
      } else if (l.target.id === this.hoveredNode.id) {
        this.connectedNodeIds.add(l.source.id);
      }
    });
  }

  // Physics Simulation: Smooth Spring Forces + Coulomb Repulsion with Zero-Division Guards
  stepPhysics() {
    if (!this.physicsRunning) return;

    const visibleNodes = this.nodes.filter(n => this.isNodeVisible(n));
    const kRepel = 2200;
    const kSpring = 0.045;
    const damping = 0.82;

    // 1. Repulsion between all node pairs
    for (let i = 0; i < visibleNodes.length; i++) {
      const n1 = visibleNodes[i];
      for (let j = i + 1; j < visibleNodes.length; j++) {
        const n2 = visibleNodes[j];
        const dx = n2.x - n1.x;
        const dy = n2.y - n1.y;
        let dist = Math.hypot(dx, dy);
        if (dist < 10) dist = 10;
        if (dist < 340) {
          const force = Math.min(8, kRepel / (dist * dist));
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          if (!n1.fixed && n1 !== this.draggedNode) { n1.vx -= fx; n1.vy -= fy; }
          if (!n2.fixed && n2 !== this.draggedNode) { n2.vx += fx; n2.vy += fy; }
        }
      }
    }

    // 2. Spring attraction along links
    this.links.forEach(l => {
      if (!this.isNodeVisible(l.source) || !this.isNodeVisible(l.target)) return;
      const dx = l.target.x - l.source.x;
      const dy = l.target.y - l.source.y;
      let dist = Math.hypot(dx, dy);
      if (dist < 1) dist = 1;
      const targetDist = (l.target.type === 'case' || l.source.type === 'case') ? 180 : 130;
      const displacement = dist - targetDist;
      const force = Math.max(-10, Math.min(10, displacement * kSpring));
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;

      if (!l.source.fixed && l.source !== this.draggedNode) {
        l.source.vx += fx;
        l.source.vy += fy;
      }
      if (!l.target.fixed && l.target !== this.draggedNode) {
        l.target.vx -= fx;
        l.target.vy -= fy;
      }
    });

    // 3. Center gravity and position integration with NaN guard
    const centerX = this.width / 2;
    const centerY = this.height / 2;
    visibleNodes.forEach(n => {
      // Guard against NaN or infinite values
      if (isNaN(n.x) || !isFinite(n.x)) n.x = centerX + (Math.random() - 0.5) * 80;
      if (isNaN(n.y) || !isFinite(n.y)) n.y = centerY + (Math.random() - 0.5) * 80;
      if (isNaN(n.vx) || !isFinite(n.vx)) n.vx = 0;
      if (isNaN(n.vy) || !isFinite(n.vy)) n.vy = 0;

      if (n.fixed || n === this.draggedNode) return;
      n.vx += (centerX - n.x) * 0.0012;
      n.vy += (centerY - n.y) * 0.0012;

      n.vx = Math.max(-15, Math.min(15, n.vx * damping));
      n.vy = Math.max(-15, Math.min(15, n.vy * damping));

      n.x += n.vx;
      n.y += n.vy;
    });
  }

  startSimulation() {
    if (this.animationId) cancelAnimationFrame(this.animationId);

    const loop = (time) => {
      this.stepPhysics();
      this.draw(time);
      this.animationId = requestAnimationFrame(loop);
    };
    this.animationId = requestAnimationFrame(loop);
  }

  // Draw Radar Tactical Grid, Glowing Links, and High-Contrast Nodes
  draw(timestamp = 0) {
    if (!this.ctx) return;

    // Reset transform to identity and clear screen
    const dpr = window.devicePixelRatio || 1;
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Reapply DPR + Pan & Zoom
    this.ctx.scale(dpr, dpr);
    this.ctx.save();
    this.ctx.translate(this.panX, this.panY);
    this.ctx.scale(this.scale, this.scale);

    // 1. Draw Tactical Grid
    this.drawTacticalGrid();

    // 2. Draw Links (Thick, Luminous, with Arrowheads and Text Pills)
    this.drawLinks(timestamp);

    // 3. Draw Nodes (Glyph Icons, High Contrast, Halo)
    this.drawNodes(timestamp);

    this.ctx.restore();

    // 4. Draw Floating HUD Tooltip in Screen Space
    this.drawHoverHUD();
  }

  drawTacticalGrid() {
    const gridSpacing = 50;
    const minX = -this.panX / this.scale - 100;
    const maxX = (this.width - this.panX) / this.scale + 100;
    const minY = -this.panY / this.scale - 100;
    const maxY = (this.height - this.panY) / this.scale + 100;

    const startX = Math.floor(minX / gridSpacing) * gridSpacing;
    const startY = Math.floor(minY / gridSpacing) * gridSpacing;

    this.ctx.save();
    this.ctx.strokeStyle = this.isDark ? 'rgba(56, 189, 248, 0.08)' : 'rgba(37, 99, 235, 0.08)';
    this.ctx.lineWidth = 1;

    this.ctx.beginPath();
    for (let x = startX; x <= maxX; x += gridSpacing) {
      this.ctx.moveTo(x, minY);
      this.ctx.lineTo(x, maxY);
    }
    for (let y = startY; y <= maxY; y += gridSpacing) {
      this.ctx.moveTo(minX, y);
      this.ctx.lineTo(maxX, y);
    }
    this.ctx.stroke();

    // Radar concentric rings around center case
    const cx = this.width / 2;
    const cy = this.height / 2;
    this.ctx.strokeStyle = this.isDark ? 'rgba(56, 189, 248, 0.12)' : 'rgba(37, 99, 235, 0.12)';
    [150, 270, 390].forEach(r => {
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, r, 0, Math.PI * 2);
      this.ctx.stroke();
    });

    this.ctx.restore();
  }

  drawLinks(timestamp) {
    this.links.forEach(l => {
      if (!this.isNodeVisible(l.source) || !this.isNodeVisible(l.target)) return;

      const isHovered = this.hoveredNode && (this.hoveredNode === l.source || this.hoveredNode === l.target);
      const isDimmed = this.hoveredNode && !isHovered;

      this.ctx.save();
      this.ctx.beginPath();
      this.ctx.moveTo(l.source.x, l.source.y);
      this.ctx.lineTo(l.target.x, l.target.y);

      let strokeColor = l.color || (this.isDark ? '#38bdf8' : '#2563eb');
      let lineWidth = isHovered ? 4.5 : 3.0;

      if (l.dashed) {
        strokeColor = l.color || '#f43f5e';
        lineWidth = 3.2;
        this.ctx.setLineDash([8, 6]);
        this.ctx.lineDashOffset = -((timestamp / 25) % 14);
      } else {
        this.ctx.setLineDash([]);
      }

      if (isHovered) {
        this.ctx.shadowColor = strokeColor;
        this.ctx.shadowBlur = 16;
      } else if (isDimmed) {
        this.ctx.globalAlpha = 0.22;
      }

      this.ctx.strokeStyle = strokeColor;
      this.ctx.lineWidth = lineWidth;
      this.ctx.stroke();
      this.ctx.shadowBlur = 0;

      // Draw Arrow pointing from source to target
      this.drawArrow(l.source, l.target, strokeColor, isDimmed);

      // Draw High-Contrast Link Label Pill
      if (l.label && (!isDimmed || isHovered)) {
        const mx = (l.source.x + l.target.x) / 2;
        const my = (l.source.y + l.target.y) / 2;
        this.drawLinkPill(l.label, mx, my, strokeColor, l.dashed);
      }

      this.ctx.restore();
    });
  }

  drawArrow(source, target, color, isDimmed) {
    const angle = Math.atan2(target.y - source.y, target.x - source.x);
    const arrowDist = target.radius + 4;
    const ax = target.x - Math.cos(angle) * arrowDist;
    const ay = target.y - Math.sin(angle) * arrowDist;
    const arrowLength = 13;

    this.ctx.save();
    if (isDimmed) this.ctx.globalAlpha = 0.22;
    this.ctx.fillStyle = color;
    this.ctx.beginPath();
    this.ctx.moveTo(ax, ay);
    this.ctx.lineTo(
      ax - arrowLength * Math.cos(angle - Math.PI / 7),
      ay - arrowLength * Math.sin(angle - Math.PI / 7)
    );
    this.ctx.lineTo(
      ax - (arrowLength * 0.7) * Math.cos(angle),
      ay - (arrowLength * 0.7) * Math.sin(angle)
    );
    this.ctx.lineTo(
      ax - arrowLength * Math.cos(angle + Math.PI / 7),
      ay - arrowLength * Math.sin(angle + Math.PI / 7)
    );
    this.ctx.closePath();
    this.ctx.fill();
    this.ctx.restore();
  }

  drawLinkPill(text, x, y, color, isDashed) {
    this.ctx.save();
    this.ctx.font = 'bold 10px "JetBrains Mono", monospace';
    const textWidth = this.ctx.measureText(text).width;
    const padX = 8;
    const boxW = textWidth + padX * 2;
    const boxH = 19;

    this.ctx.fillStyle = this.isDark ? '#060a14' : '#ffffff';
    this.ctx.strokeStyle = isDashed ? '#f43f5e' : (this.isDark ? 'rgba(56, 189, 248, 0.6)' : 'rgba(37, 99, 235, 0.6)');
    this.ctx.lineWidth = 1.2;

    this.ctx.beginPath();
    this.roundRect(x - boxW / 2, y - boxH / 2, boxW, boxH, 4);
    this.ctx.fill();
    this.ctx.stroke();

    this.ctx.fillStyle = isDashed ? '#fb7185' : (this.isDark ? '#f8fafc' : '#0f172a');
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText(text, x, y);
    this.ctx.restore();
  }

  drawNodes(timestamp) {
    this.nodes.forEach(n => {
      if (!this.isNodeVisible(n)) return;

      const isHovered = (n === this.hoveredNode);
      const isConnected = this.connectedNodeIds.has(n.id);
      const isDimmed = this.hoveredNode && !isConnected;

      this.ctx.save();
      if (isDimmed) this.ctx.globalAlpha = 0.22;

      const r = isHovered ? n.radius + 4 : n.radius;

      // Outer Halo Glow
      this.ctx.beginPath();
      this.ctx.arc(n.x, n.y, r + 5, 0, Math.PI * 2);
      this.ctx.fillStyle = n.glowColor || 'rgba(56, 189, 248, 0.35)';
      this.ctx.fill();

      // Main Node Fill
      this.ctx.beginPath();
      this.ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
      this.ctx.fillStyle = n.color;
      this.ctx.shadowColor = n.color;
      this.ctx.shadowBlur = isHovered ? 20 : 10;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      // Inner Border Ring
      this.ctx.strokeStyle = '#ffffff';
      this.ctx.lineWidth = isHovered ? 2.5 : 2;
      this.ctx.stroke();

      // Center Icon
      if (n.icon) {
        this.ctx.font = `${Math.round(r * 0.95)}px -apple-system, sans-serif`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(n.icon, n.x, n.y + 1);
      }

      // Pulsing Alert Badge
      if (n.isAlert) {
        const pulse = Math.sin(timestamp / 160) * 2;
        this.ctx.beginPath();
        this.ctx.arc(n.x + r - 3, n.y - r + 3, 7 + pulse, 0, Math.PI * 2);
        this.ctx.fillStyle = '#f43f5e';
        this.ctx.fill();
        this.ctx.strokeStyle = '#ffffff';
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();

        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = 'bold 9px sans-serif';
        this.ctx.fillText('!', n.x + r - 3, n.y - r + 6);
      }

      // Label Pill
      this.drawNodeLabelPill(n, r, isHovered);

      this.ctx.restore();
    });
  }

  drawNodeLabelPill(n, radius, isHovered) {
    const labelY = n.y + radius + 15;
    this.ctx.font = 'bold 11px "Plus Jakarta Sans", sans-serif';
    const textW = this.ctx.measureText(n.label).width;
    const pillW = textW + 16;
    const pillH = 20;

    this.ctx.fillStyle = this.isDark ? 'rgba(8, 12, 22, 0.95)' : 'rgba(255, 255, 255, 0.96)';
    this.ctx.strokeStyle = isHovered ? n.color : (this.isDark ? 'rgba(56, 189, 248, 0.3)' : 'rgba(0, 0, 0, 0.15)');
    this.ctx.lineWidth = 1;

    this.ctx.beginPath();
    this.roundRect(n.x - pillW / 2, labelY - pillH / 2, pillW, pillH, 5);
    this.ctx.fill();
    this.ctx.stroke();

    this.ctx.fillStyle = this.isDark ? '#f8fafc' : '#0f172a';
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText(n.label, n.x, labelY);

    if (n.sublabel && isHovered) {
      this.ctx.font = '9px "JetBrains Mono", monospace';
      this.ctx.fillStyle = n.color;
      this.ctx.fillText(n.sublabel, n.x, labelY + 14);
    }
  }

  drawHoverHUD() {
    if (!this.hoveredNode || !this.hoveredNode.details) return;

    const n = this.hoveredNode;
    const screenX = n.x * this.scale + this.panX;
    const screenY = n.y * this.scale + this.panY;

    this.ctx.save();
    this.ctx.font = 'bold 12px "Plus Jakarta Sans", sans-serif';

    const titleText = `${n.icon || '📌'} ${n.label} [${(n.type || 'ENTITY').toUpperCase()}]`;
    const bodyText = n.details;

    const maxHUDWidth = 340;
    const lines = this.wrapText(bodyText, maxHUDWidth - 24, '11px "Plus Jakarta Sans", sans-serif');
    const hudHeight = 36 + (lines.length * 16) + 16;
    const hudWidth = maxHUDWidth;

    let boxX = screenX - hudWidth / 2;
    let boxY = screenY - n.radius * this.scale - hudHeight - 12;

    if (boxX < 14) boxX = 14;
    if (boxX + hudWidth > this.width - 14) boxX = this.width - hudWidth - 14;
    if (boxY < 14) boxY = screenY + n.radius * this.scale + 16;

    this.ctx.fillStyle = this.isDark ? 'rgba(8, 12, 22, 0.97)' : 'rgba(255, 255, 255, 0.98)';
    this.ctx.strokeStyle = n.color;
    this.ctx.lineWidth = 1.5;
    this.ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
    this.ctx.shadowBlur = 18;

    this.ctx.beginPath();
    this.roundRect(boxX, boxY, hudWidth, hudHeight, 8);
    this.ctx.fill();
    this.ctx.stroke();
    this.ctx.shadowBlur = 0;

    this.ctx.fillStyle = n.color;
    this.ctx.fillRect(boxX, boxY, hudWidth, 3);

    this.ctx.fillStyle = n.color;
    this.ctx.font = 'bold 12px "JetBrains Mono", monospace';
    this.ctx.textAlign = 'left';
    this.ctx.textBaseline = 'top';
    this.ctx.fillText(titleText, boxX + 12, boxY + 12);

    this.ctx.fillStyle = this.isDark ? '#cbd5e1' : '#334155';
    this.ctx.font = '11px "Plus Jakarta Sans", sans-serif';
    lines.forEach((line, idx) => {
      this.ctx.fillText(line, boxX + 12, boxY + 34 + (idx * 16));
    });

    this.ctx.fillStyle = this.isDark ? '#94a3b8' : '#64748b';
    this.ctx.font = '9.5px "JetBrains Mono", monospace';
    let hint = "Drag to reposition node";
    if (n.type === 'cctv') hint = "Click node to open Surveillance Feed 📹";
    if (n.type === 'case') hint = "Click node to view statutory FIR (Form II) 📑";
    if (n.type === 'missing_evidence') hint = "Click node to inspect Audit Flags ⚠️";
    this.ctx.fillText(`• ${hint}`, boxX + 12, boxY + hudHeight - 14);

    this.ctx.restore();
  }

  wrapText(text, maxWidth, font) {
    this.ctx.font = font;
    const words = text.split(' ');
    const lines = [];
    let currentLine = words[0] || '';

    for (let i = 1; i < words.length; i++) {
      const testLine = currentLine + ' ' + words[i];
      if (this.ctx.measureText(testLine).width < maxWidth) {
        currentLine = testLine;
      } else {
        lines.push(currentLine);
        currentLine = words[i];
      }
    }
    if (currentLine) lines.push(currentLine);
    return lines;
  }

  roundRect(x, y, w, h, r) {
    this.ctx.beginPath();
    this.ctx.moveTo(x + r, y);
    this.ctx.lineTo(x + w - r, y);
    this.ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    this.ctx.lineTo(x + w, y + h - r);
    this.ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    this.ctx.lineTo(x + r, y + h);
    this.ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    this.ctx.lineTo(x, y + r);
    this.ctx.quadraticCurveTo(x, y, x + r, y);
    this.ctx.closePath();
  }

  zoomIn() {
    this.scale = Math.min(2.8, this.scale * 1.25);
    this.draw();
  }

  zoomOut() {
    this.scale = Math.max(0.4, this.scale / 1.25);
    this.draw();
  }

  resetView() {
    this.scale = 1.0;
    this.panX = 0;
    this.panY = 0;
    this.draw();
  }

  togglePhysics() {
    this.physicsRunning = !this.physicsRunning;
    return this.physicsRunning;
  }
}

window.RelationshipGraph = RelationshipGraph;
