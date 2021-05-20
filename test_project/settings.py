DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SECRET_KEY = "not-a-secret"
ROOT_URLCONF = "test_project.urls"
SITE_ID = 1

ALDJEMY_ENGINES = {"sqlite3": "sqlite+pysqlite"}
DATABASE_ROUTERS = ["sample.routers.LogsRouter"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "sample",
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
}
