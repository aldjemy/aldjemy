# Generated by Django 5.0.4 on 2024-04-12 03:24

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pg", "0004_daterangemodel"),
    ]

    operations = [
        migrations.CreateModel(
            name="DecimalArrayModel",
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
                    "array",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.DecimalField(decimal_places=3, max_digits=5),
                        max_length=10,
                        size=None,
                    ),
                ),
            ],
        ),
    ]
