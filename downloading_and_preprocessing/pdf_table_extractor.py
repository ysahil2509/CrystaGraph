"""
Native PDF Table Extractor for CrystaGraph.
Extracts tabular structures, headers, and text from scientific PDF publications using pdfplumber,
multi-strategy grid detection, and heuristic tabular stream parsing.
"""

import os
import re
import pandas as pd
from typing import List, Dict, Any, Optional

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


class PDFTableExtractor:
    """
    Extracts tabular data directly from research paper PDFs with multi-strategy fallback.
    """

    def __init__(self):
        self.has_pdfplumber = pdfplumber is not None
        self.has_fitz = fitz is not None

    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extracts all tables detected across all pages of a PDF file using hybrid strategies."""
        if not os.path.exists(pdf_path):
            return [{"error": f"File not found: {pdf_path}"}]

        extracted_tables = []
        filename = os.path.basename(pdf_path)
        paper_id = os.path.splitext(filename)[0]

        if not self.has_pdfplumber:
            return [{"error": "pdfplumber is not installed on system."}]

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    page_tables = []

                    # Strategy 1: Standard Lattice Table Detection
                    raw_tables = page.extract_tables()
                    if raw_tables:
                        for t in raw_tables:
                            if t and len(t) >= 2:
                                page_tables.append((f"Table on Page {page_idx+1} of {filename}", t))

                    # Strategy 2: Text & Line Strategy for borderless/ruled tables
                    if not page_tables:
                        try:
                            tables_line = page.extract_tables(table_settings={
                                "vertical_strategy": "text",
                                "horizontal_strategy": "lines",
                                "snap_y_tolerance": 4,
                            })
                            if tables_line:
                                for t in tables_line:
                                    if t and len(t) >= 2 and any(t[0]):
                                        page_tables.append((f"Table on Page {page_idx+1} of {filename}", t))
                        except Exception:
                            pass

                    # Strategy 3: Text Stream Parser if page explicitly has "Table <num>"
                    if not page_tables and re.search(r"\b(Table|TABLE)\s+\d+", page_text):
                        lines = [l.strip() for l in page_text.splitlines() if l.strip()]
                        in_tbl = False
                        caption = ""
                        tbl_lines = []
                        for l in lines:
                            if re.match(r"^(Table|TABLE)\s+\d+", l):
                                if in_tbl and len(tbl_lines) >= 2:
                                    break
                                in_tbl = True
                                caption = l
                                tbl_lines = []
                                continue
                            if in_tbl:
                                if re.match(r"^(Fig\.|Figure|\d+\.\d+|References|\b[A-Z][a-z]+ \(\d{4}\))", l):
                                    in_tbl = False
                                    break
                                tbl_lines.append(l)

                        if tbl_lines and len(tbl_lines) >= 2:
                            hdr_raw = tbl_lines[0]
                            headers = re.split(r"\s{2,}|\t", hdr_raw)
                            if len(headers) < 2:
                                headers = hdr_raw.split()[:5]

                            rows = []
                            for r_str in tbl_lines[1:]:
                                parts = re.split(r"\s{2,}|\t", r_str)
                                if len(parts) == 1 and len(headers) > 1:
                                    parts = r_str.split()
                                rows.append(parts)

                            if rows:
                                max_c = max(len(headers), max(len(r) for r in rows))
                                hdr_padded = [headers[i] if i < len(headers) else f"Col_{i+1}" for i in range(max_c)]
                                padded_rows = []
                                for r in rows:
                                    padded = [r[i] if i < len(r) else "-" for i in range(max_c)]
                                    padded_rows.append(padded)

                                page_tables.append((caption or f"Table on Page {page_idx+1} of {filename}", [hdr_padded] + padded_rows))

                    # Process extracted tables for this page
                    for tbl_idx, (caption, raw_t) in enumerate(page_tables):
                        headers = [str(c).strip() if c else f"Col_{i+1}" for i, c in enumerate(raw_t[0])]
                        rows = []
                        for r in raw_t[1:]:
                            clean_r = [str(c).strip() if c else "-" for c in r]
                            if any(c not in ["-", "", "None"] for c in clean_r):
                                rows.append(clean_r)

                        if rows:
                            max_cols = max(len(headers), max(len(r) for r in rows))
                            headers = [headers[i] if i < len(headers) else f"Col_{i+1}" for i in range(max_cols)]
                            padded_rows = [[r[i] if i < len(r) else "-" for i in range(max_cols)] for r in rows]
                            df_cleaned = pd.DataFrame(padded_rows, columns=headers)

                            tbl_dict = df_cleaned.to_dict(orient="records")
                            extracted_tables.append({
                                "paper_id": paper_id,
                                "table_id": f"tbl_p{page_idx+1}_{tbl_idx+1}",
                                "page_number": page_idx + 1,
                                "caption": caption,
                                "footnote": "",
                                "num_rows": len(padded_rows),
                                "num_cols": max_cols,
                                "headers": headers,
                                "raw_records": tbl_dict,
                                "cleaned_records": tbl_dict,
                                "raw_dict": tbl_dict,
                                "cleaned_dict": tbl_dict,
                                "cleaned_df": df_cleaned,
                            })

        except Exception as e:
            print(f"[PDF Extractor] Error processing {pdf_path}: {e}")

        return extracted_tables


if __name__ == "__main__":
    extractor = PDFTableExtractor()
    print("PDF Table Extractor initialized. pdfplumber available:", extractor.has_pdfplumber)
