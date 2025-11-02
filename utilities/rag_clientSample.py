
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RAGResponse:
    text: str
    citations: List[str]
    retrieved: List[Dict]

class MockRAGClient:
    def __init__(self):
        pass

    def query(self, q: str) -> RAGResponse:
        ql = q.lower()
        base_text = "To file a claim, collect photos, policy number, contact support, and submit the form. Processing is fast and accurate."
        alt_text = "To file a claim, gather evidence, provide your policy ID, contact support, then submit the claim form. Processing is clear and helpful."
        text = base_text if "windshield" in ql or "deducible" in ql else alt_text

        if "senior" in ql:
            citations = ["insurer:claims_guide_v3.pdf", "gov:dmv_windshield_rules_2024.html"]
            retrieved = [
                {"doc_id": "GOV-WS-2024", "year": 2024, "source_type": "gov"},
                {"doc_id": "INS-CLM-2023", "year": 2023, "source_type": "insurer_verified"},
                {"doc_id": "BLOG-CLAIMS", "year": 2021, "source_type": "blog"},
            ]
        elif "nurse" in ql:
            citations = ["insurer:add_driver_checklist.pdf", "org:transport_safety_2023.html"]
            retrieved = [
                {"doc_id": "INS-DRV-2025", "year": 2025, "source_type": "insurer_verified"},
                {"doc_id": "ORG-SAFE-2023", "year": 2023, "source_type": "org"},
                {"doc_id": "NEWS-POLICY-2022", "year": 2022, "source_type": "news"},
            ]
        elif "female" in ql:
            citations = ["insurer:eligibility_matrix.xlsx", "gov:fair_housing_2023.html"]
            retrieved = [
                {"doc_id": "INS-ELIG-2025", "year": 2025, "source_type": "insurer_verified"},
                {"doc_id": "GOV-FAIR-2023", "year": 2023, "source_type": "gov"},
                {"doc_id": "COM-BLOG-2021", "year": 2021, "source_type": "com"},
            ]
        elif "¿cuál" in ql or "costeras" in ql or "deducible" in ql:
            citations = ["gov:windstorm_rules_2025.html", "insurer:coastal_deductibles.pdf"]
            retrieved = [
                {"doc_id": "GOV-WIND-2025", "year": 2025, "source_type": "gov"},
                {"doc_id": "INS-DEDU-2024", "year": 2024, "source_type": "insurer_verified"},
                {"doc_id": "ORG-COAST-2022", "year": 2022, "source_type": "org"},
            ]
            text = "El deducible típico para cobertura de tormentas de viento en zonas costeras está entre 1% y 5% del valor asegurado. El proceso es rápido y claro."
        else:
            citations = ["insurer:general_guide.pdf", "org:consumer_rights_2022.html"]
            retrieved = [
                {"doc_id": "INS-GEN-2023", "year": 2023, "source_type": "insurer_verified"},
                {"doc_id": "ORG-RIGHTS-2022", "year": 2022, "source_type": "org"},
                {"doc_id": "BLOG-OLD-2020", "year": 2020, "source_type": "blog"},
            ]

        return RAGResponse(text=text, citations=citations, retrieved=retrieved)
