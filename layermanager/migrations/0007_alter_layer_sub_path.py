# Generated by Django 3.2.4 on 2021-06-07 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layermanager', '0006_remove_derivedlayer_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layer',
            name='sub_path',
            field=models.CharField(max_length=100),
        ),
    ]