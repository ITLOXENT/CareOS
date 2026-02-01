from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_messaging_mvp"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganizationSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("stripe_customer_id", models.CharField(blank=True, max_length=120)),
                ("stripe_subscription_id", models.CharField(blank=True, max_length=120)),
                ("plan_code", models.CharField(blank=True, max_length=64)),
                ("status", models.CharField(default="inactive", max_length=32)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("seat_limit", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscription",
                        to="core.organization",
                    ),
                ),
            ],
        ),
    ]
