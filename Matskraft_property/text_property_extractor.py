"""
Narrative Text Property & Material Extractor for CrystaGraph.
Extracts material entities, composition formulas, and experimental property measurements
directly from scientific literature text (abstracts, paragraphs, introductions, experimental sections)
when tables are absent or properties are detailed in narrative prose.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import os
import sys

# Add Matskraft_property to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from property_vocab import canonicalize_property, get_property_category, PROPERTY_SYNONYMS
from unit_normalizer import normalize_unit
from si_units import convert_to_si

class TextPropertyExtractor:
    """
    NLP and pattern-based extractor for discovering material properties from narrative scientific text.
    Handles papers without tables or properties stated in article paragraphs.
    """

    def __init__(self):
        # Known common material keywords and alloy patterns
        self.alloy_pattern = re.compile(
            r'\b(?:Ti|Al|Fe|Ni|Co|Cu|Mg|Zr|Nb|Mo|W|Ta|Cr)-[A-Za-z0-9\-\.]+\b|'
            r'\b(?:AA\s*\d{4}[A-Za-z0-9\-]*|Grade\s+\d+|Inconel\s*\d+|Hastelloy\s*[A-Za-z0-9\-]+)\b|'
            r'\b(?:Bioglass\s*45S5|45S5|Cantor\s+alloy|HEA|SMA)\b|'
            r'\b(?:Li[A-Za-z0-9\.\-]+O\d*|Ba[A-Za-z0-9\.\-]+O\d*|Bi\d+Te\d+|CoSb\d+|NiTi[A-Za-z0-9\-]*|YBa\d+Cu\d+O\d*|YSZ|8YSZ)\b',
            re.IGNORECASE
        )

        # General chemical formula regex (e.g. SiO2, Al2O3, LiFePO4, BaTiO3)
        self.formula_pattern = re.compile(r'\b(?:[A-Z][a-z]?(?:\d*(?:\.\d+)?)){2,}\b')

        # Property names pattern for matching in text
        sorted_synonyms = sorted(PROPERTY_SYNONYMS.keys(), key=lambda x: len(x), reverse=True)
        synonyms_escaped = [re.escape(s) for s in sorted_synonyms if len(s) > 1]
        self.props_alt = '(?:' + '|'.join(synonyms_escaped) + ')'

        # Units regex pattern
        self.units_alt = (
            r'(?:MPa|GPa|Pa|g/cm[3³]|g\s*cm\^?-3|kg/m[3³]|HV\d*|mAh/g|Wh/kg|mV|V|W/m[\·\-\s]*K|W/\(m[\·\s]*K\)|'
            r'S/cm|S/m|µS/cm|µV/K|uV/K|µW/cm[\·\s]*K[2²]|pC/N|µC/cm[2²]|T|Tesla|MA/cm[2²]|K|°C|deg\s*C|%)'
        )

        # Number pattern
        self.num_pat = r'[~><≥≤]?\s*-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?:\s*(?:±|-|to|–)\s*\d+(?:\.\d+)?)?'

        # Pattern A: <Property> [verb] <Value> <Unit>
        self.pattern_a = re.compile(
            r'\b(?P<prop>' + self.props_alt + r')\s*'
            r'(?:(?:of|was|is|are|reached|exhibited|exhibits|measured|determined|reported|found|shows|yielded|equals|=|~|approx(?:imately)?)\s*(?:as|to\s+be|at|around)?|:)?\s*'
            r'(?P<val>' + self.num_pat + r')\s*'
            r'(?P<unit>' + self.units_alt + r')\b',
            re.IGNORECASE
        )

        # Pattern B: <Value> <Unit> <Property>
        self.pattern_b = re.compile(
            r'\b(?P<val>' + self.num_pat + r')\s*'
            r'(?P<unit>' + self.units_alt + r')\s*(?:of)?\s*'
            r'(?P<prop>' + self.props_alt + r')\b',
            re.IGNORECASE
        )

        # Pattern C: Dimensionless properties (dielectric constant, dielectric loss, ZT, etc.)
        dim_props_alt = r'(?:dielectric\s+constant|permittivity|dielectric\s+loss|tan\s+delta|figure\s+of\s+merit|zt|loss\s+tangent)'
        self.pattern_c = re.compile(
            r'\b(?P<prop>' + dim_props_alt + r')\s*'
            r'(?:of|was|is|reached|measured|reported\s+as|equals|:)?\s*'
            r'(?P<val>[~><≥≤]?\s*-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b',
            re.IGNORECASE
        )

    def extract_materials_from_text(self, text: str) -> List[str]:
        """Finds candidate material names and chemical formulas from text."""
        candidates = []
        
        # 1. Known alloy patterns
        for m in self.alloy_pattern.finditer(text):
            mat = m.group(0).strip()
            if len(mat) >= 2 and mat not in candidates:
                candidates.append(mat)

        # 2. Chemical formulas
        for m in self.formula_pattern.finditer(text):
            mat = m.group(0).strip()
            if any(c.isdigit() for c in mat) and mat not in candidates:
                candidates.append(mat)

        # 3. Named sample / alloy designations
        sample_matches = re.findall(r'\b(?:Sample|Alloy|Formulation|Glass|Ceramic)\s+([A-Za-z0-9\-]+)\b', text, re.IGNORECASE)
        for s in sample_matches:
            name = f"Sample {s}"
            if name not in candidates:
                candidates.append(name)

        return candidates

    def parse_numeric_value(self, val_str: str) -> Tuple[Optional[float], str]:
        """Parses a raw number string (including ranges and uncertainties) into a float and clean string."""
        clean = val_str.replace("~", "").replace(">", "").replace("<", "").replace("≥", "").replace("≤", "").strip()
        
        # Range check: "800 - 850" or "800 to 850"
        range_match = re.search(r'(-?\d+(?:\.\d+)?)\s*(?:-|to|–)\s*(-?\d+(?:\.\d+)?)', clean)
        if range_match:
            try:
                v1 = float(range_match.group(1))
                v2 = float(range_match.group(2))
                return round((v1 + v2) / 2.0, 3), f"{v1} - {v2}"
            except ValueError:
                pass

        # Uncertainty check: "880 ± 15"
        pm_match = re.search(r'(-?\d+(?:\.\d+)?)\s*±\s*(-?\d+(?:\.\d+)?)', clean)
        if pm_match:
            try:
                v1 = float(pm_match.group(1))
                return v1, clean
            except ValueError:
                pass

        num_only = re.sub(r'[^\d\.\-\+eE]', '', clean)
        try:
            val = float(num_only)
            return val, clean
        except ValueError:
            return None, clean

    def extract_properties_from_sentence(
        self,
        sentence: str,
        active_material: str,
        paper_id: str = "doc_text",
        doi: str = ""
    ) -> List[Dict[str, Any]]:
        """Extracts property-value-unit triples from an individual sentence."""
        results = []
        if len(sentence.strip()) < 10:
            return results

        matched_spans = set()

        # 1. Try Pattern A: <Property> <Value> <Unit>
        for match in self.pattern_a.finditer(sentence):
            prop_raw = match.group("prop")
            val_raw = match.group("val")
            unit_raw = match.group("unit")
            span = match.span()
            matched_spans.add(span)

            canonical = canonicalize_property(prop_raw)
            if not canonical:
                continue

            num_val, clean_val_str = self.parse_numeric_value(val_raw)
            norm_unit = normalize_unit(unit_raw)
            si_info = convert_to_si(num_val, norm_unit, canonical)

            results.append({
                "paper_id": paper_id,
                "doi": doi,
                "table_id": "narrative_text",
                "material_name": active_material or "Investigated Material",
                "property_name": canonical,
                "raw_property_header": prop_raw.strip(),
                "property_category": get_property_category(canonical),
                "value_raw": f"{clean_val_str} {norm_unit}".strip(),
                "value_numeric": num_val,
                "unit": norm_unit,
                "si_value": si_info["si_value"],
                "si_unit": si_info["si_unit"],
                "si_formatted": si_info["si_formatted"],
                "source_type": "Narrative Text",
                "condition_footnote": f"Context: \"{sentence.strip()}\"",
                "confidence": 0.94
            })

        # 2. Try Pattern B: <Value> <Unit> <Property>
        for match in self.pattern_b.finditer(sentence):
            val_raw = match.group("val")
            unit_raw = match.group("unit")
            prop_raw = match.group("prop")
            span = match.span()
            if any(abs(span[0] - ms[0]) < 5 for ms in matched_spans):
                continue
            matched_spans.add(span)

            canonical = canonicalize_property(prop_raw)
            if not canonical:
                continue

            num_val, clean_val_str = self.parse_numeric_value(val_raw)
            norm_unit = normalize_unit(unit_raw)
            si_info = convert_to_si(num_val, norm_unit, canonical)

            results.append({
                "paper_id": paper_id,
                "doi": doi,
                "table_id": "narrative_text",
                "material_name": active_material or "Investigated Material",
                "property_name": canonical,
                "raw_property_header": prop_raw.strip(),
                "property_category": get_property_category(canonical),
                "value_raw": f"{clean_val_str} {norm_unit}".strip(),
                "value_numeric": num_val,
                "unit": norm_unit,
                "si_value": si_info["si_value"],
                "si_unit": si_info["si_unit"],
                "si_formatted": si_info["si_formatted"],
                "source_type": "Narrative Text",
                "condition_footnote": f"Context: \"{sentence.strip()}\"",
                "confidence": 0.92
            })

        # 3. Try Pattern C: Dimensionless properties (Dielectric constant, Loss, ZT)
        for match in self.pattern_c.finditer(sentence):
            prop_raw = match.group("prop")
            val_raw = match.group("val")
            span = match.span()
            if any(abs(span[0] - ms[0]) < 5 for ms in matched_spans):
                continue

            canonical = canonicalize_property(prop_raw)
            if not canonical:
                continue

            num_val, clean_val_str = self.parse_numeric_value(val_raw)
            si_info = convert_to_si(num_val, "dimensionless", canonical)

            results.append({
                "paper_id": paper_id,
                "doi": doi,
                "table_id": "narrative_text",
                "material_name": active_material or "Investigated Material",
                "property_name": canonical,
                "raw_property_header": prop_raw.strip(),
                "property_category": get_property_category(canonical),
                "value_raw": clean_val_str,
                "value_numeric": num_val,
                "unit": "dimensionless",
                "si_value": si_info["si_value"],
                "si_unit": si_info["si_unit"],
                "si_formatted": si_info["si_formatted"],
                "source_type": "Narrative Text",
                "condition_footnote": f"Context: \"{sentence.strip()}\"",
                "confidence": 0.91
            })

        return results

    def extract_from_text(
        self,
        full_text: str,
        paper_id: str = "doc_text",
        doi: str = "",
        default_material: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Parses multi-paragraph narrative text, resolves active material context,
        and extracts all property mentions with standardized SI units.
        """
        if not full_text:
            return []

        # Split text into sentences
        sentences = re.split(r'(?<!\d)\.(?!\d)\s+|\n\n+', full_text)

        all_extractions = []
        current_material = default_material or ""

        # First pass: identify document-level candidate material
        doc_materials = self.extract_materials_from_text(full_text)
        if not current_material and doc_materials:
            current_material = doc_materials[0]

        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue

            # Update active material if new material is specifically introduced
            sent_mats = self.extract_materials_from_text(sent_clean)
            if sent_mats:
                current_material = sent_mats[0]

            extracted = self.extract_properties_from_sentence(
                sentence=sent_clean,
                active_material=current_material,
                paper_id=paper_id,
                doi=doi
            )
            all_extractions.extend(extracted)

        return all_extractions

    def batch_extract_from_papers(
        self,
        papers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extracts properties from narrative sections of multiple papers.
        Each paper dict can contain 'paper_id', 'doi', 'title', 'abstract', and 'paragraphs'.
        """
        results = []
        for p in papers:
            paper_id = p.get("paper_id", "")
            doi = p.get("doi", "")
            title = p.get("title", "")
            abstract = p.get("abstract", "")
            paragraphs = p.get("paragraphs", [])

            title_mats = self.extract_materials_from_text(title)
            default_mat = title_mats[0] if title_mats else ""

            combined_text = f"{title}\n\n{abstract}\n\n" + "\n\n".join(paragraphs)
            props = self.extract_from_text(
                full_text=combined_text,
                paper_id=paper_id,
                doi=doi,
                default_material=default_mat
            )
            results.extend(props)

        return results

if __name__ == "__main__":
    extractor = TextPropertyExtractor()
    sample_text = """
    In this study, Ti-6Al-4V titanium alloy was investigated for aerospace turbine applications.
    The Ti-6Al-4V alloy exhibited a yield strength of 880 MPa, an ultimate tensile strength of 950 MPa,
    and a density of 4.43 g/cm3. The Vickers hardness reached 350 HV.
    Furthermore, BaTiO3 perovskite ceramics demonstrated a high dielectric constant of 1850 and dielectric loss of 0.015.
    The thermal conductivity of the sample was 1.45 W/m-K at 300 K.
    """
    res = extractor.extract_from_text(sample_text)
    print(f"Extracted {len(res)} property records from sample narrative text:")
    for r in res:
        print(f" • [{r['material_name']}] {r['property_name']}: {r['value_raw']} -> SI: {r['si_formatted']} ({r['si_unit']})")
