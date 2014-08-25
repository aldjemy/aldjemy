# In this file we import all django models and patch them
from django import VERSION

from .orm import prepare_models


if VERSION < (1, 7):
    prepare_models()
