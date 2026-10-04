"""
Extracts textual narratives, titles, abstracts, and sections from scientific XML papers.
Part of the CrystaGraph downloading and preprocessing pipeline.
"""

import os
import glob
import json
from mit_table_extractor import MITTableExtractor

def extract_text_from_xml(xml_path: str) -> dict:
    """Extracts metadata and text content from an individual XML file."""
    extractor = MITTableExtractor()
    parsed = extractor.parse_xml_file(xml_path)
    if not parsed["success"]:
        return {
            "file": os.path.basename(xml_path),
            "status": "error",
            "error": parsed.get("error", "Unknown error")
        }
    
    meta = parsed["metadata"]
    return {
        "file": os.path.basename(xml_path),
        "status": "success",
        "doi": meta.get("doi", ""),
        "pii": meta.get("pii", ""),
        "title": meta.get("title", ""),
        "abstract": meta.get("abstract", "")
    }

def batch_extract_text(xml_dir: str, output_json: str = None) -> list:
    """Batch extracts text metadata from all XML files in a directory."""
    xml_files = sorted(glob.glob(os.path.join(xml_dir, "*.xml")))
    results = []
    for fpath in xml_files:
        res = extract_text_from_xml(fpath)
        results.append(res)
    
    if output_json:
        os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    import sys
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "data/raw_xmls"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "data/processed/paper_metadata.json"
    data = batch_extract_text(src_dir, out_file)
    print(f"Extracted metadata for {len(data)} papers.")
