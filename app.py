import os
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.db import (
    init_db, get_all_cases, get_case_by_id, save_case, delete_case,
    save_audit_result, get_latest_audit_result, save_human_review, get_human_reviews_for_case
)
from services.audit_engine import AuditEngine
from services.rag_service import rag_service
from services.llm_service import llm_service
from services.translation_service import translation_service
from services.report_generator import report_generator
from services.document_processor import document_processor

app = FastAPI(
    title="AI Investigation Auditor",
    description="AI-Assisted Second-Level Audit for Investigation Records",
    version="2.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Pre-index all existing cases into RAG service
    all_cases = get_all_cases()
    for c_meta in all_cases:
        c_full = get_case_by_id(c_meta["case_id"])
        if c_full and "data" in c_full:
            rag_service.index_case(c_full["data"])

# Static directories
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if os.path.exists(os.path.join(STATIC_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(STATIC_DIR, "css")), name="css")
if os.path.exists(os.path.join(STATIC_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(STATIC_DIR, "js")), name="js")

@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>AI Investigation Auditor API Running</h1><p>Frontend loading...</p>")

# ----------------- CASE ENDPOINTS -----------------

@app.get("/api/cases")
def list_cases():
    cases = get_all_cases()
    return {"status": "success", "count": len(cases), "cases": cases}

@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return {"status": "success", "case": case}

@app.post("/api/cases")
def create_or_update_case(payload: Dict[str, Any]):
    case_id = payload.get("case_id")
    if not case_id or not str(case_id).strip():
        raise HTTPException(status_code=400, detail="Case ID is required")
    
    saved = save_case(payload)
    if saved and "data" in saved:
        rag_service.index_case(saved["data"])
    return {"status": "success", "case": saved}

@app.delete("/api/cases/{case_id}")
def remove_case(case_id: str):
    success = delete_case(case_id)
    return {"status": "success", "deleted": case_id}

# ----------------- AUDIT & RAG ENDPOINTS -----------------

class AuditRequest(BaseModel):
    lang: Optional[str] = "en"

@app.post("/api/cases/{case_id}/audit")
def run_case_audit(case_id: str, req: Optional[AuditRequest] = None):
    case_rec = get_case_by_id(case_id)
    if not case_rec or "data" not in case_rec:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    case_data = case_rec["data"]

    # 1. Index current case records into RAG
    rag_service.index_case(case_data)

    # 2. Run deterministic audit engine
    engine = AuditEngine(case_data)
    audit_res = engine.run_audit()

    # 3. Enhance each detected flag with Case-Isolated RAG retrieval & GenAI reasoning
    enhanced_flags = []
    rag_evidence_map = {}

    for flag in audit_res["flags"]:
        query = f"{flag.get('title', '')} {flag.get('explanation', '')} {' '.join(flag.get('source_records', []))}"
        retrieved_chunks = rag_service.retrieve(case_id, query, top_k=3)
        rag_evidence_map[flag["flag_id"]] = retrieved_chunks

        # LLM reasoning note
        explanation_note = llm_service.generate_explanation(case_id, flag, retrieved_chunks)
        flag_copy = flag.copy()
        flag_copy["llm_assessment"] = explanation_note
        flag_copy["retrieved_sources"] = retrieved_chunks
        enhanced_flags.append(flag_copy)

    # 4. Save result to SQLite
    audit_id = save_audit_result(
        case_id=case_id,
        scores=audit_res["scores"],
        flags=enhanced_flags,
        rag_sources=rag_evidence_map,
        llm_analysis="Audit performed using hybrid deterministic rules + case-isolated RAG retrieval"
    )

    # 5. Fetch existing human reviews
    reviews = get_human_reviews_for_case(case_id)

    # 6. Apply translation if requested
    lang = req.lang if req and req.lang else "en"
    translated_flags = [translation_service.translate_flag(f, lang) for f in enhanced_flags]

    return {
        "status": "success",
        "audit_id": audit_id,
        "case_id": case_id,
        "crime_type": audit_res["crime_type"],
        "scores": audit_res["scores"],
        "flags": translated_flags,
        "rag_evidence": rag_evidence_map,
        "human_reviews": reviews,
        "language": lang,
        "llm_status": llm_service.get_status()
    }

# ----------------- HUMAN REVIEW WORKFLOW -----------------

class ReviewPayload(BaseModel):
    flag_id: str
    status: str # 'Reviewed', 'Needs Further Investigation', 'False Positive'
    reviewer_name: Optional[str] = "Investigator"
    notes: Optional[str] = ""

@app.post("/api/cases/{case_id}/review")
def record_review(case_id: str, review: ReviewPayload):
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    res = save_human_review(
        case_id=case_id,
        flag_id=review.flag_id,
        status=review.status,
        reviewer_name=review.reviewer_name,
        notes=review.notes
    )
    return {"status": "success", "review": res}

@app.get("/api/cases/{case_id}/reviews")
def get_reviews(case_id: str):
    revs = get_human_reviews_for_case(case_id)
    return {"status": "success", "case_id": case_id, "reviews": revs}

# ----------------- REPORT EXPORT -----------------

@app.get("/api/cases/{case_id}/report")
def export_report(case_id: str, format: str = "html"):
    case_rec = get_case_by_id(case_id)
    if not case_rec or "data" not in case_rec:
        raise HTTPException(status_code=404, detail="Case not found")

    latest_audit = get_latest_audit_result(case_id)
    if not latest_audit:
        # Run audit on the fly if not yet executed
        engine = AuditEngine(case_rec["data"])
        latest_audit = engine.run_audit()

    reviews = get_human_reviews_for_case(case_id)

    if format == "markdown":
        md = report_generator.generate_markdown_report(case_rec["data"], latest_audit, reviews)
        return Response(content=md, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename=Audit_Report_{case_id}.md"})

    html = report_generator.generate_html_report(case_rec["data"], latest_audit, reviews)
    return HTMLResponse(content=html)

SAMPLE_DOCS_DIR = os.path.join(os.path.dirname(__file__), "sample_documents")

SAMPLE_FILES_METADATA = [
    {
        "id": "sample-1",
        "filename": "sample_1_forensic_ballistics_report.txt",
        "format": "TXT",
        "badge_class": "badge-txt",
        "title": "SFSL Ballistics & Firearms Analysis",
        "description": "Microscopic striation & firing pin comparison confirming 9mm casing E-001 matches seized pistol E-003, with chain of custody seal.",
        "size": "1.4 KB",
        "category": "Forensic Laboratory Report"
    },
    {
        "id": "sample-2",
        "filename": "sample_2_cctv_surveillance_analysis.json",
        "format": "JSON",
        "badge_class": "badge-json",
        "title": "Traffic CCTV & ANPR Surveillance Log",
        "description": "Automated camera detections, vehicle speed & route tracking (KA-03-HA-9821), and FASTag toll timestamp contradicting suspect alibi.",
        "size": "2.1 KB",
        "category": "Digital Surveillance Record"
    },
    {
        "id": "sample-3",
        "filename": "sample_3_call_detail_records_cdr.csv",
        "format": "CSV",
        "badge_class": "badge-csv",
        "title": "Call Detail Records (CDR) Tower Dump",
        "description": "Multi-cell tower logs mapping suspect mobile device location, call durations, and associate contacts during incident timeline.",
        "size": "1.1 KB",
        "category": "Telecom Intelligence"
    },
    {
        "id": "sample-4",
        "filename": "sample_4_eyewitness_supplementary_statement.txt",
        "format": "TXT",
        "badge_class": "badge-txt",
        "title": "Eyewitness Supplementary Statement (Sec 161 CrPC)",
        "description": "Security supervisor statement correcting timeline from 20:30 to 21:05 hrs based on security desk guard logbook.",
        "size": "1.8 KB",
        "category": "Witness Deposition"
    }
]

def ingest_parsed_document_into_case(case_data: dict, filename: str, parsed: dict):
    doc_type = parsed.get("type")
    if doc_type == "txt":
        raw_text = parsed.get("raw_text", "")
        ext = parsed.get("extracted", {})
        summary_tokens = []
        if ext.get("detected_dates"):
            summary_tokens.append(f"Dates: {', '.join(ext['detected_dates'])}")
        if ext.get("detected_times"):
            summary_tokens.append(f"Times: {', '.join(ext['detected_times'])}")
        if ext.get("detected_evidence_ids"):
            summary_tokens.append(f"Evidence: {', '.join(ext['detected_evidence_ids'])}")
        
        token_str = f" [{'; '.join(summary_tokens)}]" if summary_tokens else ""
        note_entry = f"📄 Ingested Document [{filename}]{token_str}:\n{raw_text}"
        case_data.setdefault("notes", []).append(note_entry)

    elif doc_type == "json":
        data = parsed.get("data", {})
        if isinstance(data, dict):
            if "surveillance_detections" in data:
                existing_cctv_ids = {c.get("cctv_id") for c in case_data.get("cctv", [])}
                for det in data["surveillance_detections"]:
                    cid = det.get("cctv_id", f"CCTV-{len(case_data.get('cctv', []))+1}")
                    if cid not in existing_cctv_ids:
                        case_data.setdefault("cctv", []).append({
                            "cctv_id": cid,
                            "camera_name": det.get("camera_name", "Surveillance Camera"),
                            "timestamp": det.get("timestamp", "N/A"),
                            "date": det.get("date", case_data.get("incident_date", "")),
                            "relevance": "Surveillance Log Enrichment",
                            "description": f"{det.get('observation', '')} (Speed: {det.get('speed_kmh', 'N/A')} km/h, Direction: {det.get('direction', 'N/A')})"
                        })
            if "associated_evidence" in data:
                ev = data["associated_evidence"]
                existing_ev_ids = {e.get("evidence_id") for e in case_data.get("evidence", [])}
                if ev.get("evidence_id") not in existing_ev_ids:
                    case_data.setdefault("evidence", []).append(ev)

            note_entry = f"📊 Ingested JSON Dossier [{filename}]:\n" + json.dumps(data, indent=2)
            case_data.setdefault("notes", []).append(note_entry)
        elif isinstance(data, list):
            note_entry = f"📊 Ingested JSON Records [{filename}] ({len(data)} items):\n" + json.dumps(data, indent=2)
            case_data.setdefault("notes", []).append(note_entry)

    elif doc_type == "csv":
        rows = parsed.get("data", [])
        csv_lines = [f"📋 Ingested CSV/CDR Dataset [{filename}] ({len(rows)} records):"]
        for r in rows:
            csv_lines.append(" | ".join([f"{k}: {v}" for k, v in r.items()]))
        case_data.setdefault("notes", []).append("\n".join(csv_lines))

# ----------------- FILE UPLOADER & SAMPLES -----------------

@app.get("/api/sample-files")
def get_sample_files():
    """Return available pre-configured sample investigation documents for test upload/ingestion."""
    return {"status": "success", "sample_files": SAMPLE_FILES_METADATA}

@app.get("/api/sample-files/{filename}")
def download_sample_file(filename: str):
    """Download a sample investigation document so user can test file upload manually."""
    clean_filename = os.path.basename(filename)
    file_path = os.path.join(SAMPLE_DOCS_DIR, clean_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample file not found")
    return FileResponse(path=file_path, filename=clean_filename, media_type="application/octet-stream")

@app.get("/api/sample-files/{filename}/content")
def get_sample_file_content(filename: str):
    """Retrieve full raw text content of a sample document to display in document viewer modal."""
    clean_filename = os.path.basename(filename)
    file_path = os.path.join(SAMPLE_DOCS_DIR, clean_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample file not found")
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return {"status": "success", "filename": clean_filename, "content": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


@app.post("/api/cases/{case_id}/ingest-sample/{filename}")
def ingest_sample_file(case_id: str, filename: str):
    """Directly ingest a sample document into the current case without requiring manual re-upload."""
    clean_filename = os.path.basename(filename)
    file_path = os.path.join(SAMPLE_DOCS_DIR, clean_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample file not found")

    case_rec = get_case_by_id(case_id)
    if not case_rec:
        raise HTTPException(status_code=404, detail="Case not found")

    with open(file_path, "rb") as f:
        content = f.read()

    parsed = document_processor.parse_uploaded_file(clean_filename, content)
    case_data = case_rec["data"]
    ingest_parsed_document_into_case(case_data, clean_filename, parsed)
    
    save_case(case_data)
    rag_service.index_case(case_data)

    return {"status": "success", "filename": clean_filename, "parsed": parsed}

@app.post("/api/cases/{case_id}/upload-doc")
async def upload_document(case_id: str, file: UploadFile = File(...)):
    content = await file.read()
    parsed = document_processor.parse_uploaded_file(file.filename, content)
    
    case_rec = get_case_by_id(case_id)
    if not case_rec:
        raise HTTPException(status_code=404, detail="Case not found")

    case_data = case_rec["data"]
    ingest_parsed_document_into_case(case_data, file.filename, parsed)

    save_case(case_data)
    rag_service.index_case(case_data)

    return {"status": "success", "filename": file.filename, "parsed": parsed}

# ----------------- UTILITY & TRANSLATION -----------------

@app.get("/api/languages")
def get_languages():
    return {"languages": translation_service.get_supported_languages()}

@app.get("/api/system-status")
def system_status():
    return {
        "system": "AI Investigation Auditor",
        "version": "2.4.0",
        "llm_engine": llm_service.get_status(),
        "rag_engine": "Case-Isolated Cosine Vector Retrieval (Active)",
        "database": "SQLite Local Store (Active)",
        "ethical_restrictions": "Guilt/Innocence prediction disabled by design. Investigation audit layer active."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
