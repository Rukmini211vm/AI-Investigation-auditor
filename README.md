# AI Investigation Auditor
### AI-Assisted Second-Level Audit for Investigation Records
> *"Connect the records. Detect the gaps. Support human review."*

---

## 1. Project Purpose
Criminal investigations involve numerous interconnected documents—FIRs, Section 161 witness statements, CCTV logs, evidence recovery memos, timelines, and chain-of-custody ledgers. The **AI Investigation Auditor** acts as an automated **second checker** layer for investigation dockets. It cross-references multi-source documents to detect internal contradictions, timeline conflicts, missing evidence links, and incomplete documentation.

---

## 2. Problem Statement
The challenge in major investigations is rarely that investigators do not know which documents belong to a case. Rather, a single docket contains dozens of interconnected records where:
- Timestamps between witness statements and CCTV logs diverge by 30+ minutes.
- Evidence tokens (e.g. `E-104`) are referenced in witness testimony but never logged in property seizure registers.
- Chain of custody transitions lack intermediate transfer or sealing timestamps.
- Key witnesses named in the initial complaint lack recorded statements.

Overlooking these discrepancies before trial compromises investigative integrity and chain of custody admissibility.

---

## 3. Proposed Solution & Key Differentiation
### Dedicated Investigation Audit Layer
Existing AI investigative tools focus on searching, facial recognition, or crime analytics. 
Our differentiation is a **dedicated investigation audit layer**:
- Audits the records themselves for consistency and completeness.
- **NEVER predicts guilt or innocence.**
- **NEVER accuses individuals of committing crimes.**
- Explains **WHY** an issue was flagged and presents exact source citations.
- Empowers the authorized human investigator with final review and decision-making authority.

---

## 4. Key Features
- **Deterministic & RAG-Assisted Audit Engine:** Rule-based cross-checking for zero false negatives on timeline and inventory checks, enhanced with TF-IDF vector retrieval.
- **Dynamic Real-Time Interactivity:** Edit any timestamp or statement in the workspace and click *Run AI Audit*—the system immediately recalculates findings!
- **Investigation Record Consistency Score:** Objective audit metrics (Consistency %, Completeness %, Evidence Linking %, Custody Tracking %).
- **Interactive Chronological Timeline Visualizer:** Plots events sequentially with red warning callouts for conflict windows.
- **Interactive Evidence Relationship Graph:** Canvas network map highlighting active evidence, witnesses, and ghost/missing evidence nodes.
- **Human Review Workflow:** Mark flags as *Reviewed*, *Needs Further Investigation*, or *False Positive* with officer notes stored in SQLite.
- **Multi-Language Support:** Instant switching between English, Kannada, Hindi, Tamil, Telugu, Malayalam, Bengali, Marathi, Spanish, and French while preserving legal entity tokens.
- **Formal Audit Report Export:** Downloadable HTML report with print-to-PDF formatting and Markdown export.
- **10+ Preloaded Synthetic Cases:** Covering Murder, Robbery, Kidnapping, Theft, Cybercrime, Assault, and Fraud.

---

## 5. Technology Stack
- **Backend:** Python 3.12, FastAPI, Uvicorn, SQLite3, Pydantic
- **AI & RAG:** Scikit-Learn (TF-IDF Vector Embeddings & Cosine Similarity), Hybrid Offline GenAI Reasoning Engine (with optional OpenAI/Gemini API integration)
- **Frontend:** Vanilla HTML5, Modern CSS3 (Dark Slate Glassmorphism), Interactive Canvas Graph, Dynamic Timeline Visualizer
- **Reporting:** HTML5 Print Engine, ReportLab, Markdown

---

## 6. Installation & Quick Start

### Prerequisites
- Python 3.10+ (Python 3.12 verified)

### 1. Clone & Navigate to Project Directory
```bash
cd "c:\Users\rukmi\OneDrive\Documents\project 5"
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python app.py
```
*Alternatively:*
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Open in Browser
Navigate to:
```
http://127.0.0.1:8000
```

---

## 7. How to Configure an LLM API (Optional)
The application functions **100% offline without requiring any API keys** using its built-in deterministic audit engine and local reasoning module.

To enable remote LLM generation (e.g. OpenAI or Gemini):
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"
# or
$env:GEMINI_API_KEY="your-api-key-here"

python app.py
```
*Note: Strict ethical system prompts prevent the LLM from determining guilt or generating speculative accusations.*

---

## 8. How RAG Works
1. **Document Ingestion:** Case files (FIR, statements, CCTV, evidence tokens, timelines) are segmented into structured chunks.
2. **Vector Indexing:** Vector representations are computed using TF-IDF n-gram vectorization.
3. **Case Isolation:** Queries only search within the active `case_id` matrix, preventing cross-case contamination.
4. **Relevance Retrieval:** When a contradiction or gap is audited, the engine retrieves top-k matching document excerpts with cosine similarity scores displayed directly in the UI.

---

## 9. Dataset Structure & Demo Cases
All records are stored under `data/synthetic_cases.json` and individual case folders in `data/cases/`.

| Case ID | Crime Classification | Deliberate Test Condition |
| :--- | :--- | :--- |
| **CASE-001** | Murder | **Timeline Conflict:** Witness Neha claims departure at 21:10; Stairwell CCTV logs exit at 20:40 (30-min discrepancy). |
| **CASE-002** | Murder | **Missing Evidence Reference:** Witness mentions Evidence E-104 (crowbar/glove) recovered at canal, but E-104 is missing from seizure register. |
| **CASE-003** | Murder | **Consistent Baseline:** Ballistics, gate CCTV, witness statements, and timeline corroborate cleanly. |
| **CASE-004** | Robbery | **Chain of Custody Gap:** Cash bundle E-401 seized at 14:45 deposited at 19:30 with no sealing log or transit courier signature. |
| **CASE-005** | Kidnapping | **Geospatial Plausibility:** CCTV confirms subject at Mall at 17:25; witness claims abduction 22 km away at 17:30 (5-minute delta). |
| **CASE-006** | Cybercrime | **Incomplete Record:** FIR names key auditor Mr. Raghav Kulkarni, but no witness statement is recorded in the docket. |
| **CASE-007** | Theft | **Direct Contradiction:** CCTV records shutter breach at 03:15 AM; security guard claims he was at entrance at 03:15 AM and found it intact. |
| **CASE-008** | Assault | **Unresolved Association:** Iron rod E-802 found in dumpster 400m away with no forensic or witness linkage to scene. |
| **CASE-009** | Extortion | **Verified Consistent:** Threat audio, CDR logs, and witness statements fully corroborated. |
| **CASE-010** | Bank Heist | **Timeline Gap:** Unexplained 45-minute delay between seismic alarm alert (02:15) and patrol vehicle dispatch (03:00). |

---

## 10. Verification of Dynamic User Input
The application is fully dynamic:
1. Open **CASE-001** in the **Case Workspace**.
2. Notice the initial Critical Flag: *Timeline Conflict between WS-001 (21:10) and CCTV-001 (20:40)*.
3. In the CCTV editor, change `20:40` to `21:10`.
4. Click **[ RUN AI INVESTIGATION AUDIT ]**.
5. The timeline conflict is immediately resolved, the red flag disappears, and the Consistency Score jumps to 100%!

---

## 11. Safety & Legal Ethics Statement
- **Academic / Hackathon Prototype:** Uses 100% synthetic/fictional records.
- **Non-Accusatory:** The system identifies discrepancies in records, not criminal guilt.
- **Human Authority:** Second-level assistive technology; final investigative authority rests exclusively with authorized human law enforcement and judiciary officers.
