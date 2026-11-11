import os
import json

CASES = [
    {
        "case_id": "CASE-001",
        "title": "Homicide Investigation at Metro Heights Apartment",
        "crime_type": "Murder",
        "incident_date": "2024-10-12",
        "incident_time": "21:00",
        "location": "Flat 402, Metro Heights Apartment, Sector 14",
        "victim": "Arun Kumar (Age 38, Architect)",
        "suspects": ["Vikram Rao (Former Business Associate)", "Ramesh Verma (Building Caretaker)"],
        "summary": "Victim Arun Kumar discovered deceased in living room from sharp force trauma. Investigation initiated on receipt of PCR call at 21:30 hrs.",
        "fir": {
            "fir_number": "FIR-2024-8841",
            "ps": "Central District Police Station",
            "date": "2024-10-12",
            "time": "21:00",
            "complainant": "Officer S. Rawat (SI)",
            "details": "Incident occurred around 21:00 hrs on 12-Oct-2024. Victim suffered fatal stab injury. Neighbor raised distress call. Security logs and area surveillance impounded.",
            "sections": "Section 302 IPC / Section 103 BNS"
        },
        "witnesses": [
            {
                "witness_id": "WS-001",
                "name": "Neha Sharma (Neighbor, Flat 403)",
                "statement_date": "2024-10-13",
                "claimed_time": "21:10",
                "location": "4th Floor Corridor",
                "statement": "I stepped into the corridor to fetch a delivery and saw an agitated male wearing a dark hooded jacket briskly exit Flat 402 at approximately 21:10 hrs. Heard a heavy door slam just prior."
            },
            {
                "witness_id": "WS-002",
                "name": "Ramesh Verma (Ground Floor Caretaker)",
                "statement_date": "2024-10-13",
                "claimed_time": "20:55",
                "location": "Building Entry Gate",
                "statement": "Saw Mr. Vikram Rao enter the premises at around 20:30 hrs. Did not observe anyone running past the gate after 21:00 hrs."
            }
        ],
        "cctv": [
            {
                "cctv_id": "CCTV-001",
                "camera_name": "Main Stairwell North Camera (CAM-04)",
                "timestamp": "20:40",
                "date": "2024-10-12",
                "description": "Footage shows a tall individual in dark hooded clothing exiting the 4th floor stairwell and leaving the camera frame towards the rear exit at 20:40 hrs.",
                "relevance": "Key departure timeline record"
            },
            {
                "cctv_id": "CCTV-002",
                "camera_name": "Ground Floor Lobby Camera (CAM-01)",
                "timestamp": "20:28",
                "date": "2024-10-12",
                "description": "Footage captures guest arrival at lobby entry at 20:28 hrs.",
                "relevance": "Premises entry verification"
            }
        ],
        "evidence": [
            {
                "evidence_id": "E-001",
                "type": "Physical Weapon",
                "description": "Stainless steel chef knife (8-inch blade) with blood staining found near kitchen counter.",
                "recovery_location": "Kitchen counter, Flat 402",
                "recovery_time": "22:15",
                "recovery_date": "2024-10-12",
                "officer": "IO Inspector Sharma"
            },
            {
                "evidence_id": "E-002",
                "type": "Digital Storage",
                "description": "Hikvision NVR Hard Drive (2TB) containing CCTV streams CAM-01 to CAM-08.",
                "recovery_location": "Building Security Room",
                "recovery_time": "23:00",
                "recovery_date": "2024-10-12",
                "officer": "Cyber Cell SI Verma"
            }
        ],
        "timeline": [
            {"event_id": "EVT-001", "time": "20:28", "date": "2024-10-12", "description": "Lobby CCTV records entry of visitor into building.", "source": "CCTV-002"},
            {"event_id": "EVT-002", "time": "20:40", "date": "2024-10-12", "description": "Stairwell CCTV records hooded male exiting stairwell.", "source": "CCTV-001"},
            {"event_id": "EVT-003", "time": "21:00", "date": "2024-10-12", "description": "FIR logged time of fatal incident occurrence.", "source": "FIR-2024-8841"},
            {"event_id": "EVT-004", "time": "21:10", "date": "2024-10-12", "description": "Witness Neha Sharma reports seeing male leave Flat 402.", "source": "WS-001"},
            {"event_id": "EVT-005", "time": "21:30", "date": "2024-10-12", "description": "First responder PCR unit arrives at Flat 402.", "source": "Police Diary"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-001",
                "collected_by": "IO Inspector Sharma",
                "collected_time": "22:15",
                "sealed_time": "22:30",
                "transferred_to": "Head Constable M. Lal (Malkhana Custodian)",
                "transfer_time": "23:45",
                "stored_location": "Police Station Evidence Locker #4",
                "status": "Sealed & Logged"
            },
            {
                "evidence_id": "E-002",
                "collected_by": "Cyber Cell SI Verma",
                "collected_time": "23:00",
                "sealed_time": "23:20",
                "transferred_to": "Digital Forensic Lab, Rohini",
                "transfer_time": "09:00",
                "stored_location": "DFL Secure Locker A-12",
                "status": "Transferred"
            }
        ],
        "notes": [
            "Autopsy report estimates time of death between 20:30 and 21:30 hrs.",
            "Critical conflict noted: CCTV shows exit at 20:40 hrs, but witness WS-001 reports seeing departure at 21:10 hrs. Check camera clock calibration against atomic network time."
        ],
        "intentional_flags": [
            "Timeline conflict: Witness WS-001 states departure at 21:10, whereas CCTV-001 indicates departure at 20:40 (30-minute discrepancy)."
        ]
    },
    {
        "case_id": "CASE-002",
        "title": "Riverside Estate Robbery & Homicide",
        "crime_type": "Murder",
        "incident_date": "2024-11-04",
        "incident_time": "22:30",
        "location": "Farmhouse 12, Riverside Estate, Badarpur Border",
        "victim": "Sanjay Mehta (Age 52, Industrialist)",
        "suspects": ["Anil Thakur (Former Driver)"],
        "summary": "Break-in and fatal assault during robbery. Gold ornaments and safe keys reported missing.",
        "fir": {
            "fir_number": "FIR-2024-9102",
            "ps": "Badarpur Police Station",
            "date": "2024-11-04",
            "time": "22:30",
            "complainant": "Sunita Mehta (Spouse)",
            "details": "Two armed individuals forced entry into master bedroom, demanded safe combinations, and struck victim before fleeing through rear boundary wall.",
            "sections": "Section 302, 397 IPC / Section 103, 311 BNS"
        },
        "witnesses": [
            {
                "witness_id": "WS-101",
                "name": "Karan Singh (Estate Security Guard)",
                "statement_date": "2024-11-05",
                "claimed_time": "22:45",
                "location": "Rear Boundary Canal",
                "statement": "While chasing the suspects towards the canal, I discovered an abandoned iron crowbar and a blood-stained leather glove labeled Evidence E-104 discarded near the drainage culvert. I handed it to the responding night patrol."
            },
            {
                "witness_id": "WS-102",
                "name": "Sunita Mehta (Spouse)",
                "statement_date": "2024-11-05",
                "claimed_time": "22:30",
                "location": "Master Bedroom",
                "statement": "Attackers spoke in local dialect, demanded jewellery keys, and dropped a flashlight Evidence E-101 on the carpet."
            }
        ],
        "cctv": [
            {
                "cctv_id": "CCTV-101",
                "camera_name": "Perimeter Wall South Camera",
                "timestamp": "22:42",
                "date": "2024-11-04",
                "description": "Two individuals scaling the south perimeter wall into the dark thicket.",
                "relevance": "Perimeter escape recording"
            }
        ],
        "evidence": [
            {
                "evidence_id": "E-101",
                "type": "Physical Item",
                "description": "Heavy duty aluminum flashlight with rubberized grip.",
                "recovery_location": "Master Bedroom Carpet",
                "recovery_time": "23:40",
                "recovery_date": "2024-11-04",
                "officer": "SI R. K. Dogra"
            },
            {
                "evidence_id": "E-102",
                "type": "Latent Fingerprints",
                "description": "Lifted ridge patterns from bedroom window latch.",
                "recovery_location": "Bedroom Window Frame",
                "recovery_time": "00:15",
                "recovery_date": "2024-11-05",
                "officer": "Mobile Forensic Unit Tech"
            }
        ],
        "timeline": [
            {"event_id": "EVT-101", "time": "22:30", "date": "2024-11-04", "description": "Break-in reported at Master Bedroom.", "source": "FIR-2024-9102"},
            {"event_id": "EVT-102", "time": "22:42", "date": "2024-11-04", "description": "Perimeter CCTV captures suspects jumping wall.", "source": "CCTV-101"},
            {"event_id": "EVT-103", "time": "23:10", "date": "2024-11-04", "description": "Police team arrives at farmhouse.", "source": "Police Dispatch Log"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-101",
                "collected_by": "SI R. K. Dogra",
                "collected_time": "23:40",
                "sealed_time": "23:55",
                "transferred_to": "District Malkhana",
                "transfer_time": "02:00",
                "stored_location": "Seizure Shelf B-4",
                "status": "Secure"
            }
        ],
        "notes": [
            "Weapon used in assault believed to be blunt iron tool.",
            "CRITICAL GAP: Witness statement WS-101 specifically mentions discovering Evidence E-104 (crowbar and glove) at canal culvert, but E-104 does NOT exist in the evidence register or seizure memo."
        ],
        "intentional_flags": [
            "Missing Evidence Link: Evidence E-104 cited in Witness WS-101 statement is missing from Evidence Register and Property Seizure records."
        ]
    },
    {
        "case_id": "CASE-003",
        "title": "Industrial Warehouse Fatal Shooting",
        "crime_type": "Murder",
        "incident_date": "2024-09-18",
        "incident_time": "19:15",
        "location": "Godown 7, Peenya Industrial Area, Phase II",
        "victim": "Dinesh Gowda (Age 45, Contractor)",
        "suspects": ["Manoj K. (Subcontractor)"],
        "summary": "Shooting following financial altercation at site office. All records, witness statements, ballistic recovery, and surveillance timestamps corroborate.",
        "fir": {
            "fir_number": "FIR-2024-7720",
            "ps": "Peenya Police Station",
            "date": "2024-09-18",
            "time": "19:15",
            "complainant": "B. Shivaraj (Storekeeper)",
            "details": "Heard loud shouts followed by two gunshots from godown office at 19:15 hrs. Suspect Manoj observed fleeing on motorcycle bearing KA-02-EZ-4412.",
            "sections": "Section 302 IPC / Section 25 Arms Act"
        },
        "witnesses": [
            {
                "witness_id": "WS-301",
                "name": "B. Shivaraj (Storekeeper)",
                "statement_date": "2024-09-18",
                "claimed_time": "19:15",
                "location": "Godown Front Gate",
                "statement": "Was checking gate manifests at 19:15 hrs. Heard two loud bangs. Saw suspect Manoj sprint to his motorcycle and speed off towards Ring Road."
            },
            {
                "witness_id": "WS-302",
                "name": "Pradeep R. (Security Guard)",
                "statement_date": "2024-09-18",
                "claimed_time": "19:18",
                "location": "Weighbridge Outpost",
                "statement": "Noted suspect motorcycle KA-02-EZ-4412 speeding past weighbridge at exactly 19:18 hrs towards Ring Road."
            }
        ],
        "cctv": [
            {
                "cctv_id": "CCTV-301",
                "camera_name": "Weighbridge Automated Camera",
                "timestamp": "19:18",
                "date": "2024-09-18",
                "description": "Color capture of motorcycle KA-02-EZ-4412 crossing weighbridge gate at 19:18 hrs.",
                "relevance": "Corroborates witness statement WS-302"
            }
        ],
        "evidence": [
            {
                "evidence_id": "E-301",
                "type": "Ballistic Cartridge",
                "description": "Two spent 7.65mm brass cartridge cases recovered from office floor.",
                "recovery_location": "Office Chamber Floor, Godown 7",
                "recovery_time": "20:00",
                "recovery_date": "2024-09-18",
                "officer": "Inspector Venkatesh"
            }
        ],
        "timeline": [
            {"event_id": "EVT-301", "time": "19:15", "date": "2024-09-18", "description": "Gunshots heard; incident reported in FIR.", "source": "FIR-2024-7720"},
            {"event_id": "EVT-302", "time": "19:18", "date": "2024-09-18", "description": "Motorcycle captured on CCTV and seen by guard.", "source": "CCTV-301"},
            {"event_id": "EVT-303", "time": "20:00", "date": "2024-09-18", "description": "Ballistic evidence E-301 collected and sealed.", "source": "Seizure Memo"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-301",
                "collected_by": "Inspector Venkatesh",
                "collected_time": "20:00",
                "sealed_time": "20:20",
                "transferred_to": "Forensic Science Laboratory (FSL) Ballistics",
                "transfer_time": "21:30",
                "stored_location": "FSL Vault Room 3",
                "status": "Transferred Under Seal"
            }
        ],
        "notes": [
            "Records demonstrate strong cross-document alignment with zero internal timeline or inventory conflicts.",
            "Case serves as verified baseline for consistent investigation records."
        ],
        "intentional_flags": []
    },
    {
        "case_id": "CASE-004",
        "title": "Jewelry Showroom Armed Robbery",
        "crime_type": "Robbery",
        "incident_date": "2024-08-22",
        "incident_time": "14:15",
        "location": "Kalyan Jewellers Commercial Branch, MG Road",
        "victim": "Staff & Store Manager R. Sethi",
        "suspects": ["Unknown masked trio"],
        "summary": "Armed heist of gold ornaments and cash vault. Seized cash bundle exhibits undocumented chain-of-custody transfer gap.",
        "fir": {
            "fir_number": "FIR-2024-6511",
            "ps": "Central Commercial PS",
            "date": "2024-08-22",
            "time": "14:15",
            "complainant": "R. Sethi (Manager)",
            "details": "Three masked men armed with country-made pistols entered showroom at 14:15 hrs, overpowered guards, and looted tray displays and vault cash.",
            "sections": "Section 392, 397 IPC / Section 309 BNS"
        },
        "witnesses": [
            {
                "witness_id": "WS-401",
                "name": "Meera Joshi (Sales Executive)",
                "statement_date": "2024-08-22",
                "claimed_time": "14:15",
                "location": "Counter 3",
                "statement": "They entered right after lunch hour at 14:15 hrs. Packed cash packets into duffel bags."
            }
        ],
        "cctv": [
            {
                "cctv_id": "CCTV-401",
                "camera_name": "Overhead Showroom Cam 1",
                "timestamp": "14:16",
                "date": "2024-08-22",
                "description": "Three individuals brandishing weapons at billing counter.",
                "relevance": "Heist execution recording"
            }
        ],
        "evidence": [
            {
                "evidence_id": "E-401",
                "type": "Currency Notes",
                "description": "Recovered bundle of 100 currency notes (Rs 50,000) dropped near rear exit door.",
                "recovery_location": "Rear Fire Exit Staircase",
                "recovery_time": "14:45",
                "recovery_date": "2024-08-22",
                "officer": "Sub-Inspector H. K. Roy"
            }
        ],
        "timeline": [
            {"event_id": "EVT-401", "time": "14:15", "date": "2024-08-22", "description": "Armed robbery occurs.", "source": "FIR-2024-6511"},
            {"event_id": "EVT-402", "time": "14:45", "date": "2024-08-22", "description": "Cash bundle E-401 recovered at fire exit.", "source": "Seizure Memo"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-401",
                "collected_by": "SI H. K. Roy",
                "collected_time": "14:45",
                "sealed_time": "",
                "transferred_to": "",
                "transfer_time": "",
                "stored_location": "Police Station Safe (Deposited at 19:30 hrs)",
                "status": "Logged at 19:30"
            }
        ],
        "notes": [
            "Chain of custody documentation gap detected: Evidence E-401 was seized at 14:45 hrs but stored at 19:30 hrs with no documented sealing, transit escort, or intermediate custody handover log."
        ],
        "intentional_flags": [
            "Chain of Custody Gap: Evidence E-401 has missing sealing time and missing transfer recipient between 14:45 collection and 19:30 station deposit."
        ]
    },
    {
        "case_id": "CASE-005",
        "title": "Minor Abduction from Shopping Mall",
        "crime_type": "Kidnapping / Abduction",
        "incident_date": "2024-10-01",
        "incident_time": "17:30",
        "location": "North Gate City Mall, Ring Road",
        "victim": "Master Aarav (Age 9)",
        "suspects": ["Unidentified driver of silver sedan"],
        "summary": "Alleged abduction of school child from shopping arcade. Severe geographic contradiction between FIR incident location and prime witness statement.",
        "fir": {
            "fir_number": "FIR-2024-9540",
            "ps": "North Town PS",
            "date": "2024-10-01",
            "time": "17:30",
            "complainant": "Vandana Kapoor (Mother)",
            "details": "Child went missing near toy store on 2nd floor of North Gate City Mall at 17:30 hrs. Search of mall premises yielded negative results.",
            "sections": "Section 363 IPC / Section 137 BNS"
        },
        "witnesses": [
            {
                "witness_id": "WS-501",
                "name": "Rohan Bakshi (Mall Security)",
                "statement_date": "2024-10-01",
                "claimed_time": "17:35",
                "location": "North Gate City Mall Exit Gate 2",
                "statement": "Mother raised alarm at 17:35 hrs inside the mall lobby."
            },
            {
                "witness_id": "WS-502",
                "name": "Devendra Pal (Highway Toll Worker)",
                "statement_date": "2024-10-01",
                "claimed_time": "17:30",
                "location": "Eastern Bypass Toll Plaza (22 km away)",
                "statement": "I witnessed a child matching Aarav's exact uniform being forcibly pulled into a silver sedan at Eastern Bypass Toll Plaza at exactly 17:30 hrs."
            }
        ],
        "cctv": [
            {
                "cctv_id": "CCTV-501",
                "camera_name": "North Gate Mall Cam 6",
                "timestamp": "17:25",
                "date": "2024-10-01",
                "description": "Child Aarav seen with mother near escalator inside North Gate Mall at 17:25 hrs.",
                "relevance": "Confirms presence inside mall at 17:25"
            }
        ],
        "evidence": [
            {
                "evidence_id": "E-501",
                "type": "Personal Effect",
                "description": "Blue school bag belonging to victim recovered in mall restroom.",
                "recovery_location": "Mall 2nd Floor Restroom",
                "recovery_time": "18:10",
                "recovery_date": "2024-10-01",
                "officer": "W/SI Poonam"
            }
        ],
        "timeline": [
            {"event_id": "EVT-501", "time": "17:25", "date": "2024-10-01", "description": "Child observed on mall camera.", "source": "CCTV-501"},
            {"event_id": "EVT-502", "time": "17:30", "date": "2024-10-01", "description": "FIR incident timestamp inside North Gate Mall.", "source": "FIR-2024-9540"},
            {"event_id": "EVT-503", "time": "17:30", "date": "2024-10-01", "description": "Witness claims seeing abduction 22km away at Bypass Toll.", "source": "WS-502"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-501",
                "collected_by": "W/SI Poonam",
                "collected_time": "18:10",
                "sealed_time": "18:30",
                "transferred_to": "Investigating Officer Locker",
                "transfer_time": "19:00",
                "stored_location": "Case Property Locker 3",
                "status": "Secured"
            }
        ],
        "notes": [
            "Severe location conflict: CCTV-501 places victim in North Gate Mall at 17:25 hrs. It is physically impossible for the victim to be 22 km away at Eastern Bypass Toll Plaza at 17:30 hrs (5 minutes later). Witness WS-502 record requires critical human verification."
        ],
        "intentional_flags": [
            "Location/Travel Inconsistency: Witness WS-502 claims event occurred at Eastern Bypass (22 km away) at 17:30, while CCTV confirms subject at Mall at 17:25."
        ]
    },
    {
        "case_id": "CASE-006",
        "title": "Corporate Treasury Cyber Fraud & Wire Transfer",
        "crime_type": "Cybercrime",
        "incident_date": "2024-11-15",
        "incident_time": "11:45",
        "location": "Nexus Financial Towers, Financial District",
        "victim": "Apex Global Logistics Pvt Ltd",
        "suspects": ["Internal system administrator / spoofed credentials"],
        "summary": "Unauthorized RTGS transfer of Rs 4.2 Crores via manipulated SWIFT gateway. FIR cites pivotal audit testimony from Senior IT Auditor, but no formal witness statement exists.",
        "fir": {
            "fir_number": "FIR-2024-11029",
            "ps": "State Cyber Crime Police Station",
            "date": "2024-11-15",
            "time": "11:45",
            "complainant": "Rajeev Saxena (CFO)",
            "details": "At 11:45 hrs, fraudulent wire instruction executed. As confirmed by Internal IT Security Auditor Mr. Raghav Kulkarni in initial briefing, the server token was hijacked.",
            "sections": "Section 420, 468 IPC / Section 66C, 66D IT Act"
        },
        "witnesses": [
            {
                "witness_id": "WS-601",
                "name": "Pooja Hegde (Accounts Manager)",
                "statement_date": "2024-11-16",
                "claimed_time": "11:50",
                "location": "Accounts Hall",
                "statement": "Received confirmation SMS for outbound transfer that was never authorized by CFO."
            }
        ],
        "cctv": [],
        "evidence": [
            {
                "evidence_id": "E-601",
                "type": "Digital Server Logs",
                "description": "Apache and gateway access logs exported as tarball.",
                "recovery_location": "Server Room Rack 4",
                "recovery_time": "14:00",
                "recovery_date": "2024-11-15",
                "officer": "Cyber Inspector S. Murthy"
            }
        ],
        "timeline": [
            {"event_id": "EVT-601", "time": "11:45", "date": "2024-11-15", "description": "Unauthorized SWIFT transfer dispatched.", "source": "FIR-2024-11029"},
            {"event_id": "EVT-602", "time": "14:00", "date": "2024-11-15", "description": "Server logs E-601 seized.", "source": "Seizure Memo"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-601",
                "collected_by": "Cyber Inspector S. Murthy",
                "collected_time": "14:00",
                "sealed_time": "14:30",
                "transferred_to": "CERT-In Cyber Forensics Wing",
                "transfer_time": "17:00",
                "stored_location": "FSL Digital Vault",
                "status": "Under Analysis"
            }
        ],
        "notes": [
            "Incomplete Case Records: FIR explicitly names Senior IT Security Auditor Mr. Raghav Kulkarni as having verified the initial breach token, but NO recorded witness statement for Mr. Raghav Kulkarni exists in the case docket."
        ],
        "intentional_flags": [
            "Missing Investigative Record: FIR names essential witness Mr. Raghav Kulkarni, but no witness statement record is filed."
        ]
    },
    {
        "case_id": "CASE-007",
        "title": "Electronics Superstore Commercial Burglary",
        "crime_type": "Theft",
        "incident_date": "2024-07-09",
        "incident_time": "03:15",
        "location": "MegaTech Electronics, Commercial Boulevard",
        "victim": "MegaTech Retail Corp",
        "suspects": ["Two individuals in dark overalls"],
        "summary": "Theft of 45 high-end smartphones and tablets. Guard statement directly contradicts CCTV surveillance timestamp regarding physical presence at the main entrance.",
        "fir": {
            "fir_number": "FIR-2024-4421",
            "ps": "City South PS",
            "date": "2024-07-09",
            "time": "03:15",
            "complainant": "Girish Patel (Store Manager)",
            "details": "Glass panel shutter shattered and high-value mobile stock stolen between 03:00 and 03:30 hrs.",
            "sections": "Section 380, 457 IPC / Section 305, 331 BNS"
        },
        "witnesses": [
            {
                "witness_id": "WS-701",
                "name": "Surender Yadav (Night Watchman)",
                "statement_date": "2024-07-09",
                "claimed_time": "03:15",
                "location": "Main Entrance Gate",
                "statement": "I conducted physical physical round of the main entrance at exactly 03:15 hrs. The lock was completely intact and nobody was present anywhere near the front facade."
            }
        ],
        "cctv": [
            {
                "cctv_id": "CCTV-701",
                "camera_name": "Exterior Entrance 4K Camera",
                "timestamp": "03:15",
                "date": "2024-07-09",
                "description": "Footage displays two intruders cutting the lock and pulling open the rolling shutter at 03:15 hrs. No security guard is visible in the frame.",
                "relevance": "Direct contradiction with guard statement"
            }
        ],
        "evidence": [
            {
                "evidence_id": "E-701",
                "type": "Physical Tool",
                "description": "Broken bolt cutter left beside display pedestal.",
                "recovery_location": "Front Shutter Threshold",
                "recovery_time": "06:30",
                "recovery_date": "2024-07-09",
                "officer": "ASI K. Swamy"
            }
        ],
        "timeline": [
            {"event_id": "EVT-701", "time": "03:15", "date": "2024-07-09", "description": "CCTV captures two thieves actively prying shutter.", "source": "CCTV-701"},
            {"event_id": "EVT-702", "time": "03:15", "date": "2024-07-09", "description": "Guard claims he inspected shutter at this exact time and it was intact.", "source": "WS-701"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-701",
                "collected_by": "ASI K. Swamy",
                "collected_time": "06:30",
                "sealed_time": "06:50",
                "transferred_to": "PS Property Room",
                "transfer_time": "08:00",
                "stored_location": "Rack 12",
                "status": "Stored"
            }
        ],
        "notes": [
            "Direct statement contradiction: Guard claims he was at entrance at 03:15 hrs and shutter was intact, while CCTV-701 clearly shows shutter being breached by two men at 03:15 hrs with guard absent."
        ],
        "intentional_flags": [
            "Contradiction between Witness Statement WS-701 and CCTV-701 at 03:15 hrs."
        ]
    },
    {
        "case_id": "CASE-008",
        "title": "Nightclub Alleyway Aggravated Assault",
        "crime_type": "Assault",
        "incident_date": "2024-11-20",
        "incident_time": "01:10",
        "location": "Rear Alley, Club Mirage, Outer Circle",
        "victim": "Sameer Joshi (Age 26)",
        "suspects": ["Rahul Taneja (Patron)"],
        "summary": "Violent brawl in rear alley behind nightclub. Unresolved evidence association: iron rod recovered 400m away with no established link to accused or victim.",
        "fir": {
            "fir_number": "FIR-2024-12401",
            "ps": "Connaught Place PS",
            "date": "2024-11-20",
            "time": "01:10",
            "complainant": "Sameer Joshi (Victim)",
            "details": "Attacked in alleyway following verbal argument inside club. Suffered blunt head trauma.",
            "sections": "Section 324, 326 IPC / Section 118 BNS"
        },
        "witnesses": [
            {
                "witness_id": "WS-801",
                "name": "Deepak Chawla (Bouncer)",
                "statement_date": "2024-11-20",
                "claimed_time": "01:10",
                "location": "Club Rear Fire Exit",
                "statement": "Saw Rahul Taneja push Sameer Joshi against brick wall and swing a dark blunt object."
            }
        ],
        "cctv": [
            {
                "cctv_id": "CCTV-801",
                "camera_name": "Alleyway Security Camera",
                "timestamp": "01:12",
                "date": "2024-11-20",
                "description": "Footage shows confrontation between two males in alleyway.",
                "relevance": "Assault incident verification"
            }
        ],
        "evidence": [
            {
                "evidence_id": "E-801",
                "type": "Torn Fabric",
                "description": "Torn denim jacket sleeve recovered at assault spot.",
                "recovery_location": "Alley pavement behind Club Mirage",
                "recovery_time": "02:00",
                "recovery_date": "2024-11-20",
                "officer": "SI Naveen"
            },
            {
                "evidence_id": "E-802",
                "type": "Blunt Iron Rod",
                "description": "Rusted iron pipe (2.5 feet) recovered from municipal garbage bin 400 meters away.",
                "recovery_location": "Municipal Dumpster, Block M",
                "recovery_time": "08:30",
                "recovery_date": "2024-11-20",
                "officer": "SI Naveen"
            }
        ],
        "timeline": [
            {"event_id": "EVT-801", "time": "01:10", "date": "2024-11-20", "description": "Assault in alleyway reported.", "source": "FIR-2024-12401"},
            {"event_id": "EVT-802", "time": "01:12", "date": "2024-11-20", "description": "CCTV captures scuffle.", "source": "CCTV-801"},
            {"event_id": "EVT-803", "time": "02:00", "date": "2024-11-20", "description": "Fabric E-801 recovered at scene.", "source": "Seizure Memo"},
            {"event_id": "EVT-804", "time": "08:30", "date": "2024-11-20", "description": "Iron rod E-802 recovered 400m away.", "source": "Seizure Memo"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-801",
                "collected_by": "SI Naveen",
                "collected_time": "02:00",
                "sealed_time": "02:20",
                "transferred_to": "PS Malkhana",
                "transfer_time": "03:15",
                "stored_location": "Bin 9",
                "status": "Secured"
            },
            {
                "evidence_id": "E-802",
                "collected_by": "SI Naveen",
                "collected_time": "08:30",
                "sealed_time": "09:00",
                "transferred_to": "PS Malkhana",
                "transfer_time": "10:00",
                "stored_location": "Bin 10",
                "status": "Secured"
            }
        ],
        "notes": [
            "Unresolved Evidence Association: Evidence E-802 (iron rod) has no forensic blood swab report, no fingerprint match, and no witness statement placing it in the suspect's hands. Relationship between E-802 and case remains unsubstantiated."
        ],
        "intentional_flags": [
            "Unresolved Association: Evidence E-802 recovered 400m away lacks documented evidentiary connection to the crime scene or suspect."
        ]
    },
    {
        "case_id": "CASE-009",
        "title": "Extortion & Threatening Call Investigation",
        "crime_type": "Fraud",
        "incident_date": "2024-12-02",
        "incident_time": "16:00",
        "location": "Sunrise Developers Head Office, MG Road",
        "victim": "Alok Singhania (Real Estate Director)",
        "suspects": ["Sim Card Holder: Mohit Garg"],
        "summary": "Extortion demand of Rs 50 Lakhs via VOIP and burner SIM. Telecom CDR logs, voice recording, and bank account freeze verified with full consistency.",
        "fir": {
            "fir_number": "FIR-2024-13890",
            "ps": "Special Cell PS",
            "date": "2024-12-02",
            "time": "16:00",
            "complainant": "Alok Singhania",
            "details": "Received call demanding extortion money with threat of physical injury to family members.",
            "sections": "Section 384, 506 IPC / Section 308, 351 BNS"
        },
        "witnesses": [
            {
                "witness_id": "WS-901",
                "name": "Kavita Nair (Personal Assistant)",
                "statement_date": "2024-12-02",
                "claimed_time": "16:00",
                "location": "Executive Office",
                "statement": "Director received the call on speaker phone in my presence at 16:00 hrs. Threat was clearly audible."
            }
        ],
        "cctv": [],
        "evidence": [
            {
                "evidence_id": "E-901",
                "type": "Digital Audio File",
                "description": "Call audio recording (MP3 format) on secure USB drive.",
                "recovery_location": "Director Smart Phone Recording",
                "recovery_time": "16:45",
                "recovery_date": "2024-12-02",
                "officer": "Inspector V. Bhatia"
            }
        ],
        "timeline": [
            {"event_id": "EVT-901", "time": "16:00", "date": "2024-12-02", "description": "Extortion call received.", "source": "FIR-2024-13890"},
            {"event_id": "EVT-902", "time": "16:45", "date": "2024-12-02", "description": "Audio recording E-901 seized and hashed.", "source": "Seizure Memo"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-901",
                "collected_by": "Inspector V. Bhatia",
                "collected_time": "16:45",
                "sealed_time": "17:15",
                "transferred_to": "Digital Evidence Custodian",
                "transfer_time": "18:00",
                "stored_location": "Digital Vault D-2",
                "status": "Verified SHA-256 Hash"
            }
        ],
        "notes": [
            "All documented timestamps, CDR logs, audio files, and witness testimonies agree. High consistency baseline."
        ],
        "intentional_flags": []
    },
    {
        "case_id": "CASE-010",
        "title": "Commercial Bank Vault Heist",
        "crime_type": "Theft",
        "incident_date": "2024-06-14",
        "incident_time": "02:15",
        "location": "National Cooperative Bank, Cantonment Branch",
        "victim": "National Cooperative Bank",
        "suspects": ["Professional safe-cracking gang"],
        "summary": "Underground tunnel drilled into strongroom. Critical 45-minute unexplained gap between automated alarm relay and initial officer dispatch.",
        "fir": {
            "fir_number": "FIR-2024-3891",
            "ps": "Cantonment Police Station",
            "date": "2024-06-14",
            "time": "02:15",
            "complainant": "Branch Manager S. K. Nair",
            "details": "Locker room breached via subterranean tunnel from adjoining stormwater drain. Total 32 safety lockers opened.",
            "sections": "Section 457, 380 IPC / Section 331, 305 BNS"
        },
        "witnesses": [
            {
                "witness_id": "WS-1001",
                "name": "G. Manjunath (Central Monitoring Agent)",
                "statement_date": "2024-06-14",
                "claimed_time": "02:15",
                "location": "Central Alarm Command",
                "statement": "Strongroom seismic sensor triggered automated priority alarm alert at 02:15 hrs. Alert immediately relayed to police control room."
            }
        ],
        "cctv": [
            {
                "cctv_id": "CCTV-1001",
                "camera_name": "Vault Corridor Low-Light Camera",
                "timestamp": "02:18",
                "date": "2024-06-14",
                "description": "Dust plume and entry of two obscured figures from tunnel opening.",
                "relevance": "Vault breach moment"
            }
        ],
        "evidence": [
            {
                "evidence_id": "E-1001",
                "type": "Hydraulic Cutter",
                "description": "Industrial hydraulic spreader left inside tunnel cavity.",
                "recovery_location": "Drain tunnel junction",
                "recovery_time": "06:00",
                "recovery_date": "2024-06-14",
                "officer": "IO ACP Raghavendra"
            }
        ],
        "timeline": [
            {"event_id": "EVT-1001", "time": "02:15", "date": "2024-06-14", "description": "Automated seismic alarm relayed to police control.", "source": "Alarm Log"},
            {"event_id": "EVT-1002", "time": "02:18", "date": "2024-06-14", "description": "CCTV records breach in vault.", "source": "CCTV-1001"},
            {"event_id": "EVT-1003", "time": "03:00", "date": "2024-06-14", "description": "Control room dispatches first patrol vehicle to bank.", "source": "PCR Dispatch Log"},
            {"event_id": "EVT-1004", "time": "03:12", "date": "2024-06-14", "description": "Patrol vehicle reaches bank premises.", "source": "PCR Unit 9 Log"}
        ],
        "chain_of_custody": [
            {
                "evidence_id": "E-1001",
                "collected_by": "IO ACP Raghavendra",
                "collected_time": "06:00",
                "sealed_time": "06:30",
                "transferred_to": "Forensic Engineering Wing",
                "transfer_time": "08:00",
                "stored_location": "Seizure Yard Unit 1",
                "status": "Transferred"
            }
        ],
        "notes": [
            "Unexplained Timeline Gap: 45 minutes elapsed between automated alarm notification at 02:15 hrs and police dispatch at 03:00 hrs. Investigation requires explanation for dispatch delay."
        ],
        "intentional_flags": [
            "Timeline Gap: 45-minute delay between seismic alarm alert (02:15) and patrol dispatch (03:00) requires administrative review."
        ]
    }
]

def generate():
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/cases", exist_ok=True)

    with open("data/synthetic_cases.json", "w", encoding="utf-8") as f:
        json.dump(CASES, f, indent=2, ensure_ascii=False)
    print("Wrote data/synthetic_cases.json with", len(CASES), "cases.")

    for c in CASES:
        cid = c["case_id"]
        cdir = os.path.join("data", "cases", cid)
        os.makedirs(cdir, exist_ok=True)

        # Write fir.txt
        with open(os.path.join(cdir, "fir.txt"), "w", encoding="utf-8") as f:
            f.write(f"CASE ID: {c['case_id']}\n")
            f.write(f"TITLE: {c['title']}\n")
            f.write(f"CRIME TYPE: {c['crime_type']}\n")
            f.write(f"INCIDENT DATE: {c['incident_date']}\n")
            f.write(f"INCIDENT TIME: {c['incident_time']}\n")
            f.write(f"LOCATION: {c['location']}\n")
            f.write(f"VICTIM: {c['victim']}\n")
            f.write(f"SUSPECTS: {', '.join(c['suspects'])}\n")
            f.write(f"FIR NUMBER: {c['fir']['fir_number']}\n")
            f.write(f"POLICE STATION: {c['fir']['ps']}\n")
            f.write(f"SECTIONS: {c['fir']['sections']}\n\n")
            f.write(f"DETAILS:\n{c['fir']['details']}\n")

        # Write witnesses
        for w in c["witnesses"]:
            wfile = os.path.join(cdir, f"{w['witness_id'].lower()}.txt")
            with open(wfile, "w", encoding="utf-8") as f:
                f.write(f"WITNESS ID: {w['witness_id']}\n")
                f.write(f"NAME: {w['name']}\n")
                f.write(f"STATEMENT DATE: {w['statement_date']}\n")
                f.write(f"CLAIMED TIME: {w['claimed_time']}\n")
                f.write(f"LOCATION: {w['location']}\n\n")
                f.write(f"STATEMENT:\n{w['statement']}\n")

        # Write cctv
        for v in c["cctv"]:
            vfile = os.path.join(cdir, f"{v['cctv_id'].lower()}.txt")
            with open(vfile, "w", encoding="utf-8") as f:
                f.write(f"CCTV ID: {v['cctv_id']}\n")
                f.write(f"CAMERA: {v['camera_name']}\n")
                f.write(f"TIMESTAMP: {v['timestamp']}\n")
                f.write(f"DATE: {v['date']}\n\n")
                f.write(f"FOOTAGE DESCRIPTION:\n{v['description']}\n")

        # Write evidence
        for e in c["evidence"]:
            efile = os.path.join(cdir, f"{e['evidence_id'].lower().replace('-', '_')}.txt")
            with open(efile, "w", encoding="utf-8") as f:
                f.write(f"EVIDENCE ID: {e['evidence_id']}\n")
                f.write(f"TYPE: {e['type']}\n")
                f.write(f"RECOVERY LOCATION: {e['recovery_location']}\n")
                f.write(f"RECOVERY TIME: {e['recovery_time']}\n")
                f.write(f"OFFICER: {e['officer']}\n\n")
                f.write(f"DESCRIPTION:\n{e['description']}\n")

        # Write timeline
        with open(os.path.join(cdir, "timeline.txt"), "w", encoding="utf-8") as f:
            f.write(f"TIMELINE REGISTER FOR {c['case_id']}\n\n")
            for t in c["timeline"]:
                f.write(f"[{t['time']} on {t['date']}] {t['event_id']} ({t['source']}): {t['description']}\n")

        # Write chain of custody
        with open(os.path.join(cdir, "chain_of_custody.txt"), "w", encoding="utf-8") as f:
            f.write(f"CHAIN OF CUSTODY REGISTER FOR {c['case_id']}\n\n")
            for coc in c["chain_of_custody"]:
                f.write(f"EVIDENCE ID: {coc['evidence_id']}\n")
                f.write(f"COLLECTED BY: {coc['collected_by']} at {coc['collected_time']}\n")
                f.write(f"SEALED TIME: {coc.get('sealed_time', 'N/A')}\n")
                f.write(f"TRANSFERRED TO: {coc.get('transferred_to', 'N/A')} at {coc.get('transfer_time', 'N/A')}\n")
                f.write(f"STORED AT: {coc.get('stored_location', 'N/A')}\n")
                f.write(f"STATUS: {coc.get('status', 'N/A')}\n\n")

        # Write notes
        with open(os.path.join(cdir, "investigation_notes.txt"), "w", encoding="utf-8") as f:
            f.write(f"INVESTIGATION DIARY NOTES FOR {c['case_id']}\n\n")
            for n in c["notes"]:
                f.write(f"- {n}\n")

    print("All individual case files generated under data/cases/!")

if __name__ == "__main__":
    generate()
