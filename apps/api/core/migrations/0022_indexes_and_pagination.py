from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0021_export_jobs"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="auditevent",
            index=models.Index(fields=["organization", "created_at"], name="core_audit_o_f5f6ef_idx"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["recipient", "read_at"], name="core_notif_r_f2f7bf_idx"),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(fields=["organization", "created_at"], name="core_episode_o_4f8e8a_idx"),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=models.Index(fields=["organization", "status", "due_at"], name="core_workit_o_c74f5b_idx"),
        ),
    ]
