DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SECRET_KEY = "not-a-secret"
ROOT_URLCONF = "test_project_postgres.urls"
USE_TZ = False  # Silence a warning until Django 5.0

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "sample",
    "aldjemy",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "aldjemy",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    },
}
