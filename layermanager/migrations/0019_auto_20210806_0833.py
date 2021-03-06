# Generated by Django 3.2.4 on 2021-08-06 08:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('layermanager', '0018_colorscale_the_rest_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='layergroup',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='colorscale',
            name='the_rest_name',
            field=models.CharField(blank=True, help_text='Label', max_length=100, null=True, verbose_name='label'),
        ),
        migrations.AlterField(
            model_name='colorvalue',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='label'),
        ),
    ]
