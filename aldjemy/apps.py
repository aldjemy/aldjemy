from django import VERSION
try:
    from django.apps import AppConfig
except ImportError:
    pass

from .orm import prepare_models


if VERSION >= (1, 7):
    class AldjemyConfig(AppConfig):
        name = 'aldjemy'
        verbose_name = 'Aldjemy'

        def ready(self):
            # Django App registry is ready. Patch models.
            prepare_models()
