"""
Tests for project-level behaviour: login creation, receipt privacy, health.

Run with:  python manage.py test deskledger
"""

import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings

from bookkeeping.models import Category, Expense

User = get_user_model()


class DefaultUserTests(TestCase):
    def test_random_password_not_demo123(self):
        tmp = tempfile.mkdtemp()
        from pathlib import Path

        with override_settings(DATA_DIR=Path(tmp), DEFAULT_USER_PASSWORD=""):
            call_command("create_default_user", stdout=StringIO())
            user = User.objects.get(email="demo@example.com")
            self.assertFalse(user.check_password("demo123"))
            text = (Path(tmp) / "first_login.txt").read_text()
            password = text.split("Password: ")[1].splitlines()[0]
            self.assertTrue(user.check_password(password))

    def test_reset_changes_password(self):
        tmp = tempfile.mkdtemp()
        from pathlib import Path

        with override_settings(DATA_DIR=Path(tmp), DEFAULT_USER_PASSWORD=""):
            call_command("create_default_user", stdout=StringIO())
            old = (Path(tmp) / "first_login.txt").read_text()
            call_command("create_default_user", reset=True, stdout=StringIO())
            new = (Path(tmp) / "first_login.txt").read_text()
            self.assertNotEqual(old, new)
            self.assertEqual(User.objects.count(), 1)

    def test_existing_user_untouched_without_reset(self):
        User.objects.create_user(email="demo@example.com", password="mine-123456")
        call_command("create_default_user", stdout=StringIO())
        self.assertTrue(
            User.objects.get(email="demo@example.com").check_password("mine-123456")
        )


class ReceiptPrivacyTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.owner = User.objects.create_user(email="a@example.com", password="pw-123456")
        self.other = User.objects.create_user(email="b@example.com", password="pw-123456")
        cat = Category.objects.create(name="Misc", category_type="expense")
        self.expense = Expense(
            user=self.owner, category=cat, description="x", amount=10, date="2026-05-01"
        )
        self.expense.receipt.save("r.png", ContentFile(b"\x89PNG\r\n\x1a\n"), save=False)
        self.expense.save()

    def test_anonymous_cannot_fetch_receipt(self):
        resp = self.client.get(self.expense.receipt.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login/", resp["Location"])

    def test_other_user_cannot_fetch_receipt(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.expense.receipt.url).status_code, 404)

    def test_owner_can_fetch_receipt(self):
        self.client.force_login(self.owner)
        resp = self.client.get(self.expense.receipt.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(b"".join(resp.streaming_content)[:4], b"\x89PNG")

    def test_unknown_path_and_traversal_404(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get("/media/../db/db.sqlite3").status_code, 404)
        self.assertEqual(self.client.get("/media/receipts/nope.png").status_code, 404)


class HealthTests(TestCase):
    def test_health(self):
        self.assertEqual(self.client.get("/health/").status_code, 200)

    def test_default_demo_password_rejected(self):
        resp = self.client.post("/login/", {"username": "demo@example.com", "password": "demo123"})
        self.assertEqual(resp.status_code, 200)  # form re-rendered, not logged in
