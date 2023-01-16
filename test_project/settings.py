from aldjemy.table import foreign_key

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SECRET_KEY = "not-a-secret"
ROOT_URLCONF = "test_project.urls"
SITE_ID = 1
USE_TZ = False  # Silence a warning until Django 5.0

ALDJEMY_ENGINES = {"sqlite3": "sqlite+pysqlite"}
DATABASE_ROUTERS = [
    "test_project.pg.routers.PgRouter",
    "test_project.sample.routers.LogsRouter",
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
    "test_project.sample",
    "test_project.pg",
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
