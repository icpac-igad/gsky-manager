# Generated by Django 3.2.4 on 2021-06-14 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layermanager', '0013_alter_layer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='layer',
            name='enable_time_series',
            field=models.BooleanField(default=False),
        ),
    ]