"""
Batch extracts and serializes all scientific tables from a folder of XML research articles.
Produces structured tables with full cell mappings, captions, footnotes, and dimensions.
"""

import os
import glob
import json
import pickle
import pandas as pd
from typing import List, Dict, Any
from mit_table_extractor import MITTableExtractor

def extract_all_tables(xml_dir: str, output_dir: str = "data/tables") -> Dict[str, Any]:
    """
    Extracts all tables from all XML papers in the directory,
    saving both JSON and pickle datasets for downstream ML modeling.
    """
    extractor = MITTableExtractor()
    xml_files = sorted(glob.glob(os.path.join(xml_dir, "*.xml")))
    os.makedirs(output_dir, exist_ok=True)

    summary = {
        "total_files": len(xml_files),
        "total_tables_detected": 0,
        "successful_tables": 0,
        "failed_tables": 0,
        "papers": []
    }

    all_tables_list = []

    for xml_path in xml_files:
        filename = os.path.basename(xml_path)
        paper_id = os.path.splitext(filename)[0]
        parsed = extractor.parse_xml_file(xml_path)

        if not parsed["success"]:
            summary["papers"].append({
                "paper_id": paper_id,
                "filename": filename,
                "status": "failed",
                "error": parsed["error"],
                "tables_count": 0
            })
            continue

        meta = parsed["metadata"]
        tables = parsed["tables"]
        summary["total_tables_detected"] += len(tables)

        paper_record = {
            "paper_id": paper_id,
            "filename": filename,
            "doi": meta.get("doi", ""),
            "title": meta.get("title", ""),
            "abstract": meta.get("abstract", ""),
            "paragraphs": parsed.get("paragraphs", []),
            "status": "success",
            "tables_count": len(tables),
            "tables": []
        }

        for idx, tbl in enumerate(tables):
            summary["successful_tables"] += 1
            tbl_info = {
                "paper_id": paper_id,
                "table_index": idx + 1,
                "table_id": tbl["table_id"],
                "doi": meta.get("doi", ""),
                "caption": tbl["caption"],
                "footnote": tbl["footnote"],
                "headers": tbl["headers"],
                "num_rows": tbl["num_rows"],
                "num_cols": tbl["num_cols"],
                "raw_records": tbl["raw_dict"],
                "cleaned_records": tbl["cleaned_dict"]
            }
            paper_record["tables"].append(tbl_info)
            all_tables_list.append(tbl_info)

            # Save individual table CSV for verification
            csv_path = os.path.join(output_dir, f"{paper_id}_{tbl['table_id']}.csv")
            tbl["cleaned_df"].to_csv(csv_path, index=False)

        summary["papers"].append(paper_record)

    # Save aggregated JSON and Pickle
    json_path = os.path.join(output_dir, "extracted_tables_all.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_tables_list, f, indent=2)

    pkl_path = os.path.join(output_dir, "extracted_tables_all.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump(all_tables_list, f)

    return summary

if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "data/raw_xmls"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/tables"
    stats = extract_all_tables(src, out)
    print(f"Processed {stats['total_files']} papers, successfully extracted {stats['successful_tables']} tables.")
