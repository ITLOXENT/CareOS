from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0027_compliance_reporting"),
    ]

    operations = [
        migrations.CreateModel(
            name="PortalNotification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("kind", models.CharField(default="general", max_length=64)),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField(blank=True)),
                ("url", models.CharField(blank=True, max_length=512)),
                ("unread", models.BooleanField(default=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
                ("patient", models.ForeignKey(on_delete=models.CASCADE, to="core.patient")),
            ],
            options={
                "indexes": [models.Index(fields=["patient", "read_at"], name="core_portal_patient_38a0f3_idx")],
            },
        ),
    ]
