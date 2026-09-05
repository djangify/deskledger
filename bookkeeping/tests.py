"""
Tests for DeskLedger core bookkeeping logic.

Run with:  python manage.py test bookkeeping
"""

from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from bookkeeping.utils import (
    get_tax_year_from_date,
    get_tax_year_bounds,
)
from bookkeeping.models import Income, Expense, Category, RecurringEntry
from bookkeeping.services import run_recurring_for_user

User = get_user_model()


# ============================================================
# TAX YEAR UTILITIES
# ============================================================

class TaxYearFromDateTests(TestCase):
    """get_tax_year_from_date — UK tax year starts 6 April."""

    def test_before_april_6_is_previous_year(self):
        self.assertEqual(get_tax_year_from_date(date(2024, 4, 5)), "2023-2024")

    def test_on_april_6_is_new_year(self):
        self.assertEqual(get_tax_year_from_date(date(2024, 4, 6)), "2024-2025")

    def test_mid_year(self):
        self.assertEqual(get_tax_year_from_date(date(2024, 10, 1)), "2024-2025")

    def test_january_is_previous_year(self):
        self.assertEqual(get_tax_year_from_date(date(2025, 1, 15)), "2024-2025")

    def test_april_5_is_previous_year(self):
        self.assertEqual(get_tax_year_from_date(date(2025, 4, 5)), "2024-2025")

    def test_april_6_starts_new_year(self):
        self.assertEqual(get_tax_year_from_date(date(2025, 4, 6)), "2025-2026")


class TaxYearBoundsTests(TestCase):
    """get_tax_year_bounds — returns correct start/end dates."""

    def test_2024_2025_bounds(self):
        start, end = get_tax_year_bounds("2024-2025")
        self.assertEqual(start, date(2024, 4, 6))
        self.assertEqual(end, date(2025, 4, 5))

    def test_2023_2024_bounds(self):
        start, end = get_tax_year_bounds("2023-2024")
        self.assertEqual(start, date(2023, 4, 6))
        self.assertEqual(end, date(2024, 4, 5))


# ============================================================
# QUARTER CALCULATION
# ============================================================

class QuarterCalculationTests(TestCase):
    """Income._calculate_quarter — UK fiscal quarters."""

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="pass")
        self.cat = Category.objects.create(name="Test Income", category_type="income")

    def _q(self, d):
        obj = Income(
            user=self.user, date=d, description="t",
            amount=Decimal("10"), category=self.cat,
        )
        return obj._calculate_quarter()

    def test_q1_start(self):
        self.assertEqual(self._q(date(2024, 4, 6)), "2024-Q1")

    def test_q1_end(self):
        self.assertEqual(self._q(date(2024, 7, 5)), "2024-Q1")

    def test_q2_start(self):
        self.assertEqual(self._q(date(2024, 7, 6)), "2024-Q2")

    def test_q2_end(self):
        self.assertEqual(self._q(date(2024, 10, 5)), "2024-Q2")

    def test_q3_start(self):
        self.assertEqual(self._q(date(2024, 10, 6)), "2024-Q3")

    def test_q3_crosses_year(self):
        self.assertEqual(self._q(date(2025, 1, 5)), "2024-Q3")

    def test_q4_start(self):
        self.assertEqual(self._q(date(2025, 1, 6)), "2024-Q4")

    def test_q4_end(self):
        self.assertEqual(self._q(date(2025, 4, 5)), "2024-Q4")

    def test_expense_uses_same_logic(self):
        cat = Category.objects.create(name="Test Expense", category_type="expense")
        exp = Expense(
            user=self.user, date=date(2024, 7, 6), description="t",
            amount=Decimal("5"), category=cat,
        )
        self.assertEqual(exp._calculate_quarter(), "2024-Q2")


# ============================================================
# VAT VALIDATION
# ============================================================

class VATValidationTests(TestCase):
    """Expense.clean — VAT amount must match rate within 5p tolerance."""

    def setUp(self):
        self.user = User.objects.create_user(email="vat@example.com", password="pass")
        self.cat = Category.objects.create(name="Supplies", category_type="expense")

    def _expense(self, amount, vat_rate, vat_amount):
        return Expense(
            user=self.user, date=date(2024, 6, 1), description="t",
            amount=Decimal(str(amount)), vat_rate=Decimal(str(vat_rate)),
            vat_amount=Decimal(str(vat_amount)), category=self.cat,
        )

    def test_exact_vat_passes(self):
        from django.core.exceptions import ValidationError
        try:
            self._expense(100, 20, 20).clean()
        except ValidationError:
            self.fail("clean() raised on correct VAT")

    def test_zero_vat_passes(self):
        from django.core.exceptions import ValidationError
        try:
            self._expense(50, 0, 0).clean()
        except ValidationError:
            self.fail("clean() raised on zero VAT")

    def test_rounding_within_tolerance_passes(self):
        from django.core.exceptions import ValidationError
        try:
            self._expense(100, 20, 20.03).clean()
        except ValidationError:
            self.fail("clean() raised on 3p rounding difference")

    def test_large_difference_fails(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self._expense(100, 20, 15).clean()


# ============================================================
# RECURRING ENTRIES
# ============================================================

class RecurringEntryTests(TestCase):
    """RecurringEntry — calculate_next_run date arithmetic."""

    def setUp(self):
        self.user = User.objects.create_user(email="rec@example.com", password="pass")
        self.cat = Category.objects.create(name="Rent", category_type="expense")

    def _entry(self, start, day=1):
        return RecurringEntry.objects.create(
            user=self.user, entry_type="expense", category=self.cat,
            description="Rent", amount=Decimal("500"),
            start_date=start, day_of_month=day,
        )

    def test_first_run_uses_start_date(self):
        entry = self._entry(date(2024, 6, 1))
        self.assertEqual(entry.calculate_next_run(), date(2024, 6, 1))

    def test_advances_one_month(self):
        entry = self._entry(date(2024, 6, 1))
        entry.last_run = date(2024, 6, 1)
        self.assertEqual(entry.calculate_next_run(), date(2024, 7, 1))

    def test_wraps_december_to_january(self):
        entry = self._entry(date(2024, 12, 1))
        entry.last_run = date(2024, 12, 1)
        self.assertEqual(entry.calculate_next_run(), date(2025, 1, 1))

    def test_day_of_month_preserved(self):
        entry = self._entry(date(2024, 6, 15), day=15)
        entry.last_run = date(2024, 6, 15)
        self.assertEqual(entry.calculate_next_run(), date(2024, 7, 15))
