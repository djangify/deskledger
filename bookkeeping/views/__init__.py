# Income views
from .income import (
    income_list,
    income_create,
    income_detail,
    income_edit,
    income_delete,
    export_income_csv,
)

# Expense views
from .expense import (
    expense_list,
    expense_create,
    expense_detail,
    expense_edit,
    expense_delete,
    export_expense_csv,
    ocr_receipt,
)

# Recurring entries
from .recurring import (
    recurring_list,
    recurring_create,
    recurring_edit,
    recurring_delete,
)

# Category exports
from .exports import (
    export_by_category,
    export_categories_screen,
    export_category_csv,
)

# Category management
from .category import (
    category_list,
    category_create,
    category_edit,
    category_delete,
)

# Reports (CSV + print views)
from .reports import (
    income_category_csv,
    income_category_print,
    combined_category_csv,
    combined_category_print,
    yearly_profit_report_csv,
)

__all__ = [
    # Income
    "income_list",
    "income_create",
    "income_detail",
    "income_edit",
    "income_delete",
    "export_income_csv",
    # Expense
    "expense_list",
    "expense_create",
    "expense_detail",
    "expense_edit",
    "expense_delete",
    "export_expense_csv",
    "ocr_receipt",
    # Recurring
    "recurring_list",
    "recurring_create",
    "recurring_edit",
    "recurring_delete",
    # Exports
    "export_by_category",
    "export_categories_screen",
    "export_category_csv",
    # Category management
    "category_list",
    "category_create",
    "category_edit",
    "category_delete",
    # Reports
    "income_category_csv",
    "income_category_print",
    "combined_category_csv",
    "combined_category_print",
    "yearly_profit_report_csv",
]
