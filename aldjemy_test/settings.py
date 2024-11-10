from aldjemy.table import foreign_key

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SECRET_KEY = "not-a-secret"
ROOT_URLCONF = "aldjemy_test.urls"
SITE_ID = 1
USE_TZ = False  # Silence a warning until Django 5.0

# TODO: Test removing these settings
ALDJEMY_ENGINES = {"sqlite3": "sqlite+pysqlite"}
DATABASE_ROUTERS = [
    "aldjemy_test.pg.routers.PgRouter",
    "aldjemy_test.sample.routers.LogsRouter",
]

ALDJEMY_DATA_TYPES = {
    "AFakeType": foreign_key,
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "aldjemy_test.sample",
    "aldjemy_test.pg",
    "aldjemy",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "default.db",
    },
    "logs": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "logs.db",
    },
    "pg": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "aldjemy",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    },
}
