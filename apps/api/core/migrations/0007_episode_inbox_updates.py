from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_interop_messages"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="membership",
            name="role",
            field=models.CharField(
                choices=[("ADMIN", "Admin"), ("STAFF", "Staff"), ("VIEWER", "Viewer")],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="episode",
            name="patient",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.patientprofile",
            ),
        ),
        migrations.AddField(
            model_name="episode",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="episode",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("triage", "Triage"),
                    ("in_progress", "In progress"),
                    ("blocked", "Blocked"),
                    ("resolved", "Resolved"),
                    ("closed", "Closed"),
                ],
                default="new",
                max_length=32,
            ),
        ),
        migrations.RenameField(
            model_name="episodeevent",
            old_name="actor",
            new_name="created_by",
        ),
        migrations.AddField(
            model_name="episodeevent",
            name="payload_json",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.RenameField(
            model_name="workitem",
            old_name="assignee",
            new_name="assigned_to",
        ),
        migrations.AddField(
            model_name="workitem",
            name="kind",
            field=models.CharField(default="general", max_length=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workitem",
            name="sla_breach_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="workitem",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_work_items",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="workitem",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="workitem",
            name="episode",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="work_items",
                to="core.episode",
            ),
        ),
        migrations.RemoveField(
            model_name="workitem",
            name="title",
        ),
    ]
