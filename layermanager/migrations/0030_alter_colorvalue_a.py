# Generated by Django 3.2.4 on 2021-11-15 20:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layermanager', '0029_auto_20211115_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colorvalue',
            name='a',
            field=models.PositiveIntegerField(default=255, validators=[django.core.validators.MaxValueValidator(255)]),
        ),
    ]
