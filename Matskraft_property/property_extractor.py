"""
CrystaGraph Property Extractor Module.
Identifies physical, mechanical, thermal, and electrical property records from scientific tables.
"""

import re
from typing import List, Dict, Any, Optional
from property_vocab import canonicalize_property, get_property_category
from unit_normalizer import extract_unit_from_text
from si_units import convert_to_si

class PropertyExtractor:
    """
    Extracts structured property values, units, and conditions from scientific tables.
    """

    def __init__(self):
        pass

    def extract_from_table(self, table_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts all property records from an individual table dictionary.
        """
        paper_id = table_dict.get("paper_id", "")
        doi = table_dict.get("doi", "")
        table_id = table_dict.get("table_id", "")
        caption = table_dict.get("caption", "")
        footnote = table_dict.get("footnote", "")
        headers = table_dict.get("headers", [])
        records = table_dict.get("cleaned_records", [])

        if not headers or not records:
            return []

        # 1. Identify Material/Sample column
        material_col_idx = 0
        for idx, h in enumerate(headers):
            h_low = h.lower()
            if any(k in h_low for k in ["alloy", "material", "sample", "glass", "phase", "compound", "ceramic", "cathode", "sma", "formulation", "specification"]):
                material_col_idx = idx
                break

        material_col_name = headers[material_col_idx]

        # 2. Identify Property Columns
        prop_columns = {}
        for idx, h in enumerate(headers):
            if idx == material_col_idx:
                continue

            canonical = canonicalize_property(h)
            if canonical:
                unit = extract_unit_from_text(h) or ""
                category = get_property_category(canonical)
                prop_columns[h] = {
                    "canonical_name": canonical,
                    "unit": unit,
                    "category": category
                }

        if not prop_columns:
            return []

        # 3. Extract properties per row
        extracted_properties = []

        for row in records:
            raw_mat_name = str(row.get(material_col_name, "")).strip()
            if not raw_mat_name or raw_mat_name in ["-", "--", "N/A"]:
                continue

            for col_header, prop_meta in prop_columns.items():
                val_str = str(row.get(col_header, "")).strip()
                if val_str in ["-", "--", "N/A", "n/a", "nil", "none", ""]:
                    continue

                # Parse numerical value
                clean_num_str = re.sub(r'[^\d\.\-\+eE]', '', val_str)
                try:
                    num_val = float(clean_num_str) if clean_num_str else None
                except ValueError:
                    num_val = None

                si_info = convert_to_si(num_val, prop_meta["unit"], prop_meta["canonical_name"])

                extracted_properties.append({
                    "paper_id": paper_id,
                    "doi": doi,
                    "table_id": table_id,
                    "material_name": raw_mat_name,
                    "property_name": prop_meta["canonical_name"],
                    "raw_property_header": col_header,
                    "property_category": prop_meta["category"],
                    "value_raw": val_str,
                    "value_numeric": num_val,
                    "unit": prop_meta["unit"],
                    "si_value": si_info["si_value"],
                    "si_unit": si_info["si_unit"],
                    "si_formatted": si_info["si_formatted"],
                    "source_type": "Table",
                    "caption": caption,
                    "condition_footnote": footnote,
                    "confidence": 0.96
                })

        return extracted_properties

    def batch_extract(self, all_tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts property records across a collection of extracted tables."""
        all_props = []
        for tbl in all_tables:
            props = self.extract_from_table(tbl)
            all_props.extend(props)
        return all_props

if __name__ == "__main__":
    import json
    import os
    if os.path.exists("data/tables/extracted_tables_all.json"):
        with open("data/tables/extracted_tables_all.json", "r", encoding="utf-8") as f:
            tbls = json.load(f)
        extractor = PropertyExtractor()
        results = extractor.batch_extract(tbls)
        print(f"Extracted {len(results)} property records.")
