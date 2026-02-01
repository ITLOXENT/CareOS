from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_episodes_workitems"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="pickup_status",
            field=models.CharField(
                choices=[
                    ("not_ready", "Not ready"),
                    ("ready", "Ready"),
                    ("picked_up", "Picked up"),
                ],
                default="not_ready",
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="PatientProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("phone", models.CharField(max_length=32, unique=True)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PatientOTP",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("phone", models.CharField(max_length=32)),
                ("code", models.CharField(max_length=8)),
                ("expires_at", models.DateTimeField()),
                ("used", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="PatientToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("token", models.CharField(max_length=64, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.patientprofile")),
            ],
        ),
        migrations.CreateModel(
            name="MedicationSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("name", models.CharField(max_length=255)),
                ("dosage", models.CharField(blank=True, max_length=120)),
                ("instructions", models.TextField(blank=True)),
                ("times", models.JSONField(default=list)),
                ("timezone", models.CharField(default="UTC", max_length=64)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("active", models.BooleanField(default=True)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.patientprofile")),
            ],
        ),
        migrations.CreateModel(
            name="MedicationDoseEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("taken", "Taken"), ("missed", "Missed")], max_length=16)),
                ("scheduled_for", models.DateTimeField()),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.patientprofile")),
                ("schedule", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.medicationschedule")),
            ],
        ),
        migrations.CreateModel(
            name="CaregiverInvite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("contact", models.CharField(max_length=255)),
                ("channel", models.CharField(default="sms", max_length=32)),
                ("status", models.CharField(choices=[("invited", "Invited"), ("accepted", "Accepted"), ("revoked", "Revoked")], default="invited", max_length=16)),
                ("permissions", models.JSONField(default=list)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.patientprofile")),
            ],
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("message", models.TextField()),
                ("category", models.CharField(blank=True, max_length=120)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.patientprofile")),
            ],
        ),
    ]
