from django.apps import AppConfig
from django.db.models import Model
from sqlalchemy import MetaData
from .orm import construct_models


class BaseSQLAModel:
    @classmethod
    def query(cls, *args, **kwargs):
        raise NotImplementedError(
            "Model.sa.query() is no longer available. "
            "Use the Django connection directly, "
            "or create and use an SQLAlchemy session explicitly. "
            "See https://github.com/aldjemy/aldjemy/issues/296"
        )


def _make_sa_model(model: Model):
    """Create a custom class for the SQLAlchemy model."""
    mixin = getattr(model, "aldjemy_mixin", None)
    bases = (mixin, BaseSQLAModel) if mixin else (BaseSQLAModel,)
    name = f'{model._meta.object_name}.sa'
    return type(name, bases, {"__module__": model.__module__})


class AldjemyConfig(AppConfig):
    name = "aldjemy"
    verbose_name = "Aldjemy"

    def ready(self):
        # Patch models with SQLAlchemy models
        models = construct_models(MetaData(), _make_sa_model=_make_sa_model)
        for model, sa_model in models.items():
            model.sa = sa_model
