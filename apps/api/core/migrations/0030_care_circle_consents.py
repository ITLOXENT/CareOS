from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0029_patient_profiles_domain"),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="restricted",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="CareCircleMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("person_name", models.CharField(max_length=255)),
                ("relationship", models.CharField(max_length=120)),
                ("contact", models.CharField(blank=True, max_length=255)),
                ("notes", models.CharField(blank=True, max_length=255)),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization"),
                ),
                (
                    "patient",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="care_circle", to="core.patient"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="consentrecord",
            name="patient",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.patient"),
        ),
        migrations.AddField(
            model_name="consentrecord",
            name="scope",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="consentrecord",
            name="lawful_basis",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="consentrecord",
            name="granted_by",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="consentrecord",
            name="expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="consentrecord",
            name="revoked_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
