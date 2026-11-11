import os
import shutil
import json
import sqlite3
import random
from PIL import Image, ImageDraw, ImageFont

STATIC_CCTV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "cctv")
os.makedirs(STATIC_CCTV, exist_ok=True)

# High-res photorealistic AI CCTV images generated earlier
HIGH_RES_MAP = {
    ("CASE-001", "CCTV-001"): "cctv_stairwell_1792259647212.jpg",
    ("CASE-001", "CCTV-002"): "cctv_lobby_1792259678571.jpg",
    ("CASE-002", "CCTV-101"): "cctv_perimeter_1792259705214.jpg",
    ("CASE-004", "CCTV-401"): "cctv_showroom_1792259738253.jpg",
    ("CASE-008", "CCTV-801"): "cctv_alleyway_1792259778315.jpg",
    ("CASE-010", "CCTV-1001"): "cctv_vault_1792259810304.jpg"
}

def generate_scene_image(output_path, camera_name, timestamp, date, scene_type="hallway"):
    w, h = 960, 540
    img = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(img)

    if scene_type == "hallway": # Murder apartment corridor
        for y in range(h):
            val = int(12 + (y/h) * 35)
            draw.line([(0, y), (w, y)], fill=(val, val + 2, val + 8))
        # Floor perspective lines
        for x in range(0, w, 50):
            draw.line([(x, h), (w*0.5 + (x - w*0.5)*0.15, h*0.48)], fill=(40, 48, 60), width=1)
        # Corridor walls & Flat 402 doorway
        draw.rectangle([w*0.38, h*0.28, w*0.62, h*0.75], outline=(60, 70, 85), width=2)
        draw.rectangle([w*0.44, h*0.34, w*0.56, h*0.75], fill=(22, 28, 38), outline=(80, 95, 115), width=2)
        # Door number plate
        draw.rectangle([w*0.48, h*0.4, w*0.52, h*0.44], fill=(180, 160, 50))
        # Police crime scene cordon line simulation
        draw.line([w*0.3, h*0.65, w*0.7, h*0.65], fill=(220, 200, 30), width=4)

    elif scene_type == "parking": # Basement parking
        for y in range(h):
            val = int(8 + (y/h) * 24)
            draw.line([(0, y), (w, y)], fill=(val, val + 4, val + 6))
        # Concrete pillars
        for px in [w*0.15, w*0.5, w*0.82]:
            draw.rectangle([px, h*0.1, px + 50, h*0.88], fill=(24, 30, 38), outline=(50, 60, 75), width=2)
            # Yellow hazard stripe on pillar
            draw.rectangle([px, h*0.45, px + 50, h*0.55], fill=(190, 160, 20))
        # Parking lane line
        draw.line([w*0.25, h, w*0.4, h*0.5], fill=(160, 150, 30), width=3)
        draw.line([w*0.75, h, w*0.6, h*0.5], fill=(160, 150, 30), width=3)

    elif scene_type == "driveway": # Estate iron gate
        for y in range(h):
            val = int(10 + (y/h) * 22)
            draw.line([(0, y), (w, y)], fill=(val + 2, val + 8, val)) # Slight IR green
        # Stone gate posts
        draw.rectangle([w*0.2, h*0.2, w*0.32, h*0.85], fill=(30, 42, 35), outline=(55, 75, 60), width=2)
        draw.rectangle([w*0.68, h*0.2, w*0.8, h*0.85], fill=(30, 42, 35), outline=(55, 75, 60), width=2)
        # Iron gate bars
        for bx in range(int(w*0.32), int(w*0.68), 16):
            draw.line([(bx, h*0.3), (bx, h*0.85)], fill=(70, 90, 75), width=2)

    elif scene_type == "loading_bay": # Industrial bay
        for y in range(h):
            val = int(15 + (y/h) * 28)
            draw.line([(0, y), (w, y)], fill=(val, val + 2, val + 6))
        # Roll-up door
        draw.rectangle([w*0.2, h*0.2, w*0.8, h*0.85], fill=(28, 34, 42), outline=(60, 70, 80), width=2)
        for ry in range(int(h*0.22), int(h*0.85), 24):
            draw.line([(w*0.2, ry), (w*0.8, ry)], fill=(45, 52, 62), width=1)
        # Pallet stack
        draw.rectangle([w*0.7, h*0.65, w*0.88, h*0.85], fill=(60, 50, 35), outline=(85, 70, 50))

    elif scene_type == "street_booth": # Payphone booth
        for y in range(h):
            val = int(10 + (y/h) * 25)
            draw.line([(0, y), (w, y)], fill=(val, val, val + 4))
        # Sidewalk
        draw.line([(0, h*0.75), (w, h*0.75)], fill=(70, 75, 80), width=2)
        # Glass telephone booth
        draw.rectangle([w*0.4, h*0.22, w*0.6, h*0.82], outline=(100, 130, 160), width=3)
        draw.rectangle([w*0.45, h*0.35, w*0.55, h*0.55], fill=(35, 50, 65), outline=(120, 150, 180))

    elif scene_type == "server": # Datacenter
        for y in range(h):
            val = int(6 + (y/h) * 20)
            draw.line([(0, y), (w, y)], fill=(int(val*0.6), val, int(val*0.8))) # Green tint
        for rx in [w*0.12, w*0.38, w*0.64, w*0.88]:
            draw.rectangle([rx, h*0.15, rx + w*0.18, h*0.88], fill=(12, 22, 16), outline=(35, 65, 45), width=2)
            for ly in range(int(h*0.22), int(h*0.82), 18):
                draw.ellipse([rx + 8, ly, rx + 14, ly + 6], fill=(0, 255, 100))
                if random.random() > 0.5:
                    draw.ellipse([rx + 20, ly, rx + 26, ly + 6], fill=(0, 180, 255))
    else: # Default commercial corridor
        for y in range(h):
            val = int(14 + (y/h) * 30)
            draw.line([(0, y), (w, y)], fill=(val, val + 3, val + 7))
        draw.rectangle([w*0.2, h*0.25, w*0.8, h*0.8], outline=(55, 65, 78), width=2)

    # Scanlines
    for y in range(0, h, 3):
        draw.line([(0, y), (w, y)], fill=(0, 0, 0), width=1)

    # HUD Overlay Top & Bottom Bars
    draw.rectangle([0, 0, w, 44], fill=(0, 0, 0, 220))
    draw.rectangle([0, h - 36, w, h], fill=(0, 0, 0, 200))

    # Red recording dot
    draw.ellipse([20, 14, 34, 28], fill=(230, 40, 40))
    cam_str = f"[{camera_name.upper()}]  ● REC  1080P/30FPS"
    time_str = f"{date}  {timestamp}:15"
    footer_str = "SURVEILLANCE EVIDENCE STREAM // ENCRYPTED PROPERTY STORAGE CH-04"

    draw.text((44, 14), cam_str, fill=(255, 255, 255))
    draw.text((w - 240, 14), time_str, fill=(255, 255, 255))
    draw.text((20, h - 26), footer_str, fill=(180, 195, 210))
    draw.text((w - 180, h - 26), "LOSSLESS RECORD", fill=(52, 211, 153))

    # Corner brackets
    cs = 20
    draw.line([(30, 60), (30 + cs, 60)], fill=(255, 255, 255), width=2)
    draw.line([(30, 60), (30, 60 + cs)], fill=(255, 255, 255), width=2)
    draw.line([(w - 30, 60), (w - 30 - cs, 60)], fill=(255, 255, 255), width=2)
    draw.line([(w - 30, 60), (w - 30, 60 + cs)], fill=(255, 255, 255), width=2)
    draw.line([(30, h - 50), (30 + cs, h - 50)], fill=(255, 255, 255), width=2)
    draw.line([(30, h - 50), (30, h - 50 - cs)], fill=(255, 255, 255), width=2)
    draw.line([(w - 30, h - 50), (w - 30 - cs, h - 50)], fill=(255, 255, 255), width=2)
    draw.line([(w - 30, h - 50), (w - 30, h - 50 - cs)], fill=(255, 255, 255), width=2)

    img.save(output_path, "JPEG", quality=90)
    print(f"Generated CCTV image: {output_path}")

# Complete multi-camera mapping across all cases
CASES_CCTV_CONFIG = {
    "CASE-001": [
        {
            "cctv_id": "CCTV-001",
            "camera_name": "Main Stairwell North Camera (CAM-04)",
            "timestamp": "20:40",
            "date": "2024-10-12",
            "scene": "stairwell",
            "description": "Footage shows a tall individual in dark hooded clothing exiting the 4th floor stairwell and leaving the camera frame towards the rear exit at 20:40 hrs.",
            "relevance": "Key departure timeline conflict record (conflicts with 21:10 witness claim)"
        },
        {
            "cctv_id": "CCTV-002",
            "camera_name": "Ground Floor Lobby Camera (CAM-01)",
            "timestamp": "20:28",
            "date": "2024-10-12",
            "scene": "lobby",
            "description": "Footage captures guest arrival at lobby entry glass doors at 20:28 hrs wearing black backpack.",
            "relevance": "Premises entry verification"
        },
        {
            "cctv_id": "CCTV-003",
            "camera_name": "4th Floor Corridor North (CAM-07)",
            "timestamp": "20:35",
            "date": "2024-10-12",
            "scene": "hallway",
            "description": "Surveillance sensor captures movement outside Flat 402 door entrance. Knocker touched at 20:35 hrs.",
            "relevance": "Direct scene corridor approach"
        },
        {
            "cctv_id": "CCTV-004",
            "camera_name": "Basement Parking Ramp Exit (CAM-02)",
            "timestamp": "20:46",
            "date": "2024-10-12",
            "scene": "parking",
            "description": "Dark grey sedan accelerates out of basement parking ramp towards Sector 14 arterial road at 20:46 hrs.",
            "relevance": "Vehicle departure window"
        }
    ],
    "CASE-002": [
        {
            "cctv_id": "CCTV-101",
            "camera_name": "Perimeter Wall South Camera (CAM-02)",
            "timestamp": "23:45",
            "date": "2024-11-04",
            "scene": "perimeter",
            "description": "Night vision feed shows shadowy silhouette scaling the perimeter brick wall near the drainage canal.",
            "relevance": "Exterior entry point near recovered evidence E-104 location"
        },
        {
            "cctv_id": "CCTV-102",
            "camera_name": "Estate Driveway Main Gate (CAM-01)",
            "timestamp": "22:15",
            "date": "2024-11-04",
            "scene": "driveway",
            "description": "Infrared footage records security guard patrolling past main ornamental iron gates at 22:15 hrs.",
            "relevance": "Guard patrol route verification"
        },
        {
            "cctv_id": "CCTV-103",
            "camera_name": "Rear Garden Pathway & Drainage Cordon (CAM-03)",
            "timestamp": "23:52",
            "date": "2024-11-04",
            "scene": "perimeter",
            "description": "Infrared night capture records figure running along wet grass verge toward drainage canal dropping an unverified object.",
            "relevance": "Direct vicinity of recovered evidence token E-104 (drainage canal)"
        },
        {
            "cctv_id": "CCTV-104",
            "camera_name": "Estate North Entrance Porch (CAM-04)",
            "timestamp": "23:30",
            "date": "2024-11-04",
            "scene": "driveway",
            "description": "Illuminated porch camera captures entry through unlocked French patio doors prior to bedroom disturbance.",
            "relevance": "Point of unlawful ingress into victim residence"
        }
    ],
    "CASE-003": [
        {
            "cctv_id": "CCTV-301",
            "camera_name": "Weighbridge Automated Camera (CAM-03)",
            "timestamp": "19:10",
            "date": "2024-09-18",
            "scene": "industrial",
            "description": "Automated security boom gate logs registration plate HR-26-8812 crossing weighbridge at 19:10 hrs.",
            "relevance": "Industrial corridor traffic record"
        },
        {
            "cctv_id": "CCTV-302",
            "camera_name": "Warehouse Loading Bay 4 (CAM-06)",
            "timestamp": "19:18",
            "date": "2024-09-18",
            "scene": "loading_bay",
            "description": "Loading bay camera captures forklift driver completing shipment sign-off without disruption.",
            "relevance": "Corroborated incident baseline"
        }
    ],
    "CASE-004": [
        {
            "cctv_id": "CCTV-401",
            "camera_name": "Overhead Showroom Cam 1 (CAM-01)",
            "timestamp": "14:15",
            "date": "2024-08-22",
            "scene": "showroom",
            "description": "Overhead high-contrast monochrome feed records armed intruder demanding tray of diamond necklaces at counter.",
            "relevance": "Primary robbery occurrence"
        },
        {
            "cctv_id": "CCTV-402",
            "camera_name": "Showroom Rear Alley Exit (CAM-03)",
            "timestamp": "14:22",
            "date": "2024-08-22",
            "scene": "hallway",
            "description": "Perpetrator bursts through rear service emergency door carrying black duffel bag.",
            "relevance": "Escape transit log"
        }
    ],
    "CASE-005": [
        {
            "cctv_id": "CCTV-501",
            "camera_name": "North Gate Mall Cam 6 (CAM-06)",
            "timestamp": "17:25",
            "date": "2024-10-01",
            "scene": "mall",
            "description": "Mall atrium camera captures minor accompanied by adult wearing beige trench coat towards East exit.",
            "relevance": "Primary abduction tracking log"
        },
        {
            "cctv_id": "CCTV-502",
            "camera_name": "Underground P2 Parking Booth (CAM-04)",
            "timestamp": "17:34",
            "date": "2024-10-01",
            "scene": "parking",
            "description": "Vehicle with tinted glass passes parking exit barrier booth paying cash.",
            "relevance": "Suspect vehicle egress verification"
        }
    ],
    "CASE-006": [
        {
            "cctv_id": "CCTV-601",
            "camera_name": "Datacenter Server Rack Cam 3 (CAM-03)",
            "timestamp": "11:38",
            "date": "2024-11-15",
            "scene": "server",
            "description": "Low-light green illumination feed shows authorized system admin badge swipe at console 4 prior to transfer.",
            "relevance": "Direct physical terminal access check"
        },
        {
            "cctv_id": "CCTV-602",
            "camera_name": "Corporate 12th Floor Executive Suite (CAM-07)",
            "timestamp": "11:42",
            "date": "2024-11-15",
            "scene": "hallway",
            "description": "Hallway camera confirms CFO was in executive boardroom meeting when wire transfer dispatch was executed.",
            "relevance": "Alibi verification for wire transfer authorization"
        }
    ],
    "CASE-007": [
        {
            "cctv_id": "CCTV-701",
            "camera_name": "Exterior Entrance 4K Camera (CAM-01)",
            "timestamp": "22:15",
            "date": "2024-10-25",
            "scene": "driveway",
            "description": "Storefront wide-angle lens captures shattered glass door and two individuals hauling electronics cartons.",
            "relevance": "Burglary break-in timestamp"
        },
        {
            "cctv_id": "CCTV-702",
            "camera_name": "Store Display Floor Zone B (CAM-04)",
            "timestamp": "22:18",
            "date": "2024-10-25",
            "scene": "hallway",
            "description": "Camera records clearing of Apple/Samsung mobile phone display counter into tote containers.",
            "relevance": "Cataloged stolen inventory corroboration"
        }
    ],
    "CASE-008": [
        {
            "cctv_id": "CCTV-801",
            "camera_name": "Alleyway Security Camera (CAM-08)",
            "timestamp": "01:10",
            "date": "2024-11-20",
            "scene": "alleyway",
            "description": "Narrow brick alleyway night vision feed records physical altercation and hooded figure running towards main street.",
            "relevance": "Assault scene direct capture"
        },
        {
            "cctv_id": "CCTV-802",
            "camera_name": "Club Emergency Exit Door (CAM-02)",
            "timestamp": "01:04",
            "date": "2024-11-20",
            "scene": "hallway",
            "description": "Victim and two unidentified patrons exit club into alleyway through emergency double doors.",
            "relevance": "Departure pre-altercation log"
        }
    ],
    "CASE-009": [
        {
            "cctv_id": "CCTV-901",
            "camera_name": "Metro Station Payphone Booth (CAM-05)",
            "timestamp": "15:58",
            "date": "2024-12-02",
            "scene": "street_booth",
            "description": "Street surveillance dome records person wearing baseball cap utilizing public coin payphone at 15:58 hrs.",
            "relevance": "Extortion call origination point"
        },
        {
            "cctv_id": "CCTV-902",
            "camera_name": "Public Park North Gate Fountain (CAM-03)",
            "timestamp": "16:20",
            "date": "2024-12-02",
            "scene": "parking",
            "description": "CCTV monitors proposed cash drop bench; no parcel deposited.",
            "relevance": "Drop location stakeout observation"
        }
    ],
    "CASE-010": [
        {
            "cctv_id": "CCTV-1001",
            "camera_name": "Vault Corridor Low-Light Camera (CAM-10)",
            "timestamp": "02:40",
            "date": "2024-12-10",
            "scene": "vault",
            "description": "Sub-basement vault corridor camera captures laser tripwire bypass and door mechanism breach attempt at 02:40 hrs.",
            "relevance": "Direct vault infiltration record"
        },
        {
            "cctv_id": "CCTV-1002",
            "camera_name": "Bank Main Banking Hall Dome (CAM-02)",
            "timestamp": "02:25",
            "date": "2024-12-10",
            "scene": "lobby",
            "description": "Ceiling dome records ventilation duct grating being removed above teller counter #3.",
            "relevance": "Initial facility entry breach"
        }
    ]
}

def setup_all_cctv():
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic_cases.json")
    with open(json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    case_dict = {c["case_id"]: c for c in cases}

    for cid, cctv_list in CASES_CCTV_CONFIG.items():
        if cid in case_dict:
            target_cctvs = []
            for c in cctv_list:
                c_id = c["cctv_id"]
                cam_name = c["camera_name"]
                t_stamp = c["timestamp"]
                d_str = c["date"]
                scene = c.get("scene", "hallway")
                target_filename = f"cctv_{cid}_{c_id}.jpg"
                target_path = os.path.join(STATIC_CCTV, target_filename)

                # Check if we have high-res AI image for this camera
                if (cid, c_id) in HIGH_RES_MAP:
                    src_file = os.path.join(STATIC_CCTV, HIGH_RES_MAP[(cid, c_id)])
                    if os.path.exists(src_file):
                        shutil.copy(src_file, target_path)
                        print(f"Used High-Res image for {cid} {c_id}")

                if not os.path.exists(target_path):
                    generate_scene_image(target_path, cam_name, t_stamp, d_str, scene)

                target_cctvs.append({
                    "cctv_id": c_id,
                    "camera_name": cam_name,
                    "timestamp": t_stamp,
                    "date": d_str,
                    "image_url": f"/static/cctv/{target_filename}",
                    "description": c["description"],
                    "relevance": c.get("relevance", "Surveillance record")
                })
            case_dict[cid]["cctv"] = target_cctvs

    # Save synthetic_cases.json
    updated_cases = list(case_dict.values())
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(updated_cases, f, indent=2)
    print("Updated synthetic_cases.json with full multi-camera coverage for ALL 10 cases.")

    # Update SQLite database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "investigation_auditor.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        for case in updated_cases:
            cid = case["case_id"]
            cur.execute("SELECT data_json FROM cases WHERE case_id = ?", (cid,))
            row = cur.fetchone()
            if row:
                existing = json.loads(row[0])
                existing["cctv"] = case.get("cctv", [])
                cur.execute("UPDATE cases SET data_json = ? WHERE case_id = ?", (json.dumps(existing), cid))
        conn.commit()
        conn.close()
        print("Updated SQLite database successfully.")

if __name__ == "__main__":
    setup_all_cctv()
