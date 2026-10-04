"""
CrystaGraph Composition Extractor Module.
Extracts material entities, chemical components, mass/atomic/molar fractions,
and associates them with source papers and tables.
"""

import re
from typing import List, Dict, Any, Optional
from composition_rules import (
    parse_header_for_component,
    is_chemical_component,
    detect_composition_unit,
    is_numeric_value
)
from model_wrapper import MatSciBERTCompositionModel

class CompositionExtractor:
    """
    Extracts structured composition profiles from scientific tables.
    """

    def __init__(self, model_checkpoint: Optional[str] = None):
        self.model = MatSciBERTCompositionModel(model_checkpoint)

    def extract_from_table(self, table_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processes a single table dictionary to extract all composition records.
        """
        paper_id = table_dict.get("paper_id", "")
        doi = table_dict.get("doi", "")
        table_id = table_dict.get("table_id", "")
        caption = table_dict.get("caption", "")
        headers = table_dict.get("headers", [])
        records = table_dict.get("cleaned_records", [])

        if not headers or not records:
            return []

        # 1. Identify Material/Sample column (typically Col 0 or column labeled Sample/Alloy/Material)
        material_col_idx = 0
        for idx, h in enumerate(headers):
            h_low = h.lower()
            if any(k in h_low for k in ["alloy", "material", "sample", "glass", "phase", "compound", "ceramic", "cathode", "sma", "formulation"]):
                material_col_idx = idx
                break

        material_col_name = headers[material_col_idx]

        # 2. Identify composition columns
        comp_columns = {}
        caption_unit = detect_composition_unit(caption)
        
        for idx, h in enumerate(headers):
            if idx == material_col_idx:
                continue
            parsed_comp = parse_header_for_component(h)
            if parsed_comp:
                comp_name, comp_unit = parsed_comp
                # If header didn't specify unit, inherit from table caption if present
                final_unit = comp_unit if comp_unit != "%" else caption_unit
                comp_columns[h] = {
                    "component": comp_name,
                    "unit": final_unit
                }

        # If no composition columns found in headers, this table is likely not a composition table
        if not comp_columns:
            return []

        # 3. Extract compositions per row
        extracted_compositions = []

        for row in records:
            raw_mat_name = str(row.get(material_col_name, "")).strip()
            if not raw_mat_name or raw_mat_name in ["-", "--", "N/A"]:
                continue

            for col_header, comp_meta in comp_columns.items():
                val_str = str(row.get(col_header, "")).strip()
                if is_numeric_value(val_str):
                    try:
                        num_val = float(val_str)
                    except ValueError:
                        continue

                    # Filter out zero compositions if explicitly 0.0 or negligible
                    if num_val > 0.0:
                        extracted_compositions.append({
                            "paper_id": paper_id,
                            "doi": doi,
                            "table_id": table_id,
                            "material_name": raw_mat_name,
                            "component": comp_meta["component"],
                            "percentage": num_val,
                            "unit": comp_meta["unit"],
                            "confidence": 0.95
                        })

        return extracted_compositions

    def batch_extract(self, all_tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts compositions across a collection of extracted tables."""
        all_comps = []
        for tbl in all_tables:
            comps = self.extract_from_table(tbl)
            all_comps.extend(comps)
        return all_comps

if __name__ == "__main__":
    import json
    import os
    if os.path.exists("data/tables/extracted_tables_all.json"):
        with open("data/tables/extracted_tables_all.json", "r", encoding="utf-8") as f:
            tbls = json.load(f)
        extractor = CompositionExtractor()
        results = extractor.batch_extract(tbls)
        print(f"Extracted {len(results)} composition records.")
