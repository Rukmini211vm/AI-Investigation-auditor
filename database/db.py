import os
import sqlite3
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "investigation_auditor.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        crime_type TEXT NOT NULL,
        incident_date TEXT,
        incident_time TEXT,
        location TEXT,
        victim TEXT,
        suspects_json TEXT,
        summary TEXT,
        data_json TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # Audit results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        audit_timestamp TEXT NOT NULL,
        consistency_score INTEGER,
        completeness_score INTEGER,
        linking_score INTEGER,
        custody_score INTEGER,
        overall_score INTEGER,
        flags_json TEXT NOT NULL,
        rag_sources_json TEXT,
        llm_analysis TEXT,
        FOREIGN KEY (case_id) REFERENCES cases (case_id)
    )
    """)

    # Human reviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS human_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        flag_id TEXT NOT NULL,
        status TEXT NOT NULL, -- 'Pending', 'Reviewed', 'Needs Further Investigation', 'False Positive'
        reviewer_name TEXT,
        notes TEXT,
        updated_at TEXT NOT NULL,
        UNIQUE(case_id, flag_id)
    )
    """)

    conn.commit()
    conn.close()

    # Seed cases from synthetic_cases.json if empty
    seed_if_needed()

def seed_if_needed():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM cases")
    count = cursor.fetchone()["count"]
    if count == 0:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic_cases.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                cases = json.load(f)
            now = datetime.now().isoformat()
            for c in cases:
                cursor.execute("""
                INSERT OR REPLACE INTO cases (
                    case_id, title, crime_type, incident_date, incident_time,
                    location, victim, suspects_json, summary, data_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c["case_id"],
                    c.get("title", f"Investigation {c['case_id']}"),
                    c.get("crime_type", "Other"),
                    c.get("incident_date", ""),
                    c.get("incident_time", ""),
                    c.get("location", ""),
                    c.get("victim", ""),
                    json.dumps(c.get("suspects", [])),
                    c.get("summary", ""),
                    json.dumps(c),
                    now,
                    now
                ))
            conn.commit()
            print(f"Seeded {len(cases)} cases into database.")
    conn.close()

def get_all_cases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT case_id, title, crime_type, incident_date, incident_time, location, victim, summary, updated_at FROM cases ORDER BY case_id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_case_by_id(case_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    res["data"] = json.loads(res["data_json"])
    res["suspects"] = json.loads(res["suspects_json"]) if res.get("suspects_json") else []
    return res

def save_case(case_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    case_id = case_data.get("case_id")
    now = datetime.now().isoformat()
    cursor.execute("""
    INSERT OR REPLACE INTO cases (
        case_id, title, crime_type, incident_date, incident_time,
        location, victim, suspects_json, summary, data_json,
        created_at, updated_at
    ) VALUES (
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        COALESCE((SELECT created_at FROM cases WHERE case_id = ?), ?), ?
    )
    """, (
        case_id,
        case_data.get("title", f"Investigation {case_id}"),
        case_data.get("crime_type", "Murder"),
        case_data.get("incident_date", ""),
        case_data.get("incident_time", ""),
        case_data.get("location", ""),
        case_data.get("victim", ""),
        json.dumps(case_data.get("suspects", [])),
        case_data.get("summary", ""),
        json.dumps(case_data),
        case_id,
        now,
        now
    ))
    conn.commit()
    conn.close()
    return get_case_by_id(case_id)

def delete_case(case_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
    cursor.execute("DELETE FROM audit_results WHERE case_id = ?", (case_id,))
    cursor.execute("DELETE FROM human_reviews WHERE case_id = ?", (case_id,))
    conn.commit()
    conn.close()
    return True

def save_audit_result(case_id: str, scores: dict, flags: list, rag_sources: list, llm_analysis: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO audit_results (
        case_id, audit_timestamp, consistency_score, completeness_score,
        linking_score, custody_score, overall_score, flags_json, rag_sources_json, llm_analysis
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        now,
        scores.get("consistency", 100),
        scores.get("completeness", 100),
        scores.get("linking", 100),
        scores.get("custody", 100),
        scores.get("overall", 100),
        json.dumps(flags),
        json.dumps(rag_sources),
        llm_analysis
    ))
    conn.commit()
    audit_id = cursor.lastrowid
    conn.close()
    return audit_id

def get_latest_audit_result(case_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM audit_results WHERE case_id = ? ORDER BY id DESC LIMIT 1
    """, (case_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    res["flags"] = json.loads(res["flags_json"])
    res["rag_sources"] = json.loads(res["rag_sources_json"]) if res.get("rag_sources_json") else []
    return res

def save_human_review(case_id: str, flag_id: str, status: str, reviewer_name: str, notes: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
    INSERT OR REPLACE INTO human_reviews (
        case_id, flag_id, status, reviewer_name, notes, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        case_id, flag_id, status, reviewer_name, notes, now
    ))
    conn.commit()
    conn.close()
    return {"status": "saved", "flag_id": flag_id, "updated_at": now}

def get_human_reviews_for_case(case_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM human_reviews WHERE case_id = ?", (case_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {r["flag_id"]: r for r in rows}
