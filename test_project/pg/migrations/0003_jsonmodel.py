# Generated by Django 3.1 on 2020-08-21 07:17

import django
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pg", "0002_auto_20170705_1331"),
    ]

    operations = [
        migrations.CreateModel(
            name="JsonModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "value",
                    models.JSONField(),
                ),
            ],
        ),
    ]
