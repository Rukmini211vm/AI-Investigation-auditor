import os
import json
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Load synthetic cases
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_path = os.path.join(base_dir, "data", "synthetic_cases.json")
with open(json_path, "r", encoding="utf-8") as f:
    cases = json.load(f)

# Output paths
output_xlsx = os.path.join(base_dir, "AI_Investigation_Auditor_Datasets.xlsx")
data_xlsx = os.path.join(base_dir, "data", "AI_Investigation_Auditor_Datasets.xlsx")

# 1. Dataset Overview
overview_rows = []
for c in cases:
    overview_rows.append({
        "Case ID": c.get("case_id"),
        "Case Title": c.get("title"),
        "Crime Type": c.get("crime_type"),
        "Incident Date": c.get("incident_date"),
        "Incident Time": c.get("incident_time"),
        "Location": c.get("location"),
        "Victim": c.get("victim"),
        "Suspects Count": len(c.get("suspects", [])),
        "Witnesses Count": len(c.get("witnesses", [])),
        "CCTV Logs Count": len(c.get("cctv", [])),
        "Evidence Items Count": len(c.get("evidence", [])),
        "Custody Records Count": len(c.get("chain_of_custody", [])),
        "Injected Audit Flags": len(c.get("intentional_flags", []))
    })
df_overview = pd.DataFrame(overview_rows)

# 2. Cases Master
cases_master_rows = []
for c in cases:
    fir = c.get("fir", {})
    cases_master_rows.append({
        "Case ID": c.get("case_id"),
        "Case Title": c.get("title"),
        "Crime Type": c.get("crime_type"),
        "Incident Date": c.get("incident_date"),
        "Incident Time": c.get("incident_time"),
        "Location": c.get("location"),
        "Victim": c.get("victim"),
        "Suspects": ", ".join(c.get("suspects", [])),
        "FIR Number": fir.get("fir_number", ""),
        "Police Station": fir.get("ps", ""),
        "Penal Sections": fir.get("sections", ""),
        "Investigation Summary": c.get("summary", "")
    })
df_cases_master = pd.DataFrame(cases_master_rows)

# 3. FIR Registry
fir_rows = []
for c in cases:
    fir = c.get("fir", {})
    fir_rows.append({
        "Case ID": c.get("case_id"),
        "FIR Number": fir.get("fir_number", ""),
        "Police Station": fir.get("ps", ""),
        "Date Registered": fir.get("date", ""),
        "Time Registered": fir.get("time", ""),
        "Complainant": fir.get("complainant", "Duty Sub-Inspector"),
        "Penal Code Sections": fir.get("sections", ""),
        "FIR Complaint Details": fir.get("details", "")
    })
df_firs = pd.DataFrame(fir_rows)

# 4. Witnesses
witness_rows = []
for c in cases:
    for w in c.get("witnesses", []):
        witness_rows.append({
            "Case ID": c.get("case_id"),
            "Witness ID": w.get("witness_id"),
            "Witness Name": w.get("name"),
            "Statement Date": w.get("statement_date"),
            "Observed Time": w.get("claimed_time"),
            "Observation Location": w.get("location"),
            "Recorded Deposition": w.get("statement")
        })
df_witnesses = pd.DataFrame(witness_rows)

# 5. CCTV Surveillance Logs
cctv_rows = []
for c in cases:
    for cam in c.get("cctv", []):
        cctv_rows.append({
            "Case ID": c.get("case_id"),
            "CCTV ID": cam.get("cctv_id"),
            "Camera Name / Location": cam.get("camera_name"),
            "Recording Date": cam.get("date"),
            "Hardware Timestamp": cam.get("timestamp"),
            "Relevance Category": cam.get("relevance", "Surveillance Feed"),
            "Surveillance Observation Log": cam.get("description")
        })
df_cctv = pd.DataFrame(cctv_rows)

# 6. Physical & Forensic Evidence Inventory
evidence_rows = []
for c in cases:
    for ev in c.get("evidence", []):
        evidence_rows.append({
            "Case ID": c.get("case_id"),
            "Evidence Token ID": ev.get("evidence_id"),
            "Evidence Category": ev.get("type"),
            "Recovery Date": ev.get("recovery_date"),
            "Recovery Time": ev.get("recovery_time"),
            "Recovery Location": ev.get("recovery_location"),
            "Seizing Officer": ev.get("officer"),
            "Seizure Specification": ev.get("description")
        })
df_evidence = pd.DataFrame(evidence_rows)

# 7. Chain of Custody Ledger
custody_rows = []
for c in cases:
    for coc in c.get("chain_of_custody", []):
        custody_rows.append({
            "Case ID": c.get("case_id"),
            "Evidence Token ID": coc.get("evidence_id"),
            "Initial Collector": coc.get("collected_by"),
            "Collection Timestamp": coc.get("collected_time"),
            "Tamper-Evident Seal Timestamp": coc.get("sealed_time"),
            "Custody Transferred To": coc.get("transferred_to"),
            "Transfer Timestamp": coc.get("transfer_time"),
            "Forensic Storage Facility": coc.get("stored_location"),
            "Registry Verification Status": coc.get("status")
        })
df_custody = pd.DataFrame(custody_rows)

# 8. Investigation Chronology
timeline_rows = []
for c in cases:
    for t in c.get("timeline", []):
        timeline_rows.append({
            "Case ID": c.get("case_id"),
            "Event ID": t.get("event_id"),
            "Date": t.get("date"),
            "Time": t.get("time"),
            "Source / Informant": t.get("source"),
            "Event Narrative": t.get("description")
        })
df_timeline = pd.DataFrame(timeline_rows)

# 9. Ground Truth Injected Discrepancies
flags_rows = []
for c in cases:
    for f in c.get("intentional_flags", []):
        if isinstance(f, dict):
            cat = f.get("type", "Audit Discrepancy")
            sev = f.get("severity", "Warning").upper()
            desc = f.get("description", str(f))
        else:
            f_str = str(f)
            parts = f_str.split(":", 1)
            cat = parts[0].strip() if len(parts) > 1 else "Audit Discrepancy"
            desc = parts[1].strip() if len(parts) > 1 else f_str
            sev = "CRITICAL" if any(k in f_str.lower() for k in ["conflict", "contradict", "murder", "weapon"]) else "WARNING"
        flags_rows.append({
            "Case ID": c.get("case_id"),
            "Discrepancy Category": cat,
            "Ground Truth Severity": sev,
            "Investigative Inconsistency Specification": desc
        })
df_flags = pd.DataFrame(flags_rows)

# 10. CDR Call Detail Records Sample
cdr_csv_path = os.path.join(base_dir, "sample_documents", "sample_3_call_detail_records_cdr.csv")
if os.path.exists(cdr_csv_path):
    df_cdr = pd.read_csv(cdr_csv_path)
else:
    df_cdr = pd.DataFrame()

# Write to Excel
writer = pd.ExcelWriter(output_xlsx, engine='openpyxl')

sheets = {
    "1_Overview": df_overview,
    "2_Cases_Master": df_cases_master,
    "3_FIR_Registry": df_firs,
    "4_Witness_Statements": df_witnesses,
    "5_CCTV_Surveillance": df_cctv,
    "6_Physical_Evidence": df_evidence,
    "7_Chain_Of_Custody": df_custody,
    "8_Investigation_Timeline": df_timeline,
    "9_Ground_Truth_Flags": df_flags
}

if not df_cdr.empty:
    sheets["10_CDR_Telecom_Dump"] = df_cdr

for sheet_name, df_sheet in sheets.items():
    df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

writer.close()

# Style Excel Workbook with OpenPyXL
import openpyxl
wb = openpyxl.load_workbook(output_xlsx)

header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Dark Navy Blue
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)
stripe_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

for ws in wb.worksheets:
    ws.views.sheetView[0].showGridLines = True
    # Header styling
    for col_idx in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 28
    
    # Data row styling & column auto-width
    for row_idx in range(2, ws.max_row + 1):
        ws.row_dimensions[row_idx].height = 20
        is_even = (row_idx % 2 == 0)
        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = thin_border
            cell.font = Font(name="Calibri", size=10)
            if is_even:
                cell.fill = stripe_fill
            if cell.value and isinstance(cell.value, (int, float)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Column width adjustment
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)

wb.save(output_xlsx)
# Also copy to data folder
wb.save(data_xlsx)

print(f"Successfully generated Master Excel Dataset Workbook at:\n{output_xlsx}")
