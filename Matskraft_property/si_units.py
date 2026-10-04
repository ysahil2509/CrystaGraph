"""
SI Units Normalizer and Conversion Engine for CrystaGraph.
Converts extracted material properties from reported literature units into standardized SI units.
"""

from typing import Tuple, Optional, Dict, Any
import re

# Standard canonical SI definitions
# Each entry defines: standard_si_unit, target_category, conversion_fn
# where conversion_fn(numeric_val, raw_unit) -> (si_numeric, si_unit_str, formatted_str)

def to_si_density(val: float, raw_unit: str) -> Tuple[float, str, str]:
    u = raw_unit.lower()
    if "g/cm" in u or "g cm" in u:
        si_val = val * 1000.0  # 1 g/cm3 = 1000 kg/m3
        return si_val, "kg/m³", f"{si_val:,.1f} kg/m³"
    elif "kg/m" in u:
        return val, "kg/m³", f"{val:,.1f} kg/m³"
    elif "mg/cm" in u:
        si_val = val * 1.0
        return si_val, "kg/m³", f"{si_val:,.1f} kg/m³"
    return val * 1000.0, "kg/m³", f"{val * 1000.0:,.1f} kg/m³"

def to_si_stress_or_modulus(val: float, raw_unit: str, canonical_prop: str) -> Tuple[float, str, str]:
    u = raw_unit.lower()
    # Young's modulus canonical SI is typically GPa, while strength is MPa
    if "modulus" in canonical_prop.lower():
        if "mpa" in u:
            si_val = val / 1000.0
            return si_val, "GPa", f"{si_val:.2f} GPa"
        elif "pa" in u and "gpa" not in u and "mpa" not in u:
            si_val = val / 1e9
            return si_val, "GPa", f"{si_val:.2f} GPa"
        else:
            return val, "GPa", f"{val:.1f} GPa"
    else:
        # Strengths (Yield Strength, Tensile Strength, UTS, Compressive, Plateau Stress)
        if "gpa" in u:
            si_val = val * 1000.0
            return si_val, "MPa", f"{si_val:,.1f} MPa"
        elif "pa" in u and "mpa" not in u:
            si_val = val / 1e6
            return si_val, "MPa", f"{si_val:,.1f} MPa"
        elif "bar" in u:
            si_val = val * 0.1
            return si_val, "MPa", f"{si_val:,.1f} MPa"
        return val, "MPa", f"{val:,.1f} MPa"

def to_si_temperature(val: float, raw_unit: str) -> Tuple[float, str, str]:
    u = raw_unit.lower()
    if "c" in u or "°" in u or "deg" in u:
        si_val = val + 273.15
        return si_val, "K", f"{si_val:.2f} K"
    elif "f" in u:
        si_val = (val - 32) * 5/9 + 273.15
        return si_val, "K", f"{si_val:.2f} K"
    return val, "K", f"{val:.2f} K"

def to_si_conductivity(val: float, raw_unit: str) -> Tuple[float, str, str]:
    u = raw_unit.lower()
    if "s/cm" in u or "s cm-1" in u:
        si_val = val * 100.0  # 1 S/cm = 100 S/m
        return si_val, "S/m", f"{si_val:,.2e} S/m" if si_val > 10000 or si_val < 0.01 else f"{si_val:,.2f} S/m"
    elif "ms/m" in u:
        si_val = val * 1e6
        return si_val, "S/m", f"{si_val:,.2e} S/m"
    return val, "S/m", f"{val:,.2f} S/m"

def to_si_thermal_conductivity(val: float, raw_unit: str) -> Tuple[float, str, str]:
    return val, "W/(m·K)", f"{val:.2f} W/(m·K)"

def to_si_capacity(val: float, raw_unit: str) -> Tuple[float, str, str]:
    u = raw_unit.lower()
    # 1 mAh/g = 3600 C/kg in pure SI, but in battery literature standard SI presentation is mAh/g (or C/kg)
    if "mah/g" in u or "mah g-1" in u or not u:
        return val, "mAh/g", f"{val:.1f} mAh/g"
    elif "ah/kg" in u:
        return val, "mAh/g", f"{val:.1f} mAh/g"
    return val, "mAh/g", f"{val:.1f} mAh/g"

def to_si_hardness(val: float, raw_unit: str) -> Tuple[float, str, str]:
    return val, "HV", f"{val:.1f} HV"

def convert_to_si(
    value_numeric: Optional[float],
    current_unit: str,
    property_name: str
) -> Dict[str, Any]:
    """
    Standardizes a property measurement into international SI units.
    
    Returns a dict with:
      - si_value (float or None)
      - si_unit (str)
      - si_formatted (str)
      - base_si_conversion_note (str)
    """
    if value_numeric is None:
        return {
            "si_value": None,
            "si_unit": current_unit or "",
            "si_formatted": "N/A",
            "note": "Non-numeric value"
        }

    prop_lower = (property_name or "").lower()
    unit_clean = (current_unit or "").strip()

    # 1. Density
    if "density" in prop_lower:
        si_val, si_u, si_fmt = to_si_density(value_numeric, unit_clean)
        return {
            "si_value": round(si_val, 2),
            "si_unit": si_u,
            "si_formatted": si_fmt,
            "note": "Converted from g/cm³ to standard SI kg/m³" if "g/cm" in unit_clean.lower() else "Standard SI"
        }

    # 2. Mechanical Strengths and Moduli
    if any(k in prop_lower for k in ["yield strength", "tensile strength", "uts", "compressive strength", "plateau stress", "modulus"]):
        si_val, si_u, si_fmt = to_si_stress_or_modulus(value_numeric, unit_clean, property_name)
        return {
            "si_value": round(si_val, 2),
            "si_unit": si_u,
            "si_formatted": si_fmt,
            "note": "Standard engineering SI unit (MPa/GPa)"
        }

    # 3. Hardness
    if "hardness" in prop_lower or "hv" in prop_lower:
        si_val, si_u, si_fmt = to_si_hardness(value_numeric, unit_clean)
        return {
            "si_value": round(si_val, 1),
            "si_unit": si_u,
            "si_formatted": si_fmt,
            "note": "Vickers Hardness (HV)"
        }

    # 4. Temperatures
    if any(k in prop_lower for k in ["temperature", "curie", "critical temp", "tg", "ms", "af"]):
        si_val, si_u, si_fmt = to_si_temperature(value_numeric, unit_clean)
        return {
            "si_value": round(si_val, 2),
            "si_unit": si_u,
            "si_formatted": si_fmt,
            "note": "Converted to SI base unit Kelvin (K)" if "c" in unit_clean.lower() else "Kelvin (K)"
        }

    # 5. Thermal Conductivity
    if "thermal conductivity" in prop_lower:
        si_val, si_u, si_fmt = to_si_thermal_conductivity(value_numeric, unit_clean)
        return {
            "si_value": round(si_val, 3),
            "si_unit": si_u,
            "si_formatted": si_fmt,
            "note": "Standard SI: W/(m·K)"
        }

    # 6. Electrical and Ionic Conductivity
    if "conductivity" in prop_lower and "thermal" not in prop_lower:
        si_val, si_u, si_fmt = to_si_conductivity(value_numeric, unit_clean)
        return {
            "si_value": round(si_val, 4),
            "si_unit": si_u,
            "si_formatted": si_fmt,
            "note": "Converted from S/cm to SI S/m (×100)" if "s/cm" in unit_clean.lower() else "SI S/m"
        }

    # 7. Battery Specific Capacity
    if "capacity" in prop_lower:
        si_val, si_u, si_fmt = to_si_capacity(value_numeric, unit_clean)
        return {
            "si_value": round(si_val, 1),
            "si_unit": si_u,
            "si_formatted": si_fmt,
            "note": "Electrochemical SI: mAh/g (1 mAh/g = 3600 C/kg)"
        }

    # 8. Voltage
    if "voltage" in prop_lower or unit_clean.lower() in ["v", "mv"]:
        v_num = value_numeric / 1000.0 if unit_clean.lower() == "mv" else value_numeric
        return {
            "si_value": round(v_num, 3),
            "si_unit": "V",
            "si_formatted": f"{v_num:.2f} V",
            "note": "Standard SI Volt (V)"
        }

    # 9. Magnetic Field
    if "magnetic" in prop_lower or "hc2" in prop_lower or unit_clean.lower() in ["t", "tesla"]:
        return {
            "si_value": round(value_numeric, 2),
            "si_unit": "T",
            "si_formatted": f"{value_numeric:.2f} T",
            "note": "Standard SI Tesla (T)"
        }

    # 10. Dimensionless (Dielectric Constant, Loss, ZT, Elongation %)
    if any(k in prop_lower for k in ["dielectric constant", "figure of merit", "zt", "loss", "elongation", "strain"]):
        unit_str = "%" if "elongation" in prop_lower or "strain" in prop_lower or "%" in unit_clean else "dimensionless"
        fmt_str = f"{value_numeric:.1f} %" if unit_str == "%" else f"{value_numeric:.3f}"
        return {
            "si_value": round(value_numeric, 3),
            "si_unit": unit_str,
            "si_formatted": fmt_str,
            "note": "Dimensionless ratio / fraction"
        }

    # Default fallback
    u_fallback = unit_clean or "a.u."
    return {
        "si_value": value_numeric,
        "si_unit": u_fallback,
        "si_formatted": f"{value_numeric:g} {u_fallback}",
        "note": "Original unit preserved"
    }
