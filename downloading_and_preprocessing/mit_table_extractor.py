"""
MIT Table Extractor Module for CrystaGraph.
Parses scientific research tables from Elsevier / JATS / TEI XML formats,
normalizing cell structures, headers, spans, captions, and footnotes.
"""

import xml.etree.ElementTree as ET
import pandas as pd
import re
import unicodedata
from typing import List, Dict, Any, Optional

class MITTableExtractor:
    """
    Extracts and standardizes tabular data from scientific XML articles.
    Preserves chemical formulas, units, scientific notations, and table hierarchy.
    """

    def __init__(self):
        # Namespaces commonly used in Elsevier and JATS XMLs
        self.namespaces = {
            'ce': 'http://www.elsevier.com/xml/common/dtd',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Normalizes Unicode characters, whitespace, and special scientific symbols."""
        if not text:
            return ""
        # Preserve specific unicode symbols but normalize redundant spacing
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_element_text(self, elem: Optional[ET.Element]) -> str:
        """Recursively extracts all text content from an XML element, ignoring nested tags."""
        if elem is None:
            return ""
        text_parts = []
        for s in elem.itertext():
            if s:
                text_parts.append(s)
        return self.clean_text(" ".join(text_parts))

    def parse_xml_file(self, xml_path: str) -> Dict[str, Any]:
        """
        Parses an XML file and extracts paper metadata along with all embedded tables.
        Includes automatic sanitization for malformed entities like unescaped ampersands.
        """
        try:
            with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            # Sanitize unescaped ampersands
            sanitized = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', '&amp;', content)
            root = ET.fromstring(sanitized)
        except Exception as e:
            return {
                "success": False,
                "error": f"XML Parse Error: {str(e)}",
                "tables": [],
                "metadata": {}
            }

        # Extract paper metadata
        metadata = self._extract_metadata(root)
        
        # Extract tables
        tables = self._extract_tables(root, metadata)

        # Extract narrative paragraphs (sections, discussion, experimental)
        paragraphs = self._extract_paragraphs(root)

        return {
            "success": True,
            "metadata": metadata,
            "tables": tables,
            "table_count": len(tables),
            "paragraphs": paragraphs
        }

    def _extract_metadata(self, root: ET.Element) -> Dict[str, str]:
        """Extracts DOI, PII, Title, and Abstract from the root XML element."""
        metadata = {
            "doi": "",
            "pii": "",
            "title": "",
            "abstract": ""
        }

        # 1. DOI
        for tag in ['.//ce:doi', './/doi', './/article-id[@pub-id-type="doi"]']:
            node = root.find(tag, self.namespaces) if 'ce:' in tag else root.find(tag)
            if node is not None and node.text:
                metadata["doi"] = self.clean_text(node.text)
                break

        # 2. PII
        for tag in ['.//ce:pii', './/pii']:
            node = root.find(tag, self.namespaces) if 'ce:' in tag else root.find(tag)
            if node is not None and node.text:
                metadata["pii"] = self.clean_text(node.text)
                break

        # 3. Title
        for tag in ['.//ce:title', './/article-title', './/title']:
            node = root.find(tag, self.namespaces) if 'ce:' in tag else root.find(tag)
            if node is not None:
                title_text = self.extract_element_text(node)
                if title_text:
                    metadata["title"] = title_text
                    break

        # 4. Abstract
        for tag in ['.//ce:abstract', './/abstract']:
            node = root.find(tag, self.namespaces) if 'ce:' in tag else root.find(tag)
            if node is not None:
                metadata["abstract"] = self.extract_element_text(node)
                break

        return metadata

    def _extract_paragraphs(self, root: ET.Element) -> List[str]:
        """Extracts all full-text narrative paragraphs from the document body."""
        paragraphs = []
        for tag in ['.//ce:para', './/ce:simple-para', './/p']:
            nodes = root.findall(tag, self.namespaces) if 'ce:' in tag else root.findall(tag)
            for n in nodes:
                # Exclude paragraphs inside tables or table captions
                txt = self.extract_element_text(n)
                if txt and len(txt) > 25 and txt not in paragraphs:
                    paragraphs.append(txt)
        return paragraphs

    def _extract_tables(self, root: ET.Element, metadata: Dict[str, str]) -> List[Dict[str, Any]]:
        """Finds all table nodes (Elsevier and JATS) and converts them into structured table objects."""
        extracted_tables = []

        # Find Elsevier tables (<ce:table> or <table>) or JATS (<table-wrap>)
        table_nodes = []
        for tag in ['.//ce:table', './/table-wrap', './/table']:
            nodes = root.findall(tag, self.namespaces) if 'ce:' in tag else root.findall(tag)
            for n in nodes:
                if n not in table_nodes:
                    table_nodes.append(n)

        for idx, tbl_node in enumerate(table_nodes):
            tbl_data = self._parse_single_table(tbl_node, idx, metadata)
            if tbl_data:
                extracted_tables.append(tbl_data)

        return extracted_tables

    def _parse_single_table(self, tbl_node: ET.Element, index: int, metadata: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extracts caption, footnotes, headers, and body rows for a single table."""
        table_id = tbl_node.get("id") or f"tbl_{index+1}"
        
        # Caption / Label
        caption = ""
        for tag in ['.//ce:caption', './/caption', './/ce:label', './/label']:
            cap_node = tbl_node.find(tag, self.namespaces) if 'ce:' in tag else tbl_node.find(tag)
            if cap_node is not None:
                caption = self.extract_element_text(cap_node)
                if caption:
                    break

        # Footnote
        footnote = ""
        for tag in ['.//ce:table-footnote', './/table-wrap-foot', './/fn', './/footnote']:
            fn_node = tbl_node.find(tag, self.namespaces) if 'ce:' in tag else tbl_node.find(tag)
            if fn_node is not None:
                footnote = self.extract_element_text(fn_node)
                if footnote:
                    break

        # Headers and Rows
        headers = []
        rows = []

        # Try Elsevier <tgroup>
        tgroup = tbl_node.find('.//tgroup')
        if tgroup is not None:
            thead = tgroup.find('thead')
            if thead is not None:
                for r in thead.findall('row'):
                    headers = [self.extract_element_text(entry) for entry in r.findall('entry')]
            
            tbody = tgroup.find('tbody')
            if tbody is not None:
                for r in tbody.findall('row'):
                    row_cells = [self.extract_element_text(entry) for entry in r.findall('entry')]
                    if any(row_cells):
                        rows.append(row_cells)
        else:
            # Try Standard HTML/JATS <table> with <thead> and <tbody> or <tr>
            thead = tbl_node.find('.//thead')
            if thead is not None:
                for tr in thead.findall('.//tr'):
                    headers = [self.extract_element_text(th) for th in (tr.findall('th') or tr.findall('td'))]
            
            tbody = tbl_node.find('.//tbody') or tbl_node
            for tr in tbody.findall('.//tr'):
                # Check if this row is just headers
                ths = tr.findall('th')
                tds = tr.findall('td')
                if ths and not tds and not headers:
                    headers = [self.extract_element_text(th) for th in ths]
                elif tds:
                    row_cells = [self.extract_element_text(td) for td in tds]
                    if any(row_cells):
                        rows.append(row_cells)

        if not rows and not headers:
            return None

        # Build raw DataFrame and Cleaned DataFrame
        max_cols = max([len(headers)] + [len(r) for r in rows]) if rows or headers else 0
        if not headers:
            headers = [f"Col_{i+1}" for i in range(max_cols)]
        elif len(headers) < max_cols:
            headers += [f"Col_{i+1}" for i in range(len(headers), max_cols)]

        padded_rows = []
        for r in rows:
            if len(r) < max_cols:
                r = r + ["-"] * (max_cols - len(r))
            padded_rows.append(r[:max_cols])

        df_raw = pd.DataFrame(padded_rows, columns=headers[:max_cols])
        
        # Create cleaned DataFrame
        df_cleaned = df_raw.copy()
        # Replace empty strings or whitespace-only with standard placeholder
        df_cleaned = df_cleaned.map(lambda x: "-" if str(x).strip() in ["", "nan", "None", "null", "N/A", "n/a", "--"] else str(x).strip())

        return {
            "table_id": table_id,
            "doi": metadata.get("doi", ""),
            "caption": caption,
            "footnote": footnote,
            "headers": headers[:max_cols],
            "num_rows": len(padded_rows),
            "num_cols": max_cols,
            "raw_df": df_raw,
            "cleaned_df": df_cleaned,
            "raw_dict": df_raw.to_dict(orient="records"),
            "cleaned_dict": df_cleaned.to_dict(orient="records")
        }
