from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0030_care_circle_consents"),
    ]

    operations = [
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("scheduled_at", models.DateTimeField()),
                ("duration_minutes", models.PositiveIntegerField(default=30)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("scheduled", "Scheduled"), ("in_progress", "In progress"), ("completed", "Completed"), ("cancelled", "Cancelled"), ("missed", "Missed")], default="scheduled", max_length=32)),
                ("notes", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user"),
                ),
                (
                    "episode",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.episode"),
                ),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization"),
                ),
                (
                    "patient",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.patient"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(max_length=255)),
                ("status", models.CharField(choices=[("open", "Open"), ("assigned", "Assigned"), ("in_progress", "In progress"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="open", max_length=32)),
                ("priority", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")], default="medium", max_length=16)),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assigned_to",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user"),
                ),
                (
                    "created_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_tasks", to="auth.user"),
                ),
                (
                    "episode",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.episode"),
                ),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.organization"),
                ),
                (
                    "work_item",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.workitem"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="workitem",
            name="appointment",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="work_items", to="core.appointment"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["organization", "scheduled_at"], name="core_appoi_organiz_f56448_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["organization", "status"], name="core_appoi_organiz_5f7f28_idx"),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(fields=["organization", "status", "due_at"], name="core_task_organiza_8c3da6_idx"),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(fields=["organization", "priority"], name="core_task_organiza_4b5b31_idx"),
        ),
    ]
