"""
Automated Unit Tests for CrystaGraph V2 Authentication and Research Workspace.
Tests password hashing, JWT token lifecycle, registration, login, and workspace isolation.
"""

import unittest
import os
import sys
import uuid
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from app.api import app
from app.auth import hash_password, verify_password, create_access_token, decode_access_token

class TestAuthAndWorkspace(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.test_email = f"test_prof_{uuid.uuid4().hex[:8]}@bmu.edu.in"
        self.test_password = "SecureAcademicPassword123"

    def test_password_hashing(self):
        hashed = hash_password(self.test_password)
        self.assertNotEqual(hashed, self.test_password)
        self.assertTrue(verify_password(self.test_password, hashed))
        self.assertFalse(verify_password("WrongPassword!", hashed))

    def test_jwt_token_lifecycle(self):
        token = create_access_token({"sub": "user_test_99", "role": "professor"})
        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "user_test_99")
        self.assertEqual(payload["role"], "professor")

    def test_user_registration_and_login_flow(self):
        # 1. Register
        reg_payload = {
            "email": self.test_email,
            "password": self.test_password,
            "full_name": "Dr. Test Researcher",
            "institution": "BML Munjal University",
            "department": "Materials Informatics",
            "role": "professor"
        }
        res_reg = self.client.post("/api/v1/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 201)
        data_reg = res_reg.json()
        self.assertIn("access_token", data_reg)
        self.assertEqual(data_reg["user"]["email"], self.test_email)

        # 2. Duplicate registration should fail
        res_dup = self.client.post("/api/v1/auth/register", json=reg_payload)
        self.assertEqual(res_dup.status_code, 400)

        # 3. Login with correct password
        login_payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        res_login = self.client.post("/api/v1/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        data_login = res_login.json()
        token = data_login["access_token"]
        self.assertIsNotNone(token)

        # 4. Login with wrong password should fail
        res_wrong = self.client.post("/api/v1/auth/login", json={
            "email": self.test_email,
            "password": "BadPassword123"
        })
        self.assertEqual(res_wrong.status_code, 401)

        # 5. Access protected route /api/v1/auth/me
        headers = {"Authorization": f"Bearer {token}"}
        res_me = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        me_data = res_me.json()
        self.assertEqual(me_data["email"], self.test_email)

        # 6. Access protected route without token should fail
        res_unauth = self.client.get("/api/v1/auth/me")
        self.assertEqual(res_unauth.status_code, 401)

    def test_workspace_summary_endpoint(self):
        res = self.client.get("/api/v1/workspace/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("counts", data)
        self.assertIn("recent_papers", data)
        self.assertIn("recent_jobs", data)
        self.assertGreaterEqual(data["counts"]["papers"], 10)

if __name__ == "__main__":
    unittest.main()
