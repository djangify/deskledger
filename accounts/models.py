from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .fields import EncryptedCharField


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model using email as the unique identifier.
    """

    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    # Currency settings - stored per user so each person sees their preferred symbol
    CURRENCY_CHOICES = [
        ("GBP", "£ British Pound (GBP)"),
        ("EUR", "€ Euro (EUR)"),
        ("USD", "$ US Dollar (USD)"),
    ]
    CURRENCY_SYMBOLS = {
        "GBP": "£",
        "EUR": "€",
        "USD": "$",
    }
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="GBP",
        blank=True,
        help_text="The currency symbol shown throughout the app.",
    )

    @property
    def currency_symbol(self):
        """Return the symbol for the user's selected currency."""
        return self.CURRENCY_SYMBOLS.get(self.currency or "GBP", "£")

    # OCR settings - stored per user so everyone uses their own API key
    OCR_PROVIDER_CHOICES = [
        ("anthropic", "Anthropic (Claude)"),
        ("openai", "OpenAI (GPT-4o)"),
    ]
    ocr_provider = models.CharField(
        max_length=20,
        choices=OCR_PROVIDER_CHOICES,
        default="anthropic",
        blank=True,
    )
    ocr_api_key = EncryptedCharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Your Anthropic or OpenAI API key. Stored encrypted at rest.",
    )

    def has_ocr_configured(self):
        return bool(self.ocr_api_key and self.ocr_api_key.strip())
