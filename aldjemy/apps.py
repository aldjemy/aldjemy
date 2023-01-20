from django.apps import AppConfig
from django.conf import settings
from django.db.backends import signals
from sqlalchemy import MetaData

from .session import get_session
from .orm import construct_models


def new_session(sender, connection, **kwargs):
    """Create a new session for the given connection."""
    if connection.alias in settings.DATABASES:
        get_session(alias=connection.alias, recreate=True)


class AldjemyConfig(AppConfig):
    name = "aldjemy"
    verbose_name = "Aldjemy"

    def ready(self):
        # Patch models with SQLAlchemy models
        for model, sa_model in construct_models(MetaData()).items():
            model.sa = sa_model

        signals.connection_created.connect(new_session)
