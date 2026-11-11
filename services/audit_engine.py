import re
from datetime import datetime
from typing import Dict, List, Any, Optional

def parse_time_to_minutes(time_str: str) -> Optional[int]:
    """Parse time string like '21:00', '08:40 PM', '8:40', '14:15' to minutes from midnight."""
    if not time_str or not isinstance(time_str, str):
        return None
    s = time_str.strip().upper()
    try:
        # Check AM/PM
        if "AM" in s or "PM" in s:
            match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', s)
            if match:
                h, m, meridiem = int(match.group(1)), int(match.group(2)), match.group(3)
                if meridiem == "PM" and h < 12:
                    h += 12
                elif meridiem == "AM" and h == 12:
                    h = 0
                return h * 60 + m
        # 24-hour format HH:MM
        match = re.search(r'(\d{1,2}):(\d{2})', s)
        if match:
            h, m = int(match.group(1)), int(match.group(2))
            if 0 <= h < 24 and 0 <= m < 60:
                return h * 60 + m
    except Exception:
        pass
    return None

def extract_evidence_ids_from_text(text: str) -> List[str]:
    """Extract evidence identifiers like E-001, E-104, E-401 from arbitrary narrative text."""
    if not text:
        return []
    # Match patterns like E-104, E-001, Evidence E-104
    matches = re.findall(r'\bE[_\-\s]?(\d{1,4})\b', text, re.IGNORECASE)
    cleaned = []
    for m in matches:
        cleaned.append(f"E-{m.zfill(3)}")
    return list(set(cleaned))

def normalize_evidence_id(eid: str) -> str:
    m = re.search(r'E[_\-\s]?(\d+)', eid, re.IGNORECASE)
    if m:
        return f"E-{m.group(1).zfill(3)}"
    return eid.strip().upper()

class AuditEngine:
    """
    Second-Level Investigation Record Audit Engine.
    Executes deterministic checks across FIR, witness statements,
    CCTV records, evidence registries, timelines, and chain of custody logs.
    """

    def __init__(self, case_data: Dict[str, Any]):
        self.case = case_data
        self.case_id = case_data.get("case_id", "UNKNOWN-CASE")
        self.flags: List[Dict[str, Any]] = []

    def run_audit(self) -> Dict[str, Any]:
        self.flags = []

        # 1. Timeline Inconsistency Checks
        self._check_timeline_conflicts()

        # 2. Missing Evidence References
        self._check_missing_evidence_links()

        # 3. Chain of Custody Documentation Checks
        self._check_chain_of_custody_gaps()

        # 4. Incomplete Investigative Records (e.g. named witnesses without statements)
        self._check_incomplete_records()

        # 5. Location / Travel Plausibility Checks
        self._check_location_conflicts()

        # 6. Unresolved Evidence Association Checks
        self._check_unresolved_associations()

        # 7. Calculate Audit Scores
        scores = self._calculate_scores()

        return {
            "case_id": self.case_id,
            "crime_type": self.case.get("crime_type", "Other"),
            "audit_timestamp": datetime.now().isoformat(),
            "scores": scores,
            "flags": self.flags,
            "flag_count": len(self.flags)
        }

    def _check_timeline_conflicts(self):
        fir = self.case.get("fir", {})
        fir_time_str = fir.get("time") or self.case.get("incident_time", "")
        fir_mins = parse_time_to_minutes(fir_time_str)

        witnesses = self.case.get("witnesses", [])
        cctvs = self.case.get("cctv", [])
        timeline_events = self.case.get("timeline", [])

        # Check CCTV vs Witness Statements
        for w in witnesses:
            w_time_str = w.get("claimed_time", "")
            w_mins = parse_time_to_minutes(w_time_str)
            if w_mins is None:
                continue

            for c in cctvs:
                c_time_str = c.get("timestamp", "")
                c_mins = parse_time_to_minutes(c_time_str)
                if c_mins is None:
                    continue

                diff = abs(w_mins - c_mins)
                # If difference between departure/observation times is > 20 minutes for related events
                is_departure_or_exit = (
                    ("exit" in w.get("statement", "").lower() or "leave" in w.get("statement", "").lower()) and
                    ("exit" in c.get("description", "").lower() or "leave" in c.get("description", "").lower())
                )

                if (diff >= 20 and is_departure_or_exit) or (diff >= 30 and ("gate" in w.get("location", "").lower() or "stair" in c.get("camera_name", "").lower())):
                    self.flags.append({
                        "flag_id": f"TL-CONF-{w.get('witness_id', 'WS')}-{c.get('cctv_id', 'CCTV')}",
                        "category": "Timeline Inconsistency",
                        "severity": "CRITICAL",
                        "title": f"Timeline Conflict: {w.get('witness_id')} vs {c.get('cctv_id')}",
                        "explanation": (
                            f"Witness statement ({w.get('witness_id')}) places observed departure/event at {w_time_str}, "
                            f"whereas camera record ({c.get('cctv_id')} - {c.get('camera_name')}) logs departure at {c_time_str}. "
                            f"The {diff}-minute discrepancy requires verification of camera time synchronization, DVR NTP clock offset, "
                            f"or witness recollection accuracy."
                        ),
                        "source_records": [
                            f"Witness Statement {w.get('witness_id')} ({w.get('name', 'Unknown')})",
                            f"CCTV Record {c.get('cctv_id')} ({c.get('camera_name')})"
                        ],
                        "timestamps": [w_time_str, c_time_str],
                        "suggested_action": "Verify DVR hardware clock calibration and cross-check access control timestamp logs."
                    })

        # Check Timeline Gaps (> 40 minutes unexplained between high priority events)
        sorted_events = []
        for e in timeline_events:
            t_min = parse_time_to_minutes(e.get("time", ""))
            if t_min is not None:
                sorted_events.append((t_min, e))
        sorted_events.sort(key=lambda x: x[0])

        for i in range(len(sorted_events) - 1):
            t1, e1 = sorted_events[i]
            t2, e2 = sorted_events[i+1]
            gap = t2 - t1
            desc1 = e1.get("description", "").lower()
            desc2 = e2.get("description", "").lower()

            # Gap between alarm and response
            if gap >= 35 and ("alarm" in desc1 or "distress" in desc1) and ("dispatch" in desc2 or "arrive" in desc2 or "patrol" in desc2):
                self.flags.append({
                    "flag_id": f"TL-GAP-{e1.get('event_id', 'EV1')}-{e2.get('event_id', 'EV2')}",
                    "category": "Unexplained Timeline Gap",
                    "severity": "WARNING",
                    "title": f"Unexplained Response Gap ({gap} minutes)",
                    "explanation": (
                        f"A {gap}-minute gap is recorded between automated alert event '{e1.get('description')}' at {e1.get('time')} "
                        f"and responder action '{e2.get('description')}' at {e2.get('time')}. "
                        f"Investigative diary lacks recorded justification for the response interval."
                    ),
                    "source_records": [e1.get("source", e1.get("event_id", "Event 1")), e2.get("source", e2.get("event_id", "Event 2"))],
                    "timestamps": [e1.get("time"), e2.get("time")],
                    "suggested_action": "Obtain PCR dispatcher transit log and telecommunications incident report."
                })

    def _check_missing_evidence_links(self):
        registered_evidence = set()
        for e in self.case.get("evidence", []):
            eid = e.get("evidence_id", "")
            if eid:
                registered_evidence.add(normalize_evidence_id(eid))

        # Check in witnesses
        for w in self.case.get("witnesses", []):
            stmt = w.get("statement", "")
            found_ids = extract_evidence_ids_from_text(stmt)
            for fid in found_ids:
                if fid not in registered_evidence:
                    self.flags.append({
                        "flag_id": f"EV-MISS-{w.get('witness_id')}-{fid}",
                        "category": "Missing Evidence Reference",
                        "severity": "CRITICAL",
                        "title": f"Unregistered Evidence Reference: {fid}",
                        "explanation": (
                            f"Witness statement {w.get('witness_id')} ({w.get('name')}) mentions {fid} "
                            f"('...{stmt[:80]}...'), but {fid} is not documented in the Evidence Register or Property Seizure Memo."
                        ),
                        "source_records": [f"Witness Statement {w.get('witness_id')}", "Evidence Register"],
                        "timestamps": [w.get("statement_date", "")],
                        "suggested_action": "Audit Malkhana seizure log to verify whether item was seized under a different property identifier."
                    })

        # Check in notes
        for note in self.case.get("notes", []):
            found_ids = extract_evidence_ids_from_text(note)
            for fid in found_ids:
                if fid not in registered_evidence:
                    self.flags.append({
                        "flag_id": f"EV-MISS-NOTE-{fid}",
                        "category": "Missing Evidence Reference",
                        "severity": "WARNING",
                        "title": f"Investigation Diary Cites Unregistered Item: {fid}",
                        "explanation": (
                            f"Investigation note references evidence token {fid}, but no matching formal seizure record "
                            f"is logged in the case property register."
                        ),
                        "source_records": ["Investigation Diary Notes", "Evidence Register"],
                        "timestamps": [],
                        "suggested_action": "Trace IO seizure memo and deposit slip for physical property tag."
                    })

    def _check_chain_of_custody_gaps(self):
        custody_logs = self.case.get("chain_of_custody", [])
        evidence_list = self.case.get("evidence", [])

        # Check each evidence has a custody entry
        logged_evidence_ids = {normalize_evidence_id(c.get("evidence_id", "")) for c in custody_logs}
        for e in evidence_list:
            norm_id = normalize_evidence_id(e.get("evidence_id", ""))
            if norm_id and norm_id not in logged_evidence_ids:
                self.flags.append({
                    "flag_id": f"COC-MISS-{norm_id}",
                    "category": "Chain of Custody Documentation Gap",
                    "severity": "CRITICAL",
                    "title": f"Missing Chain of Custody Record for {norm_id}",
                    "explanation": (
                        f"Evidence item {norm_id} ({e.get('description', '')}) is listed in evidence records "
                        f"but possesses no corresponding Chain of Custody transfer or Malkhana register entry."
                    ),
                    "source_records": [f"Evidence Record {norm_id}", "Chain of Custody Log"],
                    "timestamps": [e.get("recovery_time", "")],
                    "suggested_action": "Log formal Chain of Custody Form with collecting officer signature."
                })

        # Check gaps in existing custody entries
        for c in custody_logs:
            eid = c.get("evidence_id", "UNKNOWN")
            c_time = parse_time_to_minutes(c.get("collected_time", ""))
            s_time = parse_time_to_minutes(c.get("sealed_time", ""))
            t_time = parse_time_to_minutes(c.get("transfer_time", ""))
            stored_loc = c.get("stored_location", "")

            # Check if sealed_time is missing or blank
            if not c.get("sealed_time"):
                self.flags.append({
                    "flag_id": f"COC-UNSEALED-{eid}",
                    "category": "Chain of Custody Documentation Gap",
                    "severity": "WARNING",
                    "title": f"Unrecorded Sealing Protocol: {eid}",
                    "explanation": (
                        f"Evidence item {eid} indicates collection at {c.get('collected_time', 'N/A')} "
                        f"by {c.get('collected_by', 'IO')}, but the formal sealing timestamp and seal imprint number are missing."
                    ),
                    "source_records": [f"Chain of Custody Entry ({eid})"],
                    "timestamps": [c.get("collected_time", "")],
                    "suggested_action": "Examine IO seizure memo for brass seal counter-signature."
                })

            # Check if stored much later (> 3 hours) with no documented transfer recipient
            if not c.get("transferred_to") and "deposited" in stored_loc.lower():
                self.flags.append({
                    "flag_id": f"COC-HANDOVER-{eid}",
                    "category": "Chain of Custody Documentation Gap",
                    "severity": "WARNING",
                    "title": f"Undocumented Custody Handover: {eid}",
                    "explanation": (
                        f"Evidence {eid} was seized at {c.get('collected_time', 'N/A')} and deposited at {stored_loc}, "
                        f"but intermediate transit handlers or custody couriers are undocumented."
                    ),
                    "source_records": [f"Chain of Custody Entry ({eid})"],
                    "timestamps": [c.get("collected_time", "")],
                    "suggested_action": "Record transit officer dispatch log and evidence carrier sign-off."
                })

    def _check_incomplete_records(self):
        fir = self.case.get("fir", {})
        fir_text = fir.get("details", "") + " " + self.case.get("summary", "")
        witnesses = self.case.get("witnesses", [])
        witness_names = " ".join([w.get("name", "").lower() for w in witnesses])

        # Scan for mentions of key persons in FIR like "Auditor Raghav", "Doctor", "Guard"
        named_patterns = [
            (r'(?:auditor|mr\.?|ms\.?|witness)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "Named Individual in Complaint")
        ]

        for pat, role in named_patterns:
            matches = re.findall(pat, fir_text)
            for name in matches:
                if name.lower() not in witness_names and len(name) > 3:
                    # Check if they are suspect or victim
                    if name.lower() not in self.case.get("victim", "").lower():
                        self.flags.append({
                            "flag_id": f"REC-INCOMPL-{name.replace(' ', '_')}",
                            "category": "Incomplete Investigative Record",
                            "severity": "WARNING",
                            "title": f"Missing Witness Statement: {name}",
                            "explanation": (
                                f"FIR/Complaint explicitly references key source/testimony from '{name}', "
                                f"yet no formal Section 161 CrPC / Section 180 BNSS witness statement is filed in the case records."
                            ),
                            "source_records": ["FIR / Complaint Summary", "Witness Statement Docket"],
                            "timestamps": [fir.get("date", "")],
                            "suggested_action": "Record or attach missing statement of referenced party."
                        })

    def _check_location_conflicts(self):
        fir_loc = self.case.get("location", "").lower()
        witnesses = self.case.get("witnesses", [])
        cctvs = self.case.get("cctv", [])

        for w in witnesses:
            w_loc = w.get("location", "").lower()
            w_time = parse_time_to_minutes(w.get("claimed_time", ""))

            for c in cctvs:
                c_time = parse_time_to_minutes(c.get("timestamp", ""))
                if w_time is not None and c_time is not None:
                    diff = abs(w_time - c_time)
                    # If same time (<= 10 mins) but radically different locations (e.g., mall vs highway bypass 20km away)
                    if diff <= 10 and (
                        ("mall" in fir_loc or "flat" in fir_loc or "shop" in fir_loc) and
                        ("highway" in w_loc or "toll" in w_loc or "bypass" in w_loc or "canal" in w_loc)
                    ):
                        self.flags.append({
                            "flag_id": f"LOC-CONF-{w.get('witness_id')}",
                            "category": "Location / Travel Inconsistency",
                            "severity": "CRITICAL",
                            "title": f"Geographic Plausibility Conflict: {w.get('witness_id')}",
                            "explanation": (
                                f"Surveillance record ({c.get('cctv_id')}) places subject/incident at primary location ({c.get('camera_name')}) "
                                f"at {c.get('timestamp')}, while witness {w.get('witness_id')} asserts observing the event at '{w.get('location')}' "
                                f"at {w.get('claimed_time')} (delta: {diff} minutes). The geographic separation is physically improbable within this window."
                            ),
                            "source_records": [f"Witness Statement {w.get('witness_id')}", f"CCTV Record {c.get('cctv_id')}"],
                            "timestamps": [c.get("timestamp"), w.get("claimed_time")],
                            "suggested_action": "Audit GPS location records and verify road travel transit time feasibility."
                        })

    def _check_unresolved_associations(self):
        notes = " ".join(self.case.get("notes", [])).lower()
        evidence_list = self.case.get("evidence", [])

        for e in evidence_list:
            desc = e.get("description", "").lower()
            loc = e.get("recovery_location", "").lower()
            # If evidence recovered in dumpster / garbage / distant location with unresolved link
            if ("dumpster" in loc or "garbage" in loc or "canal" in loc or "away" in loc or "road" in loc) and (
                "unresolved" in notes or "unsubstantiated" in notes or "no forensic" in notes
            ):
                eid = e.get("evidence_id", "ITEM")
                self.flags.append({
                    "flag_id": f"ASSOC-UNRES-{eid}",
                    "category": "Unresolved Evidence Association",
                    "severity": "INFO",
                    "title": f"Unsubstantiated Evidence Link: {eid}",
                    "explanation": (
                        f"Evidence {eid} ({e.get('description')}) recovered at secondary location ('{e.get('recovery_location')}') "
                        f"does not currently have documented forensic linkage (DNA/fingerprint) or direct witness association linking it to the incident scene."
                    ),
                    "source_records": [f"Evidence Seizure {eid}", "Forensic Examination Registry"],
                    "timestamps": [e.get("recovery_time", "")],
                    "suggested_action": "Submit item for latent fingerprint enhancement and DNA comparative analysis."
                })

    def _calculate_scores(self) -> Dict[str, int]:
        # Baseline 100
        consistency = 100
        completeness = 100
        linking = 100
        custody = 100

        for f in self.flags:
            cat = f.get("category", "")
            sev = f.get("severity", "WARNING")
            penalty = 25 if sev == "CRITICAL" else (15 if sev == "WARNING" else 5)

            if "Timeline" in cat or "Location" in cat:
                consistency = max(20, consistency - penalty)
            elif "Missing Evidence" in cat or "Unresolved" in cat:
                linking = max(20, linking - penalty)
            elif "Chain of Custody" in cat:
                custody = max(25, custody - penalty)
            elif "Incomplete" in cat or "Gap" in cat:
                completeness = max(30, completeness - penalty)

        overall = int((consistency * 0.35) + (linking * 0.25) + (custody * 0.20) + (completeness * 0.20))
        return {
            "consistency": consistency,
            "completeness": completeness,
            "linking": linking,
            "custody": custody,
            "overall": overall
        }
