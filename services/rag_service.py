import os
import json
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CaseRAGService:
    """
    Case-Isolated RAG Engine.
    Chunks case documents, maintains vector representation,
    and retrieves exact relevant source text with similarity metrics.
    """

    def __init__(self):
        self.vectorizers = {} # case_id -> TfidfVectorizer
        self.matrices = {}    # case_id -> matrix
        self.chunks_db = {}   # case_id -> List[Dict]

    def index_case(self, case_data: Dict[str, Any]):
        case_id = case_data.get("case_id", "DEFAULT")
        chunks = self._chunk_case(case_data)
        if not chunks:
            return

        corpus = [c["text"] for c in chunks]
        vectorizer = TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b\w+\b', ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(corpus)

        self.vectorizers[case_id] = vectorizer
        self.matrices[case_id] = matrix
        self.chunks_db[case_id] = chunks

    def _chunk_case(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        case_id = case_data.get("case_id", "")
        chunks = []

        # FIR chunk
        fir = case_data.get("fir", {})
        fir_text = (
            f"FIR No: {fir.get('fir_number', '')} | Police Station: {fir.get('ps', '')} | "
            f"Date: {fir.get('date', '')} {fir.get('time', '')} | Sections: {fir.get('sections', '')} | "
            f"Location: {case_data.get('location', '')} | Details: {fir.get('details', '')}"
        )
        chunks.append({
            "chunk_id": f"{case_id}-FIR",
            "case_id": case_id,
            "doc_type": "FIR",
            "title": f"FIR Record ({fir.get('fir_number', 'N/A')})",
            "text": fir_text,
            "timestamp": f"{fir.get('date', '')} {fir.get('time', '')}"
        })

        # Witness chunks
        for w in case_data.get("witnesses", []):
            w_text = (
                f"Witness ID: {w.get('witness_id')} | Name: {w.get('name')} | "
                f"Statement Date: {w.get('statement_date')} | Observed Time: {w.get('claimed_time')} | "
                f"Location: {w.get('location')} | Statement: {w.get('statement')}"
            )
            chunks.append({
                "chunk_id": f"{case_id}-{w.get('witness_id')}",
                "case_id": case_id,
                "doc_type": "Witness Statement",
                "title": f"Witness {w.get('witness_id')} ({w.get('name')})",
                "text": w_text,
                "timestamp": f"{w.get('statement_date')} {w.get('claimed_time')}"
            })

        # CCTV chunks
        for c in case_data.get("cctv", []):
            c_text = (
                f"CCTV ID: {c.get('cctv_id')} | Camera: {c.get('camera_name')} | "
                f"Timestamp: {c.get('timestamp')} | Date: {c.get('date')} | "
                f"Relevance: {c.get('relevance', '')} | Description: {c.get('description')}"
            )
            chunks.append({
                "chunk_id": f"{case_id}-{c.get('cctv_id')}",
                "case_id": case_id,
                "doc_type": "CCTV Record",
                "title": f"CCTV Footage ({c.get('camera_name')})",
                "text": c_text,
                "timestamp": f"{c.get('date')} {c.get('timestamp')}"
            })

        # Evidence chunks
        for e in case_data.get("evidence", []):
            e_text = (
                f"Evidence ID: {e.get('evidence_id')} | Type: {e.get('type')} | "
                f"Location: {e.get('recovery_location')} | Time: {e.get('recovery_time')} {e.get('recovery_date')} | "
                f"Officer: {e.get('officer')} | Description: {e.get('description')}"
            )
            chunks.append({
                "chunk_id": f"{case_id}-{e.get('evidence_id')}",
                "case_id": case_id,
                "doc_type": "Evidence Record",
                "title": f"Evidence Token ({e.get('evidence_id')} - {e.get('type')})",
                "text": e_text,
                "timestamp": f"{e.get('recovery_date')} {e.get('recovery_time')}"
            })

        # Timeline chunks
        for t in case_data.get("timeline", []):
            t_text = (
                f"Timeline Event ID: {t.get('event_id')} | Time: {t.get('time')} | Date: {t.get('date')} | "
                f"Source: {t.get('source')} | Event: {t.get('description')}"
            )
            chunks.append({
                "chunk_id": f"{case_id}-{t.get('event_id')}",
                "case_id": case_id,
                "doc_type": "Timeline Event",
                "title": f"Timeline {t.get('event_id')} ({t.get('source')})",
                "text": t_text,
                "timestamp": f"{t.get('date')} {t.get('time')}"
            })

        # Chain of custody chunks
        for coc in case_data.get("chain_of_custody", []):
            coc_text = (
                f"Chain of Custody | Evidence ID: {coc.get('evidence_id')} | "
                f"Collected By: {coc.get('collected_by')} at {coc.get('collected_time')} | "
                f"Sealed At: {coc.get('sealed_time', 'Unrecorded')} | "
                f"Transferred To: {coc.get('transferred_to', 'N/A')} at {coc.get('transfer_time', 'N/A')} | "
                f"Storage: {coc.get('stored_location', 'N/A')} | Status: {coc.get('status', 'N/A')}"
            )
            chunks.append({
                "chunk_id": f"{case_id}-COC-{coc.get('evidence_id')}",
                "case_id": case_id,
                "doc_type": "Chain of Custody",
                "title": f"Custody Transfer Register ({coc.get('evidence_id')})",
                "text": coc_text,
                "timestamp": coc.get("collected_time", "")
            })

        # Notes chunks
        for i, n in enumerate(case_data.get("notes", [])):
            chunks.append({
                "chunk_id": f"{case_id}-NOTE-{i+1}",
                "case_id": case_id,
                "doc_type": "Investigation Diary Note",
                "title": f"Investigator Note #{i+1}",
                "text": f"Investigation Diary: {n}",
                "timestamp": "N/A"
            })

        return chunks

    def retrieve(self, case_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve top_k relevant chunks strictly for the given case_id."""
        if case_id not in self.chunks_db or case_id not in self.vectorizers:
            return []

        vectorizer = self.vectorizers[case_id]
        matrix = self.matrices[case_id]
        chunks = self.chunks_db[case_id]

        try:
            query_vec = vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, matrix).flatten()
            top_indices = similarities.argsort()[::-1][:top_k]

            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score > 0.01: # only relevant matches
                    c = chunks[idx].copy()
                    c["score"] = round(score, 4)
                    results.append(c)
            return results
        except Exception:
            return []

rag_service = CaseRAGService()
