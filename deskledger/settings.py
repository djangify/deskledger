"""
DeskLedger Settings
Single settings file - SQLite database
"""

import os
import sys
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Where user data (database, uploaded receipts) is stored.
# When running as a packaged desktop app (PyInstaller .exe), the program files
# live in a temporary, read-only folder, so user data must be written to a
# persistent, writable location instead. For the normal local dev run it
# stays inside the project folder exactly as before.
if getattr(sys, "frozen", False):
    DATA_DIR = Path(
        os.environ.get("LOCALAPPDATA")
        or os.environ.get("APPDATA")
        or Path.home()
    ) / "DeskLedger"
else:
    DATA_DIR = BASE_DIR / "data"

(DATA_DIR / "db").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "media" / "receipts").mkdir(parents=True, exist_ok=True)

# Environment variables
env = environ.Env(DEBUG=(bool, True))
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# Security
SECRET_KEY = env("SECRET_KEY", default="change-me-in-production")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Encryption key for sensitive fields (currently the user's OCR API key — see
# accounts.fields.EncryptedCharField). Prefer an explicit ENCRYPTION_KEY from the
# environment. If none is set (the usual case for the desktop/self-hosted app),
# fall back to a per-install key generated once and persisted OUTSIDE the
# database — and therefore outside the daily DB backups — so encrypted data is
# never readable from a leaked .sqlite3 backup, with zero manual setup.
# NB: it is deliberately NOT derived from SECRET_KEY, which defaults to a public
# constant in desktop mode.
ENCRYPTION_KEY = env("ENCRYPTION_KEY", default="")
if not ENCRYPTION_KEY:
    from cryptography.fernet import Fernet

    _key_file = DATA_DIR / ".encryption_key"
    if _key_file.exists():
        ENCRYPTION_KEY = _key_file.read_text(encoding="utf-8").strip()
    else:
        ENCRYPTION_KEY = Fernet.generate_key().decode("utf-8")
        _key_file.write_text(ENCRYPTION_KEY, encoding="utf-8")
        try:
            os.chmod(_key_file, 0o600)  # best-effort; no-op on some Windows setups
        except OSError:
            pass

# Application definition
INSTALLED_APPS = [
    "adminita",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Allauth
    "allauth",
    "allauth.account",
    # Local apps
    "accounts",
    "bookkeeping",
    "business",
]

AUTH_USER_MODEL = "accounts.User"
SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "secure_uploads.middleware.SecureUploadMiddleware",
    "secure_uploads.middleware.ContentSecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "deskledger.middleware.TaxYearMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "deskledger.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "deskledger.context_processors.version",
                "deskledger.context_processors.tax_year_data",
                "deskledger.context_processors.currency",
            ],
        },
    },
]

WSGI_APPLICATION = "deskledger.wsgi.application"

# Database - SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db" / "db.sqlite3",
    }
}

# Authentication
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Allauth settings
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "first_name*",
    "last_name*",
    "password1*",
    "password2*",
]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = False

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


# WhiteNoise Configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
# Cache static files for 1 year (immutable because of hashed filenames)
WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds

# Desktop (PyWebView) mode: let WhiteNoise serve static files directly from the
# source folders via the staticfiles finders, so the app works even if
# collectstatic hasn't been run.
if os.environ.get("DESKLEDGER_DESKTOP") == "1":
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True

# Media files (receipts etc)
MEDIA_URL = "/media/"
MEDIA_ROOT = DATA_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication URLs
LOGIN_URL = "/login/"
LOGOUT_REDIRECT_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"

# Email — uses SMTP when EMAIL_HOST is set, otherwise logs to console
_email_host = env("EMAIL_HOST", default="")
if _email_host:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = _email_host
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
    ACCOUNT_EMAIL_VERIFICATION = "mandatory"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    ACCOUNT_EMAIL_VERIFICATION = "optional"

# Version
DESKLEDGER_VERSION = "0.1.1"

# Production security (only when DEBUG=False)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host != "*"]


# File size limits
SECURE_UPLOAD_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB (default)

# Image settings
SECURE_UPLOAD_MAX_IMAGE_DIMENSIONS = (4096, 4096)  # Default
SECURE_UPLOAD_MIN_IMAGE_DIMENSIONS = (10, 10)  # Default

# Allowed types
SECURE_UPLOAD_ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
SECURE_UPLOAD_ALLOWED_IMAGE_MIME_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
]

# Document settings (for PDFs, receipts, etc.)
SECURE_UPLOAD_ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".webp"]
SECURE_UPLOAD_ALLOWED_DOCUMENT_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
]

# Security
SECURE_UPLOAD_SANITISE_FILENAMES = True  # Replace filenames with UUIDs
SECURE_UPLOAD_REQUIRE_HTTPS_URLS = True  # Require HTTPS for external URLs
