# Generated by Django 3.2.4 on 2021-06-08 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layermanager', '0011_alter_layergrouplayer_layer'),
    ]

    operations = [
        migrations.AddField(
            model_name='layer',
            name='shard_name',
            field=models.CharField(default='daily_rainfall', max_length=100),
            preserve_default=False,
        ),
    ]