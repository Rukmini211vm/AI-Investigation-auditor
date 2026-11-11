import os
import json
from datetime import datetime
from typing import Dict, Any, List

class ReportGenerator:
    """
    Generates formal, printable investigation audit reports in HTML, Markdown, and text formats.
    """

    @staticmethod
    def generate_html_report(case_data: Dict[str, Any], audit_result: Dict[str, Any], reviews: Dict[str, Any]) -> str:
        case_id = case_data.get("case_id", "UNKNOWN")
        title = case_data.get("title", f"Investigation {case_id}")
        crime_type = case_data.get("crime_type", "Other")
        date_str = case_data.get("incident_date", "")
        time_str = case_data.get("incident_time", "")
        location = case_data.get("location", "")
        victim = case_data.get("victim", "")
        suspects = ", ".join(case_data.get("suspects", [])) or "None Listed"

        scores = audit_result.get("scores", {})
        flags = audit_result.get("flags", [])
        timestamp = audit_result.get("audit_timestamp", datetime.now().isoformat())

        # Generate flag table rows
        flag_rows = ""
        for idx, f in enumerate(flags, start=1):
            fid = f.get("flag_id", "")
            rev = reviews.get(fid, {})
            rev_status = rev.get("status", "Pending Review")
            rev_notes = rev.get("notes", "No officer notes recorded.")
            badge_color = "#ef4444" if f.get("severity") == "CRITICAL" else ("#f59e0b" if f.get("severity") == "WARNING" else "#3b82f6")

            flag_rows += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 12px; font-weight: 600;">#{idx}</td>
                <td style="padding: 12px;">
                    <span style="background: {badge_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">
                        {f.get('severity', 'FLAG')}
                    </span>
                    <div style="font-weight: 600; margin-top: 4px; color: #1e293b;">{f.get('title', '')}</div>
                    <div style="font-size: 13px; color: #475569; margin-top: 4px;">{f.get('explanation', '')}</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                        <strong>Source Records:</strong> {', '.join(f.get('source_records', []))}
                    </div>
                </td>
                <td style="padding: 12px; font-size: 12px;">
                    <div style="font-weight: 600; color: #0f172a;">Status: {rev_status}</div>
                    <div style="font-style: italic; color: #475569; margin-top: 4px;">Note: {rev_notes}</div>
                </td>
            </tr>
            """

        if not flags:
            flag_rows = """
            <tr>
                <td colspan="3" style="padding: 24px; text-align: center; color: #059669; font-weight: 600;">
                    ✓ Zero active inconsistencies detected. Investigation records corroborate within tolerance parameters.
                </td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Investigation Record Audit Report - {case_id}</title>
    <style>
        @page {{ size: A4; margin: 20mm; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #0f172a; line-height: 1.5; margin: 0; padding: 20px; background: #fff; }}
        .header {{ border-bottom: 3px solid #1e293b; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .title {{ font-size: 24px; font-weight: 800; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px; }}
        .subtitle {{ font-size: 13px; color: #475569; font-weight: 500; margin-top: 4px; }}
        .meta-box {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin-bottom: 25px; }}
        .meta-item {{ font-size: 13px; }}
        .meta-label {{ font-weight: 700; color: #475569; text-transform: uppercase; font-size: 11px; }}
        .meta-val {{ color: #0f172a; font-weight: 600; font-size: 14px; margin-top: 2px; }}
        .scores-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 25px; }}
        .score-card {{ background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; text-align: center; }}
        .score-num {{ font-size: 26px; font-weight: 800; color: #1e293b; }}
        .score-label {{ font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 13px; }}
        th {{ background: #f1f5f9; padding: 10px 12px; text-align: left; font-size: 11px; text-transform: uppercase; font-weight: 700; color: #475569; border-bottom: 2px solid #cbd5e1; }}
        .disclaimer {{ background: #eff6ff; border-left: 4px solid #3b82f6; padding: 14px; font-size: 12px; color: #1e3a8a; border-radius: 0 6px 6px 0; margin-top: 30px; }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 20px; text-align: right;">
        <button onclick="window.print()" style="background: #2563eb; color: #fff; padding: 8px 18px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer;">
            🖨️ Print / Save as PDF
        </button>
    </div>

    <div class="header">
        <div>
            <div class="title">Investigation Record Audit Report</div>
            <div class="subtitle">AI-Assisted Second-Level Audit for Investigation Records</div>
        </div>
        <div style="text-align: right; font-size: 12px; color: #64748b;">
            <div><strong>Audit Reference:</strong> AUD-{case_id}</div>
            <div><strong>Timestamp:</strong> {timestamp}</div>
        </div>
    </div>

    <div class="meta-box">
        <div class="meta-item"><div class="meta-label">Case Identifier</div><div class="meta-val">{case_id}</div></div>
        <div class="meta-item"><div class="meta-label">Crime Classification</div><div class="meta-val">{crime_type}</div></div>
        <div class="meta-item"><div class="meta-label">Incident Title</div><div class="meta-val">{title}</div></div>
        <div class="meta-item"><div class="meta-label">Incident Date & Time</div><div class="meta-val">{date_str} at {time_str} hrs</div></div>
        <div class="meta-item"><div class="meta-label">Incident Location</div><div class="meta-val">{location}</div></div>
        <div class="meta-item"><div class="meta-label">Victim / Complainant</div><div class="meta-val">{victim}</div></div>
        <div class="meta-item"><div class="meta-label">Persons Mentioned / Suspects</div><div class="meta-val">{suspects}</div></div>
        <div class="meta-item"><div class="meta-label">Documents Audited</div><div class="meta-val">FIR, {len(case_data.get('witnesses', []))} Witness Statements, {len(case_data.get('cctv', []))} CCTV Logs, {len(case_data.get('evidence', []))} Evidence Tags, {len(case_data.get('chain_of_custody', []))} Custody Records</div></div>
    </div>

    <div style="font-size: 14px; font-weight: 700; text-transform: uppercase; color: #334155; margin-bottom: 10px;">Record-Level Audit Metrics (Non-Legal Quality Score)</div>
    <div class="scores-grid">
        <div class="score-card"><div class="score-num">{scores.get('consistency', 100)}%</div><div class="score-label">Timeline & Statement Consistency</div></div>
        <div class="score-card"><div class="score-num">{scores.get('completeness', 100)}%</div><div class="score-label">Record Completeness</div></div>
        <div class="score-card"><div class="score-num">{scores.get('linking', 100)}%</div><div class="score-label">Evidence Cross-Linking</div></div>
        <div class="score-card"><div class="score-num">{scores.get('custody', 100)}%</div><div class="score-label">Chain of Custody Tracking</div></div>
    </div>

    <div style="font-size: 14px; font-weight: 700; text-transform: uppercase; color: #334155; margin-bottom: 10px;">Detected Audit Flags & Second-Level Review Items</div>
    <table>
        <thead>
            <tr>
                <th style="width: 50px;">Item</th>
                <th>Audit Finding & Source Record Citations</th>
                <th style="width: 220px;">Human Review Status & Notes</th>
            </tr>
        </thead>
        <tbody>
            {flag_rows}
        </tbody>
    </table>

    <div class="disclaimer">
        <strong>LEGAL AND ETHICAL AUDIT MANDATE:</strong><br>
        This report is generated by the AI Investigation Auditor as an automated second-level record auditing assistant.
        It identifies record-level discrepancies, timeline gaps, and missing document linkages for review.
        <strong>This tool DOES NOT determine innocence or guilt, does not accuse suspects, and does not replace the judgment of sworn investigating officers.</strong>
        Final investigative conclusions belong solely to authorized law enforcement officers and judicial authorities.
    </div>

    <div style="margin-top: 40px; display: flex; justify-content: space-between; font-size: 12px; color: #475569; border-top: 1px dashed #cbd5e1; padding-top: 15px;">
        <div>Audited By: AI Investigation Auditor System v2.4 (Deterministic + RAG Engine)</div>
        <div>Authorized Officer Review Signature: ___________________________</div>
    </div>
</body>
</html>"""
        return html

    @staticmethod
    def generate_markdown_report(case_data: Dict[str, Any], audit_result: Dict[str, Any], reviews: Dict[str, Any]) -> str:
        case_id = case_data.get("case_id", "UNKNOWN")
        scores = audit_result.get("scores", {})
        flags = audit_result.get("flags", [])

        md = f"""# INVESTIGATION RECORD AUDIT REPORT
**System:** AI Investigation Auditor  
**Case ID:** {case_id}  
**Crime Classification:** {case_data.get('crime_type')}  
**Title:** {case_data.get('title')}  
**Incident Date/Time:** {case_data.get('incident_date')} at {case_data.get('incident_time')}  
**Location:** {case_data.get('location')}  

---

### Record Consistency Scores (Prototype Audit Metrics - Not Legal Conclusions)
- **Timeline & Statement Consistency:** {scores.get('consistency', 100)}%
- **Record Completeness:** {scores.get('completeness', 100)}%
- **Evidence Cross-Linking:** {scores.get('linking', 100)}%
- **Chain of Custody Tracking:** {scores.get('custody', 100)}%
- **Overall Audit Quality:** {scores.get('overall', 100)}%

---

### Detected Audit Flags ({len(flags)} Items)
"""
        for idx, f in enumerate(flags, start=1):
            fid = f.get("flag_id", "")
            rev = reviews.get(fid, {})
            md += f"""
#### [{f.get('severity')}] #{idx} {f.get('title')}
- **Category:** {f.get('category')}
- **Explanation:** {f.get('explanation')}
- **Source Documents:** {', '.join(f.get('source_records', []))}
- **Timestamps:** {', '.join(f.get('timestamps', []))}
- **Suggested Action:** {f.get('suggested_action', 'Review records')}
- **Human Review Decision:** {rev.get('status', 'Pending')}
- **Investigator Note:** {rev.get('notes', 'None recorded')}
"""

        md += """
---
**ETHICAL LIMITATION:**
*AI-generated audit assistance. Human review required. The system never decides guilt or innocence.*
"""
        return md

report_generator = ReportGenerator()
