"""
Chemical composition extraction rules and regular expression patterns for CrystaGraph.
Handles periodic table elements, oxide formulas, stoichiometry, and percentage unit matching.
"""

import re
from typing import Dict, List, Optional, Tuple

# Standard Periodic Table Elements
ELEMENTS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
    "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
    "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe",
    "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu",
    "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra",
    "Ac", "Th", "Pa", "U", "Np", "Pu"
}

# Common Ceramic Oxides and Compounds
COMMON_OXIDES = {
    "SiO2", "Al2O3", "Fe2O3", "FeO", "Fe3O4", "TiO2", "ZrO2", "BaO", "CaO", "MgO", "Na2O", "K2O",
    "P2O5", "B2O3", "Y2O3", "CeO2", "Gd2O3", "La2O3", "SrO", "NiO", "CoO", "ZnO", "MnO", "Nb2O5",
    "Bi2O3", "Ta2O5", "WO3", "MoO3", "PbO", "Li2O", "CuO", "V2O5", "Cr2O3", "Ga2O3", "In2O3", "SnO2"
}

# Patterns for percentage and composition units
UNIT_PATTERN = re.compile(r'\b(wt\.?%|at\.?%|mol\.?%|vol\.?%|mass\s*%|atomic\s*%|weight\s*%|mol%|wt%|at%|%)\b', re.IGNORECASE)

# Pattern to extract chemical component and unit from header like "SiO2 (wt.%)" or "Al (at.%)"
HEADER_COMP_PATTERN = re.compile(r'^([A-Za-z0-9\(\)\-\.]+)\s*(\([^\)]*\))?$')

def detect_composition_unit(text: str) -> str:
    """Identifies the composition unit from text or headers."""
    match = UNIT_PATTERN.search(text)
    if match:
        unit = match.group(1).lower().replace(" ", "")
        if "wt" in unit or "weight" in unit or "mass" in unit:
            return "wt.%"
        elif "at" in unit or "atomic" in unit:
            return "at.%"
        elif "mol" in unit:
            return "mol%"
        elif "%" in unit:
            return "%"
    return "wt.%" # Default assumption in materials science tables if omitted

def is_chemical_component(token: str) -> bool:
    """Checks if a string token is a recognized chemical element, oxide, or compound."""
    clean = re.sub(r'[\(\)\[\]\.,\:]', '', token).strip()
    if not clean:
        return False
    if clean in ELEMENTS or clean in COMMON_OXIDES:
        return True
    
    # Check if formula consists of valid element blocks like BaTiO3, LiFePO4, Al0.3CoCrFeNi
    elem_pattern = r'([A-Z][a-z]?)([0-9\.]*)'
    matches = re.findall(elem_pattern, clean)
    if matches:
        recon = "".join([m[0] + m[1] for m in matches])
        if recon == clean and all(m[0] in ELEMENTS for m in matches):
            return True
    return False

def parse_header_for_component(header: str) -> Optional[Tuple[str, str]]:
    """
    Analyzes a table header string to determine if it represents a composition column.
    Returns (component_name, unit) if matched, else None.
    """
    clean_h = header.strip()
    # Check if header contains keywords indicating a property rather than a composition
    property_keywords = [
        "strength", "hardness", "modulus", "density", "temperature", "voltage",
        "capacity", "conductivity", "strain", "elongation", "pressure", "energy",
        "loss", "constant", "factor", "field", "length", "depth", "stress", "roughness",
        "dimension", "thickness", "diameter", "sample", "alloy", "material", "name", "id", "formula"
    ]
    if any(k in clean_h.lower() for k in property_keywords):
        return None

    # Try matching "SiO2 (wt.%)" or "Al (at.%)"
    unit = detect_composition_unit(clean_h)
    # Remove unit from header to check component
    comp_part = UNIT_PATTERN.sub('', clean_h).replace('(', '').replace(')', '').replace('[', '').replace(']', '').strip()
    
    if is_chemical_component(comp_part):
        return (comp_part, unit)
    
    # Also check if the raw token is a component
    tokens = clean_h.split()
    for tok in tokens:
        cand = re.sub(r'[^A-Za-z0-9]', '', tok)
        if is_chemical_component(cand):
            return (cand, unit)

    return None

def is_numeric_value(val: str) -> bool:
    """Validates if a string cell is numeric (including floating point, negative, or scientific notation)."""
    val = str(val).strip().replace(',', '')
    if val in ["-", "--", "N/A", "n/a", "nil", "none", "None", ""]:
        return False
    try:
        float(val)
        return True
    except ValueError:
        # Check range format like 10-15 or 12.5 +/- 0.5
        if re.match(r'^-?\d+(\.\d+)?\s*(±|\+/-|-)\s*\d+(\.\d+)?$', val):
            return True
        return False
