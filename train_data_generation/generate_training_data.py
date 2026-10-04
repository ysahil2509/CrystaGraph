"""
Train Data Generation for CrystaGraph.
Converts extracted tabular knowledge and paper contexts into annotated JSON/CoNLL sequences
for training domain NER and relation extraction models.
"""

import os
import json
from typing import List, Dict, Any

def generate_relation_pairs(linked_data: List[Dict[str, Any]], output_path: str = "data/processed/relation_training_pairs.json") -> List[Dict[str, Any]]:
    """
    Generates training pairs of (Material, Property, Value) relations for supervised training.
    """
    pairs = []
    for item in linked_data:
        pairs.append({
            "head_entity": item["material_name"],
            "head_type": "MATERIAL",
            "relation": "has_property",
            "tail_entity": f"{item['property_name']}={item['value_raw']} {item['unit']}".strip(),
            "tail_type": "PROPERTY_VALUE",
            "context": f"Table '{item['caption']}' in paper {item['doi']} specifies that {item['material_name']} possesses {item['property_name']} of {item['value_raw']} {item['unit']}."
        })

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2)

    return pairs

if __name__ == "__main__":
    import sys
    print("Train data generation module ready.")
