"""
Composition-Property Linker for CrystaGraph.
Associates material entities with their chemical composition profiles and experimental properties
across intra-table rows and cross-table references within scientific research papers.
"""

from typing import List, Dict, Any
import re
from collections import defaultdict

class KnowledgeLinker:
    """
    Links isolated material, composition, and property extractions into cohesive knowledge records.
    """

    def __init__(self):
        pass

    @staticmethod
    def normalize_material_key(name: str) -> str:
        """Normalizes material names for robust fuzzy/sub-match linking across tables."""
        # e.g. "Ti-6Al-4V (Grade 5)" -> "ti-6al-4v"
        clean = name.lower()
        clean = re.sub(r'\(.*?\)', '', clean) # Remove parenthesized aliases
        clean = re.sub(r'[^a-z0-9]', '', clean)
        return clean

    def link_extractions(
        self,
        compositions: List[Dict[str, Any]],
        properties: List[Dict[str, Any]],
        tables: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merges composition records and property records by matching paper_id and material entities.
        """
        # 1. Group compositions by (paper_id, normalized_material)
        comp_map = defaultdict(lambda: {"components": {}, "raw_names": set(), "units": set(), "doi": "", "table_ids": set()})

        for c in compositions:
            paper_id = c["paper_id"]
            mat_raw = c["material_name"]
            mat_norm = self.normalize_material_key(mat_raw)
            key = (paper_id, mat_norm)

            comp_map[key]["raw_names"].add(mat_raw)
            comp_map[key]["components"][c["component"]] = {
                "percentage": c["percentage"],
                "unit": c["unit"]
            }
            comp_map[key]["doi"] = c.get("doi", "")
            comp_map[key]["table_ids"].add(c.get("table_id", ""))

        # 2. Link properties with composition profiles
        linked_knowledge = []
        record_id = 1

        for p in properties:
            paper_id = p["paper_id"]
            mat_raw = p["material_name"]
            mat_norm = self.normalize_material_key(mat_raw)
            key = (paper_id, mat_norm)

            # Find matching composition profile
            comp_data = comp_map.get(key)
            if not comp_data:
                # Try finding closest match in the same paper
                for (p_id, m_norm), c_val in comp_map.items():
                    if p_id == paper_id and (m_norm in mat_norm or mat_norm in m_norm):
                        comp_data = c_val
                        break

            components_dict = comp_data["components"] if comp_data else {}
            comp_summary = ", ".join([f"{k}: {v['percentage']}{v['unit']}" for k, v in components_dict.items()]) if components_dict else "Not explicitly tabulated"

            linked_knowledge.append({
                "record_id": record_id,
                "paper_id": paper_id,
                "doi": p.get("doi", ""),
                "table_id": p.get("table_id", ""),
                "material_name": mat_raw,
                "normalized_material": mat_norm,
                "composition_dict": components_dict,
                "composition_summary": comp_summary,
                "property_name": p["property_name"],
                "property_category": p.get("property_category", "General"),
                "value_numeric": p.get("value_numeric"),
                "value_raw": p.get("value_raw", ""),
                "unit": p.get("unit", ""),
                "si_value": p.get("si_value"),
                "si_unit": p.get("si_unit", ""),
                "source_type": p.get("source_type", "table"),
                "condition": p.get("condition_footnote", ""),
                "caption": p.get("caption", "")
            })
            record_id += 1

        return linked_knowledge
