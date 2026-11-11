import json
import csv
import io
import re
from typing import Dict, Any, List

class DocumentProcessor:
    @staticmethod
    def parse_uploaded_file(filename: str, content_bytes: bytes) -> Dict[str, Any]:
        """Safely parse uploaded text, json, or csv file into case/record structure."""
        fn = filename.lower()
        try:
            text = content_bytes.decode('utf-8', errors='replace')
        except Exception:
            text = str(content_bytes)

        if fn.endswith('.json'):
            try:
                data = json.loads(text)
                return {"success": True, "type": "json", "data": data}
            except Exception as e:
                return {"success": False, "error": f"Invalid JSON file format: {str(e)}"}

        elif fn.endswith('.csv'):
            try:
                reader = csv.DictReader(io.StringIO(text))
                rows = [row for row in reader]
                return {"success": True, "type": "csv", "data": rows}
            except Exception as e:
                return {"success": False, "error": f"Invalid CSV file format: {str(e)}"}

        else: # .txt or any raw document
            # Extract basic structure heuristically
            extracted = DocumentProcessor.extract_entities_from_text(text)
            return {"success": True, "type": "txt", "raw_text": text, "extracted": extracted}

    @staticmethod
    def extract_entities_from_text(text: str) -> Dict[str, Any]:
        """Extract timestamps, evidence IDs, and key tokens from unformatted text."""
        # Times like 21:00, 8:40 PM
        times = re.findall(r'\b(?:\d{1,2}:\d{2}(?:\s*(?:AM|PM|hrs))?)\b', text, re.IGNORECASE)
        # Evidence tokens like E-001, E-104
        evidence_ids = re.findall(r'\bE[_\-\s]?(\d{1,4})\b', text, re.IGNORECASE)
        # Dates like 2024-10-12, 12-Oct-2024, 12/10/2024
        dates = re.findall(r'\b(?:\d{4}[-/]\d{2}[-/]\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b', text)

        return {
            "detected_times": list(set(times)),
            "detected_evidence_ids": [f"E-{e.zfill(3)}" for e in set(evidence_ids)],
            "detected_dates": list(set(dates)),
            "word_count": len(text.split())
        }

document_processor = DocumentProcessor()
