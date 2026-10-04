"""
Master Pipeline Execution Script for CrystaGraph.
Runs the complete multi-paper table extraction, composition extraction, property mining,
composition-property linking, evaluation metric calculation, and database ingestion.
"""

import os
import sys
import time
import json
import argparse

# Add relevant directories to python path for modular import
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "downloading_and_preprocessing"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Matskraft_composition"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Matskraft_property"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Linking_the_extracted_info_and_final_evaluation"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "train_data_generation"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

from get_table_from_xmls import extract_all_tables
from create_train_val_test_data import create_dataset_splits
from composition_extractor import CompositionExtractor
from property_extractor import PropertyExtractor
from text_property_extractor import TextPropertyExtractor
from linker import KnowledgeLinker
from evaluator import PipelineEvaluator
from generate_training_data import generate_relation_pairs
from build_database import populate_database

def run_pipeline(
    xml_dir: str = "data/raw_xmls",
    tables_dir: str = "data/tables",
    extracted_dir: str = "data/extracted",
    processed_dir: str = "data/processed",
    db_path: str = "data/database/matgraph.db"
) -> dict:
    """Executes the complete CrystaGraph materials informatics pipeline."""
    print("=" * 70)
    print("🚀 STARTING CRYSTA GRAPH KNOWLEDGE MINING PIPELINE")
    print("=" * 70)
    start_time = time.time()

    # Step 1: Scientific XML Table Extraction
    print("\n[Step 1/6] Extracting scientific tables from XML research papers...")
    t0 = time.time()
    papers_summary = extract_all_tables(xml_dir, tables_dir)
    t_tables = time.time() - t0
    print(f" -> Processed {papers_summary['total_files']} XML papers.")
    print(f" -> Extracted {papers_summary['successful_tables']} tables across all documents in {t_tables:.2f}s.")

    # Load aggregated extracted tables
    tables_json_path = os.path.join(tables_dir, "extracted_tables_all.json")
    with open(tables_json_path, "r", encoding="utf-8") as f:
        all_tables = json.load(f)

    # Step 2: Machine Learning Dataset Generation & Splits
    print("\n[Step 2/6] Generating MatSciBERT train/val/test tokenized splits...")
    splits_info = create_dataset_splits(tables_json_path, processed_dir)
    print(f" -> Splits created: {splits_info}")

    # Step 3: Material & Composition Extraction
    print("\n[Step 3/6] Extracting material compositions (wt%, at%, mol%)...")
    comp_extractor = CompositionExtractor()
    extracted_compositions = comp_extractor.batch_extract(all_tables)
    os.makedirs(extracted_dir, exist_ok=True)
    with open(os.path.join(extracted_dir, "extracted_compositions.json"), "w", encoding="utf-8") as f:
        json.dump(extracted_compositions, f, indent=2)
    print(f" -> Extracted {len(extracted_compositions)} composition records.")

    # Step 4: Material Property Extraction & Unit Normalization (Tables + Narrative Prose)
    print("\n[Step 4/6] Extracting material properties, values, and units (Tables + Narrative Prose)...")
    prop_extractor = PropertyExtractor()
    table_properties = prop_extractor.batch_extract(all_tables)
    print(f" -> Extracted {len(table_properties)} property measurements from scientific tables.")

    # Narrative Text Extraction (Extracts properties from abstracts, text paragraphs, and papers without tables)
    text_extractor = TextPropertyExtractor()
    text_properties = text_extractor.batch_extract_from_papers(papers_summary["papers"])
    print(f" -> Extracted {len(text_properties)} property measurements from narrative paper text.")

    extracted_properties = table_properties + text_properties
    with open(os.path.join(extracted_dir, "extracted_properties.json"), "w", encoding="utf-8") as f:
        json.dump(extracted_properties, f, indent=2)
    print(f" -> Total unified properties extracted: {len(extracted_properties)} records.")

    # Step 5: Composition-Property Knowledge Linking
    print("\n[Step 5/6] Associating materials, compositions, and properties into knowledge triples...")
    linker = KnowledgeLinker()
    linked_knowledge = linker.link_extractions(extracted_compositions, extracted_properties, all_tables)
    with open(os.path.join(extracted_dir, "extracted_knowledge.json"), "w", encoding="utf-8") as f:
        json.dump(linked_knowledge, f, indent=2)
    
    # Generate relation pairs for training
    generate_relation_pairs(linked_knowledge, os.path.join(processed_dir, "relation_training_pairs.json"))
    print(f" -> Created {len(linked_knowledge)} linked material knowledge tuples.")

    # Step 6: Evaluation & Relational SQLite Database Ingestion
    total_elapsed = time.time() - start_time
    print("\n[Step 6/6] Calculating genuine metrics and populating SQLite database...")
    evaluator = PipelineEvaluator()
    eval_results = evaluator.evaluate_extraction_pipeline(
        papers_summary,
        extracted_compositions,
        extracted_properties,
        linked_knowledge,
        total_elapsed
    )

    # Save metrics JSON
    with open(os.path.join(processed_dir, "pipeline_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(eval_results["summary_metrics"], f, indent=2)

    # Populate database
    populate_database(
        papers_summary["papers"],
        all_tables,
        extracted_compositions,
        extracted_properties,
        linked_knowledge,
        eval_results,
        db_path
    )

    print("\n" + "=" * 70)
    print("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n--- Summary Performance Metrics (Genuine Execution) ---")
    for k, v in eval_results["summary_metrics"].items():
        print(f"  • {k:<40}: {v}")
    print("\n--- Per-Paper Summary Table ---")
    print(eval_results["per_paper_table"].to_string(index=False))
    print("=" * 70)

    return eval_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CrystaGraph Knowledge Mining Pipeline")
    parser.add_argument("--xml_dir", default="data/raw_xmls", help="Directory containing raw XML papers")
    parser.add_argument("--tables_dir", default="data/tables", help="Directory to save extracted tables")
    parser.add_argument("--extracted_dir", default="data/extracted", help="Directory to save extraction JSONs")
    parser.add_argument("--processed_dir", default="data/processed", help="Directory to save splits and metrics")
    parser.add_argument("--db_path", default="data/database/matgraph.db", help="Path to SQLite database")

    args = parser.parse_args()
    run_pipeline(
        xml_dir=args.xml_dir,
        tables_dir=args.tables_dir,
        extracted_dir=args.extracted_dir,
        processed_dir=args.processed_dir,
        db_path=args.db_path
    )
