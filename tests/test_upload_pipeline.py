"""
Unit and integration tests for CrystaGraph Paper Upload and Processing Pipeline.
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))
sys.path.insert(0, PROJECT_ROOT)

from api import app
from pipeline_executor import execute_extraction_pipeline, update_job_status
from components.db_utils import get_connection

class TestUploadPipeline(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_upload_rejects_invalid_file_extension(self):
        """Should return HTTP 400 when non-XML/PDF files are uploaded."""
        files = {"file": ("test.txt", b"plain text data", "text/plain")}
        res = self.client.post("/api/v1/papers/upload", files=files)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unsupported format", res.json()["detail"])

    def test_upload_accepts_valid_xml_and_creates_job(self):
        """Should accept valid XML paper and return 202 Accepted with job_id."""
        sample_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <article>
            <front>
                <article-meta>
                    <article-id pub-id-type="doi">10.1016/j.test.2024.001</article-id>
                    <title-group><article-title>Test Materials Ingestion</article-title></title-group>
                </article-meta>
            </front>
            <body>
                <table-wrap id="tbl1">
                    <caption><p>Sample alloy compositions</p></caption>
                    <table>
                        <thead>
                            <tr><th>Alloy</th><th>Ti (wt.%)</th><th>Al (wt.%)</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>Alloy-A</td><td>90.0</td><td>10.0</td></tr>
                        </tbody>
                    </table>
                </table-wrap>
            </body>
        </article>"""
        files = {"file": ("sample_upload_test.xml", sample_xml, "application/xml")}
        res = self.client.post("/api/v1/papers/upload", files=files)
        self.assertEqual(res.status_code, 202)
        data = res.json()
        self.assertIn("job_id", data)
        self.assertEqual(data["file_type"], "xml")
        self.assertEqual(data["status"], "pending")

        job_id = data["job_id"]

        # Poll status
        status_res = self.client.get(f"/api/v1/jobs/{job_id}")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertEqual(status_data["job_id"], job_id)
        self.assertEqual(status_data["filename"], "sample_upload_test.xml")

    def test_list_jobs_returns_records(self):
        """Should list recent jobs."""
        res = self.client.get("/api/v1/jobs")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_direct_pipeline_execution_sample_xml(self):
        """Verifies direct execution of the extraction pipeline on benchmark paper XML."""
        xml_path = os.path.join(PROJECT_ROOT, "data", "raw_xmls", "paper_01_ti_alloys.xml")
        if not os.path.exists(xml_path):
            self.skipTest("Benchmark XML not found for direct test")

        test_job_id = "test_job_ti_direct"
        # Seed test job
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO extraction_jobs (job_id, filename, file_type, status, progress_pct, current_step)
            VALUES (?, 'paper_01_ti_alloys.xml', 'xml', 'pending', 0, 'Test queued');
        """, (test_job_id,))
        conn.commit()
        conn.close()

        # Run pipeline directly
        execute_extraction_pipeline(
            job_id=test_job_id,
            file_path=xml_path,
            filename="paper_01_ti_alloys.xml",
            file_type="xml"
        )

        # Check job result
        status_res = self.client.get(f"/api/v1/jobs/{test_job_id}")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertEqual(status_data["status"], "completed")
        self.assertEqual(status_data["progress_pct"], 100)
        self.assertGreaterEqual(status_data["extracted_tables_count"], 1)

if __name__ == "__main__":
    unittest.main()
