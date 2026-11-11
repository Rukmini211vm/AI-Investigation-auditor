# DATA SOURCES & ETHICAL SAFETY SPECIFICATION

## AI Investigation Auditor
**AI-Assisted Second-Level Audit for Investigation Records**

---

### 1. Overview & Public Reference Sources
To ensure legal safety, privacy compliance, and investigative realism, this application relies on structural patterns derived from open public repositories rather than confidential police records.

| Source Name | Platform / Organization | Reference URL | Information Referenced | Usage in Project |
| :--- | :--- | :--- | :--- | :--- |
| **NCRB Crime in India Open Data** | National Crime Records Bureau / data.gov.in | https://www.data.gov.in/ | IPC/BNS crime classification schemas, FIR metadata attributes (Date, Time, Location, Complainant, Offense Sections) | **Structural Reference Only** (no PII or actual FIRs used) |
| **Kaggle Indian Police & Crime Datasets** | Open Community Contributors (Kaggle) | https://www.kaggle.com/datasets | Case lifecycle schemas, property seizure registers, witness declaration fields | **Structural Reference Only** |
| **Model Police Seizure & Chain of Custody Protocols** | UNODC / Interpol Forensic Guidelines | https://www.unodc.org/ | Chain of custody transition steps: Seizure -> Recovery -> Seal -> Transfer -> Forensic Storage -> Analysis | **Validation Rule Benchmarks** |

---

### 2. Distinction: Public Structural Data vs Synthetic Investigation Records

#### Why Real Police Case Files Are NOT Used:
1. **Privacy & Legal Safety:** Active and closed criminal records contain personal identifiers (PII), victim identities, confidential informant details, and sensitive forensic materials.
2. **Controlled Evaluation:** Real police records may contain unverified real-world ambiguity. In order to rigorously benchmark and validate the **AI Investigation Auditor**, cases must contain controlled, reproducible conditions (deliberate timeline conflicts, missing chain of custody steps, and uncataloged evidence IDs).

#### Synthetic Dataset Generation Protocol:
All case files, witness statements, CCTV logs, evidence tags, and investigation diary entries in this application are **100% FICTIONAL and SYNTHETICALLY GENERATED**. Any resemblance to real persons, alive or deceased, or actual investigation cases is entirely coincidental.

---

### 3. Case Structure Schema
Every synthetic case adheres to a strict relational schema:
- **Case ID** (e.g., `CASE-001`, `CASE-002`)
- **Crime Type** (Murder, Robbery, Kidnapping / Abduction, Cybercrime, Theft, Assault, etc.)
- **FIR Document**: Case summary, incident date, reported time, incident location, complainant, suspect references.
- **Witness Statements**: Witness IDs, interview timestamps, observed timelines, person descriptors.
- **CCTV & Digital Evidence**: Device ID, camera location, precise hardware timestamp, description.
- **Physical & Forensic Evidence**: Evidence ID (`E-101`, `E-102`), recovery location, recovery timestamp, type, forensic status.
- **Investigation Timeline**: Sequential event log (`EVT-001`, etc.) with action, officer, and linked evidence.
- **Chain of Custody Register**: Custody transitions (`COLLECTED`, `SEALED`, `TRANSFERRED`, `STORED`, `EXAMINED`) with responsible handlers and verification timestamps.
- **Investigation Diary Notes**: Follow-up leads, detective notes, and unresolved inquiries.

---

### 4. Ethical & Legal Limitations
- **Investigation Support Only:** The system is an audit and cross-referencing tool for investigators.
- **No Guilt / Innocence Determination:** The system never labels a suspect as guilty or innocent.
- **Neutral Audit Terminology:** Outputs use strictly objective language:
  - *"Potential timeline inconsistency detected"*
  - *"Evidence association requires human review"*
  - *"Chain of custody documentation gap"*
  - *"Records appear consistent based on available data"*
- **Human Authority:** The system provides second-level checks; final investigative decisions always belong to authorized human officers.
