from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.core.management.base import BaseCommand

from core.models import Membership, Organization
from core.rbac import Role


class Command(BaseCommand):
    help = "Bootstrap a deterministic admin session for smoke tests."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--org-slug", required=True)
        parser.add_argument("--org-name", default="Smoke Org")
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options) -> None:
        org, _ = Organization.objects.get_or_create(
            slug=options["org_slug"], defaults={"name": options["org_name"]}
        )
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=options["username"], defaults={"email": ""}
        )
        if created or not user.check_password(options["password"]):
            user.set_password(options["password"])
            user.save(update_fields=["password"])
        Membership.objects.get_or_create(
            user=user, organization=org, defaults={"role": Role.ADMIN}
        )

        session = SessionStore()
        session["_auth_user_id"] = user.pk
        session["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
        session["_auth_user_hash"] = user.get_session_auth_hash()
        session.save()

        payload = {
            "session_key": session.session_key,
            "org_id": org.id,
            "user_id": user.id,
        }
        self.stdout.write(json.dumps(payload))
