from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bookkeeping.models import Category
from bookkeeping.forms import CategoryForm


@login_required
def category_list(request):
    income_categories = Category.objects.filter(
        category_type="income", is_active=True
    ).order_by("name")
    expense_categories = Category.objects.filter(
        category_type="expense", is_active=True
    ).order_by("name")
    return render(
        request,
        "bookkeeping/category/category_list.html",
        {
            "income_categories": income_categories,
            "expense_categories": expense_categories,
        },
    )


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created.")
            return redirect("bookkeeping:category_list")
    else:
        form = CategoryForm()
    return render(
        request, "bookkeeping/category/category_form.html", {"form": form, "action": "Add"}
    )


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("bookkeeping:category_list")
    else:
        form = CategoryForm(instance=category)
    return render(
        request,
        "bookkeeping/category/category_form.html",
        {"form": form, "action": "Edit", "category": category},
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.is_active = False
        category.save()
        messages.success(request, f'Category "{category.name}" deactivated.')
        return redirect("bookkeeping:category_list")
    return render(
        request,
        "bookkeeping/category/category_confirm_delete.html",
        {"category": category},
    )
