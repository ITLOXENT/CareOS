from __future__ import annotations

import pytest
from django.db import connection

from core.models import Episode


@pytest.mark.django_db
def test_episode_table_exists_in_db() -> None:
    tables = set(connection.introspection.table_names())
    assert Episode._meta.db_table in tables
