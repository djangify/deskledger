# bookkeeping/utils.py
"""
Tax year utilities for UK tax year management (6 April - 5 April)
"""

from datetime import date


def get_current_tax_year():
    """
    Get the current UK tax year.

    Returns:
        str: Current tax year in format "2024-2025"
    """
    today = date.today()
    return get_tax_year_from_date(today)


def get_tax_year_from_date(input_date):
    """
    Calculate UK tax year from a given date.
    """
    if input_date.month < 4 or (input_date.month == 4 and input_date.day < 6):
        return f"{input_date.year - 1}-{input_date.year}"
    else:
        return f"{input_date.year}-{input_date.year + 1}"


def get_tax_year_bounds(tax_year_string):
    """
    Given '2024-2025', return the start and end dates for that tax year.
    """
    start_year = int(tax_year_string.split("-")[0])
    end_year = int(tax_year_string.split("-")[1])

    return date(start_year, 4, 6), date(end_year, 4, 5)


def get_available_tax_years(user):
    """
    Get all tax years that contain data for this user.
    Uses DB-level year extraction to avoid loading all dates into Python memory.
    """
    from django.db.models.functions import ExtractYear
    from bookkeeping.models import Income, Expense

    income_years = (
        Income.objects.filter(user=user)
        .annotate(yr=ExtractYear("date"))
        .values_list("yr", flat=True)
        .distinct()
    )
    expense_years = (
        Expense.objects.filter(user=user)
        .annotate(yr=ExtractYear("date"))
        .values_list("yr", flat=True)
        .distinct()
    )

    # Each calendar year can appear in up to two tax years (before/after April 6)
    calendar_years = set(list(income_years) + list(expense_years))

    if not calendar_years:
        return [get_current_tax_year()]

    # Generate all possible tax years from calendar years
    tax_years = set()
    for yr in calendar_years:
        if yr:
            tax_years.add(f"{yr - 1}-{yr}")
            tax_years.add(f"{yr}-{yr + 1}")

    # Filter to only years that actually have data (avoid phantom years)
    # by checking at least one record falls within each candidate's bounds
    valid = []
    for ty in tax_years:
        start, end = get_tax_year_bounds(ty)
        has_data = (
            Income.objects.filter(user=user, date__gte=start, date__lte=end).exists()
            or Expense.objects.filter(user=user, date__gte=start, date__lte=end).exists()
        )
        if has_data:
            valid.append(ty)

    return sorted(valid, reverse=True) if valid else [get_current_tax_year()]


def format_tax_year_display(tax_year_string):
    return f"Tax Year {tax_year_string}"


def get_tax_year_label(tax_year_string):
    if not tax_year_string:
        return ""
    start_year = tax_year_string.split("-")[0]
    end_year = tax_year_string.split("-")[1][-2:]
    return f"{start_year}/{end_year}"
