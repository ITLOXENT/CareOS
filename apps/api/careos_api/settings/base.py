from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DJANGO_ENV = os.environ.get("DJANGO_ENV", "dev")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DJANGO_ENV in {"prod", "production"} and not DEBUG:
        raise RuntimeError("DJANGO_SECRET_KEY is required in production.")
    SECRET_KEY = "dev-insecure-key"

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1"
).split(",")
CSRF_TRUSTED_ORIGINS = [
    origin
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin
]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "careos_api.observability.RequestContextMiddleware",
    "core.security.SecurityHeadersMiddleware",
    "core.security.LoginRateLimitMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.TenantMiddleware",
]

ROOT_URLCONF = "careos_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "careos_api.wsgi.application"
ASGI_APPLICATION = "careos_api.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 8
SESSION_SAVE_EVERY_REQUEST = True
EVIDENCE_STORAGE_DIR = os.environ.get(
    "EVIDENCE_STORAGE_DIR", str(BASE_DIR / ".data" / "evidence")
)
EXPORT_STORAGE_DIR = os.environ.get("EXPORT_STORAGE_DIR", str(BASE_DIR / ".data" / "exports"))
SLA_WARNING_MINUTES = int(os.environ.get("SLA_WARNING_MINUTES", "60"))
SLA_DEFAULT_MINUTES = int(os.environ.get("SLA_DEFAULT_MINUTES", "120"))
AUTO_CREATE_EPISODE_WORK_ITEM = (
    os.environ.get("AUTO_CREATE_EPISODE_WORK_ITEM", "true").lower() == "true"
)
AUTO_CREATE_APPOINTMENT_WORK_ITEM = (
    os.environ.get("AUTO_CREATE_APPOINTMENT_WORK_ITEM", "true").lower() == "true"
)
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_BEAT_SCHEDULE = {
    "sla-notifications": {
        "task": "core.tasks.check_sla_notifications_task",
        "schedule": 60.0,
    },
    "retention-purge": {
        "task": "core.tasks.purge_retention_task",
        "schedule": 86400.0,
    },
    "compliance-reports": {
        "task": "core.tasks.run_report_jobs_task",
        "schedule": 3600.0,
    },
}
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
BILLING_DEFAULT_CURRENCY = os.environ.get("BILLING_DEFAULT_CURRENCY", "GBP")
BILLING_DEFAULT_PLAN = os.environ.get("BILLING_DEFAULT_PLAN", "starter")
BILLING_AI_REVIEW_WINDOW_DAYS = int(os.environ.get("BILLING_AI_REVIEW_WINDOW_DAYS", "30"))
BILLING_ENTITLEMENTS = {
    "starter": {
        "max_users": 5,
        "evidence_storage_mb": 500,
        "ai_review_quota": 50,
    },
    "pro": {
        "max_users": 25,
        "evidence_storage_mb": 5000,
        "ai_review_quota": 250,
    },
}
BILLING_PLANS = [
    {
        "code": "starter",
        "name": "Starter",
        "price_id_gbp": os.environ.get("STRIPE_PRICE_STARTER_GBP", ""),
        "price_id_usd": os.environ.get("STRIPE_PRICE_STARTER_USD", ""),
        "price_id": os.environ.get("STRIPE_PRICE_STARTER", ""),
        "seats": 5,
    },
    {
        "code": "pro",
        "name": "Pro",
        "price_id_gbp": os.environ.get("STRIPE_PRICE_PRO_GBP", ""),
        "price_id_usd": os.environ.get("STRIPE_PRICE_PRO_USD", ""),
        "price_id": os.environ.get("STRIPE_PRICE_PRO", ""),
        "seats": 25,
    },
]
AI_REVIEW_PROVIDER = os.environ.get("AI_REVIEW_PROVIDER", "mock")
ADMIN_AUDIT_SECRET = os.environ.get("ADMIN_AUDIT_SECRET", "")
ADMIN_AUDIT_ORG_ID = os.environ.get("ADMIN_AUDIT_ORG_ID", "")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "redact": {"()": "careos_api.logging.RedactionFilter"},
        "request_id": {"()": "careos_api.logging.RequestIdFilter"},
    },
    "formatters": {
        "json": {"()": "careos_api.logging.JsonFormatter"},
        "simple": {
            "format": "%(asctime)s %(levelname)s %(name)s %(request_id)s %(org_id)s %(user_id)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["redact", "request_id"],
            "formatter": "simple" if DEBUG else "json",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@careos.local")

INTEROP_SIMULATOR_ENABLED = (
    os.environ.get("INTEROP_SIMULATOR_ENABLED", "false").lower() == "true"
)
