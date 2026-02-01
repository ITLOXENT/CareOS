from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0028_portal_notifications"),
    ]

    operations = [
        migrations.CreateModel(
            name="PatientIdentifier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("kind", models.CharField(max_length=64)),
                ("value", models.CharField(max_length=255)),
                ("system", models.CharField(blank=True, max_length=120)),
                ("is_primary", models.BooleanField(default=False)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
                (
                    "patient",
                    models.ForeignKey(on_delete=models.CASCADE, related_name="identifiers", to="core.patient"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PatientAddress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("address_type", models.CharField(default="home", max_length=64)),
                ("line1", models.CharField(max_length=255)),
                ("line2", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(blank=True, max_length=120)),
                ("region", models.CharField(blank=True, max_length=120)),
                ("postal_code", models.CharField(blank=True, max_length=32)),
                ("country", models.CharField(blank=True, max_length=120)),
                ("is_primary", models.BooleanField(default=False)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
                (
                    "patient",
                    models.ForeignKey(on_delete=models.CASCADE, related_name="addresses", to="core.patient"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PatientContactMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("kind", models.CharField(max_length=64)),
                ("value", models.CharField(max_length=255)),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("is_primary", models.BooleanField(default=False)),
                (
                    "organization",
                    models.ForeignKey(on_delete=models.CASCADE, to="core.organization"),
                ),
                (
                    "patient",
                    models.ForeignKey(on_delete=models.CASCADE, related_name="contacts", to="core.patient"),
                ),
            ],
        ),
    ]
