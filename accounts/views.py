from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms


class AccountSettingsForm(forms.Form):
    currency = forms.ChoiceField(
        choices=[
            ("GBP", "£ British Pound (GBP)"),
            ("EUR", "€ Euro (EUR)"),
            ("USD", "$ US Dollar (USD)"),
        ],
        label="Currency",
        widget=forms.Select(attrs={"class": "w-full border px-3 py-2 rounded"}),
        help_text="The currency symbol shown throughout DeskLedger.",
    )
    ocr_provider = forms.ChoiceField(
        choices=[
            ("anthropic", "Anthropic (Claude Haiku) — recommended"),
            ("openai", "OpenAI (GPT-4o mini)"),
        ],
        label="OCR Provider",
        widget=forms.Select(attrs={"class": "w-full border px-3 py-2 rounded"}),
    )
    ocr_api_key = forms.CharField(
        label="API Key",
        required=False,
        max_length=200,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full border px-3 py-2 rounded font-mono",
                "placeholder": "sk-ant-... or sk-...",
                "autocomplete": "off",
            },
            render_value=True,
        ),
        help_text=(
            "Your Anthropic or OpenAI API key. "
            "This is stored in your account and only used to scan receipts you upload. "
            "Leave blank to disable OCR."
        ),
    )


@login_required
def account_settings(request):
    user = request.user

    if request.method == "POST":
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            user.currency = form.cleaned_data["currency"]
            user.ocr_provider = form.cleaned_data["ocr_provider"]
            new_key = form.cleaned_data.get("ocr_api_key", "").strip()
            # Only update the key if they typed something; blank = keep existing
            if new_key:
                user.ocr_api_key = new_key
            elif "clear_api_key" in request.POST:
                user.ocr_api_key = ""
            user.save(update_fields=["currency", "ocr_provider", "ocr_api_key"])
            messages.success(request, "Settings saved.")
            return redirect("accounts:settings")
    else:
        form = AccountSettingsForm(
            initial={
                "currency": user.currency or "GBP",
                "ocr_provider": user.ocr_provider,
                # Show masked key if set
                "ocr_api_key": user.ocr_api_key if user.ocr_api_key else "",
            }
        )

    return render(
        request,
        "accounts/settings.html",
        {
            "form": form,
            "has_api_key": user.has_ocr_configured(),
        },
    )
