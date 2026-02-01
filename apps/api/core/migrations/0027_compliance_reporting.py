from __future__ import annotations

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0026_audit_request_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="EvidenceBundle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("manifest", models.JSONField(default=dict)),
                ("artifact_path", models.CharField(blank=True, max_length=512)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
                ("episode", models.ForeignKey(on_delete=models.CASCADE, to="core.episode")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReportJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("name", models.CharField(max_length=200)),
                ("report_type", models.CharField(max_length=120)),
                ("status", models.CharField(default="active", max_length=32)),
                ("interval_days", models.PositiveIntegerField(default=30)),
                ("next_run_at", models.DateTimeField(blank=True, null=True)),
                ("last_run_at", models.DateTimeField(blank=True, null=True)),
                ("params_json", models.JSONField(blank=True, default=dict)),
                ("artifact_path", models.CharField(blank=True, max_length=512)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubmissionRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("due_date", models.DateField()),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(default="pending", max_length=32)),
                ("notes", models.TextField(blank=True)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
                (
                    "episode",
                    models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="core.episode"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
