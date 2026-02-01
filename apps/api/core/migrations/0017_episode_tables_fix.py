from __future__ import annotations

from django.db import migrations


def ensure_episode_tables(apps, schema_editor) -> None:
    existing = set(schema_editor.connection.introspection.table_names())
    for model_name in ("Episode", "EpisodeEvent", "WorkItem"):
        model = apps.get_model("core", model_name)
        if model._meta.db_table not in existing:
            schema_editor.create_model(model)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_ai_review"),
    ]

    operations = [
        migrations.RunPython(ensure_episode_tables, reverse_code=migrations.RunPython.noop),
    ]
