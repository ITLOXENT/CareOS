from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_default_form(apps, schema_editor):
    FormTemplate = apps.get_model("core", "FormTemplate")
    FormTemplate.objects.get_or_create(
        name="Episode Intake",
        version=1,
        defaults={
            "schema": {"required": ["symptoms", "notes"], "fields": ["symptoms", "notes"]}
        },
        active=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_patient_medication"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FormTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("name", models.CharField(max_length=255)),
                ("version", models.PositiveIntegerField(default=1)),
                ("schema", models.JSONField(default=dict)),
                ("active", models.BooleanField(default=True)),
            ],
            options={"unique_together": {("name", "version")}},
        ),
        migrations.CreateModel(
            name="FormResponse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("data", models.JSONField(default=dict)),
                ("validated", models.BooleanField(default=False)),
                ("validation_errors", models.JSONField(default=list)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("episode", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.episode")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization")),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.formtemplate")),
            ],
        ),
        migrations.CreateModel(
            name="Signature",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("template_version", models.PositiveIntegerField()),
                ("signed_at", models.DateTimeField(auto_now_add=True)),
                ("response", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.formresponse")),
                ("signer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="EvidencePack",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("manifest", models.JSONField(default=dict)),
                ("pdf_bytes", models.BinaryField()),
                ("episode", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.episode")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization")),
            ],
        ),
        migrations.RunPython(seed_default_form, migrations.RunPython.noop),
    ]
