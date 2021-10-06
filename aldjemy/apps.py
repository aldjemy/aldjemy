from django.apps import AppConfig
from sqlalchemy import MetaData

from .orm import construct_models


class AldjemyConfig(AppConfig):
    name = "aldjemy"
    verbose_name = "Aldjemy"

    def ready(self):
        # Patch models with SQLAlchemy models
        for model, sa_model in construct_models(MetaData()).items():
            model.sa = sa_model
