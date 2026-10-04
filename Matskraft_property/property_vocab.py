"""
Property Ontology and Vocabulary for CrystaGraph.
Defines canonical property names, synonym dictionaries, categories, and standard physical units.
"""

from typing import Dict, List, Optional, Tuple

PROPERTY_TAXONOMY = {
    "Mechanical Properties": [
        "Yield Strength", "Ultimate Tensile Strength", "Tensile Strength", "Compressive Strength",
        "Elongation", "Plastic Strain", "Young's Modulus", "Vickers Hardness", "Hardness",
        "Fracture Toughness", "Plateau Stress", "Recoverable Strain"
    ],
    "Physical & Structural Properties": [
        "Density", "Tap Density", "Relative Density", "Curie Temperature", "Glass Transition Tg",
        "Martensite Start Ms", "Austenite Finish Af"
    ],
    "Electrochemical & Battery Properties": [
        "Specific Capacity", "Nominal Voltage", "Energy Density", "Cycle Retention"
    ],
    "Dielectric & Piezoelectric Properties": [
        "Dielectric Constant", "Dielectric Loss", "Piezoelectric Coefficient d33", "Remanent Polarization"
    ],
    "Superconducting & Magnetic Properties": [
        "Critical Temp Tc", "Upper Critical Field Hc2", "Critical Current Density Jc",
        "Coherence Length xi", "Penetration Depth lambda"
    ],
    "Thermal & Thermoelectric Properties": [
        "Thermal Expansion CTE", "Thermal Conductivity", "Seebeck Coefficient",
        "Electrical Conductivity", "Power Factor", "Figure of Merit ZT", "Activation Energy",
        "Ionic Conductivity at 800C"
    ]
}

# Mapping common table header synonyms to canonical property names
PROPERTY_SYNONYMS = {
    "ys": "Yield Strength",
    "yield strength": "Yield Strength",
    "yield stress": "Yield Strength",
    "uts": "Ultimate Tensile Strength",
    "ultimate tensile strength": "Ultimate Tensile Strength",
    "tensile strength": "Tensile Strength",
    "compressive strength": "Compressive Strength",
    "elongation": "Elongation",
    "plastic strain": "Plastic Strain",
    "strain": "Plastic Strain",
    "hardness": "Hardness",
    "vickers hardness": "Vickers Hardness",
    "hv": "Vickers Hardness",
    "hv30": "Vickers Hardness",
    "density": "Density",
    "tap density": "Tap Density",
    "relative density": "Relative Density",
    "young's modulus": "Young's Modulus",
    "elastic modulus": "Young's Modulus",
    "fracture toughness": "Fracture Toughness",
    "k1c": "Fracture Toughness",
    "specific capacity": "Specific Capacity",
    "capacity": "Specific Capacity",
    "voltage": "Nominal Voltage",
    "nominal voltage": "Nominal Voltage",
    "operating voltage": "Nominal Voltage",
    "energy density": "Energy Density",
    "cycle retention": "Cycle Retention",
    "dielectric constant": "Dielectric Constant",
    "permittivity": "Dielectric Constant",
    "dielectric loss": "Dielectric Loss",
    "tan delta": "Dielectric Loss",
    "curie temperature": "Curie Temperature",
    "tc": "Critical Temp Tc",
    "critical temp": "Critical Temp Tc",
    "critical temperature": "Critical Temp Tc",
    "d33": "Piezoelectric Coefficient d33",
    "piezoelectric coefficient": "Piezoelectric Coefficient d33",
    "remanent polarization": "Remanent Polarization",
    "pr": "Remanent Polarization",
    "upper critical field": "Upper Critical Field Hc2",
    "hc2": "Upper Critical Field Hc2",
    "critical current density": "Critical Current Density Jc",
    "jc": "Critical Current Density Jc",
    "coherence length": "Coherence Length xi",
    "penetration depth": "Penetration Depth lambda",
    "glass transition": "Glass Transition Tg",
    "tg": "Glass Transition Tg",
    "thermal expansion": "Thermal Expansion CTE",
    "cte": "Thermal Expansion CTE",
    "thermal conductivity": "Thermal Conductivity",
    "seebeck coefficient": "Seebeck Coefficient",
    "seebeck": "Seebeck Coefficient",
    "electrical conductivity": "Electrical Conductivity",
    "ionic conductivity": "Ionic Conductivity at 800C",
    "ionic conductivity at 800c": "Ionic Conductivity at 800C",
    "activation energy": "Activation Energy",
    "ea": "Activation Energy",
    "power factor": "Power Factor",
    "zt": "Figure of Merit ZT",
    "figure of merit": "Figure of Merit ZT",
    "martensite start": "Martensite Start Ms",
    "ms": "Martensite Start Ms",
    "austenite finish": "Austenite Finish Af",
    "af": "Austenite Finish Af",
    "recoverable strain": "Recoverable Strain",
    "plateau stress": "Plateau Stress"
}

def canonicalize_property(header_text: str) -> Optional[str]:
    """Finds the standard canonical property name from arbitrary header text."""
    clean = header_text.lower().strip()
    # Direct synonym match
    if clean in PROPERTY_SYNONYMS:
        return PROPERTY_SYNONYMS[clean]

    # Substring search
    for syn, canonical in PROPERTY_SYNONYMS.items():
        if syn in clean:
            return canonical

    return None

def get_property_category(canonical_name: str) -> str:
    """Returns the high-level category for a canonical property."""
    for cat, props in PROPERTY_TAXONOMY.items():
        if canonical_name in props:
            return cat
    return "General Properties"
