from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

from .observability import init_error_reporting

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "careos_api.settings.dev")

init_error_reporting()
application = get_wsgi_application()
