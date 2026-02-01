from __future__ import annotations

from datetime import datetime, timedelta, timezone as dt_timezone

from django.conf import settings

import stripe

from django.db.models import Sum
from django.utils import timezone

from .models import AIReviewRequest, EvidenceItem, Organization, OrganizationSubscription


def _normalize_currency(value: str | None) -> str:
    return (value or settings.BILLING_DEFAULT_CURRENCY or "GBP").upper()


def _plan_price_id(plan: dict, currency: str) -> str:
    currency_key = f"price_id_{currency.lower()}"
    if plan.get(currency_key):
        return str(plan.get(currency_key))
    if plan.get("prices") and isinstance(plan.get("prices"), dict):
        return str(plan["prices"].get(currency, "")) or ""
    return str(plan.get("price_id", "")) or ""


def get_entitlements(plan_code: str) -> dict:
    entitlements = getattr(settings, "BILLING_ENTITLEMENTS", {})
    return entitlements.get(plan_code, {})


def get_plans(currency: str | None = None) -> list[dict]:
    normalized = _normalize_currency(currency)
    plans = []
    for plan in getattr(settings, "BILLING_PLANS", []):
        price_id = _plan_price_id(plan, normalized)
        plans.append(
            {
                "code": plan.get("code"),
                "name": plan.get("name"),
                "seats": plan.get("seats", 0),
                "currency": normalized,
                "price_id": price_id,
                "entitlements": get_entitlements(str(plan.get("code", ""))),
            }
        )
    return plans


def _plan_lookup_by_price(price_id: str) -> dict | None:
    if not price_id:
        return None
    for plan in getattr(settings, "BILLING_PLANS", []):
        if plan.get("price_id") == price_id:
            return plan
        for currency in ("GBP", "USD"):
            if _plan_price_id(plan, currency) == price_id:
                return plan
    return None


def ensure_stripe_configured() -> None:
    if not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY is required")
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    organization: Organization,
    plan_code: str,
    success_url: str,
    cancel_url: str,
    currency: str | None = None,
) -> dict:
    ensure_stripe_configured()
    normalized = _normalize_currency(currency)
    plans = {plan["code"]: plan for plan in getattr(settings, "BILLING_PLANS", [])}
    if plan_code not in plans:
        raise ValueError("Unknown plan")
    price_id = _plan_price_id(plans[plan_code], normalized)
    if not price_id:
        raise RuntimeError("Price not configured for currency")
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=None,
        metadata={
            "organization_id": organization.id,
            "plan_code": plan_code,
            "currency": normalized,
        },
    )
    return {"id": session.id, "url": session.url}


def upsert_subscription_from_stripe(subscription: dict) -> OrganizationSubscription | None:
    metadata = subscription.get("metadata", {}) or {}
    org_id = metadata.get("organization_id")
    plan_code = metadata.get("plan_code")
    currency = _normalize_currency(metadata.get("currency"))
    if not org_id:
        return None
    organization = Organization.objects.filter(id=org_id).first()
    if not organization:
        return None
    price_id = None
    items = subscription.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id")
    plan_from_price = _plan_lookup_by_price(price_id) if price_id else None
    if not plan_code and plan_from_price:
        plan_code = plan_from_price.get("code")
    seat_limit = plan_from_price.get("seats") if plan_from_price else 0
    entitlements = get_entitlements(plan_code or "")
    max_users = entitlements.get("max_users")
    if isinstance(max_users, int) and max_users > seat_limit:
        seat_limit = max_users
    current_period_end = subscription.get("current_period_end")
    period_end = None
    if current_period_end is not None:
        period_end = datetime.fromtimestamp(current_period_end, tz=dt_timezone.utc)
    subscription_obj, _ = OrganizationSubscription.objects.get_or_create(
        organization=organization
    )
    subscription_obj.stripe_customer_id = subscription.get("customer", "") or ""
    subscription_obj.stripe_subscription_id = subscription.get("id", "") or ""
    subscription_obj.plan_code = plan_code or ""
    subscription_obj.status = subscription.get("status", "inactive")
    subscription_obj.current_period_end = period_end
    subscription_obj.seat_limit = seat_limit or 0
    subscription_obj.save()
    return subscription_obj


def resolve_plan_code(subscription: OrganizationSubscription | None) -> str:
    if subscription and subscription.status in {"active", "trialing"}:
        return subscription.plan_code or settings.BILLING_DEFAULT_PLAN
    return settings.BILLING_DEFAULT_PLAN


def entitlements_for_org(organization: Organization) -> dict:
    subscription = OrganizationSubscription.objects.filter(
        organization=organization
    ).first()
    plan_code = resolve_plan_code(subscription)
    return get_entitlements(plan_code)


def check_evidence_storage_limit(organization: Organization, additional_bytes: int) -> tuple[bool, dict]:
    entitlements = entitlements_for_org(organization)
    limit_mb = entitlements.get("evidence_storage_mb")
    if not isinstance(limit_mb, int):
        return True, {"limit_bytes": None, "used_bytes": None}
    if limit_mb <= 0:
        return False, {"limit_bytes": 0, "used_bytes": 0}
    limit_bytes = limit_mb * 1024 * 1024
    used_bytes = (
        EvidenceItem.objects.filter(organization=organization).aggregate(
            total=Sum("size_bytes")
        )["total"]
        or 0
    )
    projected = used_bytes + max(additional_bytes, 0)
    return projected <= limit_bytes, {
        "limit_bytes": limit_bytes,
        "used_bytes": used_bytes,
    }


def check_ai_review_quota(organization: Organization) -> tuple[bool, dict]:
    entitlements = entitlements_for_org(organization)
    quota = entitlements.get("ai_review_quota")
    if not isinstance(quota, int) or quota <= 0:
        return True, {"limit": None, "used": None}
    window_days = getattr(settings, "BILLING_AI_REVIEW_WINDOW_DAYS", 30)
    since = timezone.now() - timedelta(days=window_days)
    used = AIReviewRequest.objects.filter(
        organization=organization, created_at__gte=since
    ).count()
    return used < quota, {"limit": quota, "used": used}
