"""
Unit tests for Text Property Extractor and SI Unit Standardization.
Verifies extraction from papers without tables and SI conversions.
"""

import unittest
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Matskraft_property"))

from text_property_extractor import TextPropertyExtractor
from si_units import convert_to_si

class TestTextAndSIExtraction(unittest.TestCase):

    def setUp(self):
        self.extractor = TextPropertyExtractor()

    def test_extract_from_narrative_text(self):
        sample_text = """
        The aerospace titanium alloy Ti-6Al-4V was evaluated under severe mechanical loading.
        Ti-6Al-4V exhibited a yield strength of 880 MPa, an ultimate tensile strength of 950 MPa,
        and a density of 4.43 g/cm3. The measured Vickers hardness reached 350 HV.
        Additionally, the thermal conductivity was determined to be 1.45 W/m-K.
        """
        results = self.extractor.extract_from_text(sample_text, paper_id="test_doc_01")
        self.assertGreaterEqual(len(results), 4)

        props_found = {r["property_name"]: r for r in results}
        self.assertIn("Yield Strength", props_found)
        self.assertEqual(props_found["Yield Strength"]["value_numeric"], 880.0)
        self.assertEqual(props_found["Yield Strength"]["si_unit"], "MPa")

        self.assertIn("Density", props_found)
        self.assertEqual(props_found["Density"]["value_numeric"], 4.43)
        self.assertEqual(props_found["Density"]["si_unit"], "kg/m³")
        self.assertEqual(props_found["Density"]["si_value"], 4430.0)

    def test_paper_without_tables(self):
        paper_obj = {
            "paper_id": "paper_no_tables",
            "doi": "10.1016/j.test.2024.001",
            "title": "Properties of novel high-strength aluminum alloy AA7075-T6",
            "abstract": "We report synthesis and testing of AA7075-T6 without any structured tables.",
            "paragraphs": [
                "The AA7075-T6 sample demonstrated an outstanding yield strength of 505 MPa.",
                "Tensile strength reached 570 MPa, with density measured as 2.81 g/cm3 and hardness of 150 HV."
            ]
        }
        results = self.extractor.batch_extract_from_papers([paper_obj])
        self.assertGreaterEqual(len(results), 3)
        names = [r["property_name"] for r in results]
        self.assertIn("Yield Strength", names)
        self.assertIn("Tensile Strength", names)
        self.assertIn("Density", names)

    def test_si_conversions(self):
        # Density g/cm3 -> kg/m3
        res = convert_to_si(4.51, "g/cm³", "Density")
        self.assertEqual(res["si_value"], 4510.0)
        self.assertEqual(res["si_unit"], "kg/m³")

        # Temperature deg C -> K
        res_temp = convert_to_si(120.0, "°C", "Curie Temperature")
        self.assertAlmostEqual(res_temp["si_value"], 393.15, places=2)
        self.assertEqual(res_temp["si_unit"], "K")

        # Electrical conductivity S/cm -> S/m
        res_cond = convert_to_si(1.5, "S/cm", "Electrical Conductivity")
        self.assertEqual(res_cond["si_value"], 150.0)
        self.assertEqual(res_cond["si_unit"], "S/m")

if __name__ == "__main__":
    unittest.main()
