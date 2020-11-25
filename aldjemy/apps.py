from django.apps import AppConfig

from .orm import prepare_models


class AldjemyConfig(AppConfig):
    name = "aldjemy"
    verbose_name = "Aldjemy"

    def ready(self):
        # Django App registry is ready. Patch models.
        prepare_models()
