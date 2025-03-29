import os

import django
from django.core.asgi import get_asgi_application

from at_tutoring_skills.core.arguments import get_args
from at_tutoring_skills.utils.settings import get_django_settings_module

settings_module = get_django_settings_module()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django.setup()

django_application = get_asgi_application()

__all__ = ["django_application", "get_args"]
