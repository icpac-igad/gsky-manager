# Generated by Django 3.2.4 on 2021-08-12 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layermanager', '0024_alter_layer_variable'),
    ]

    operations = [
        migrations.AddField(
            model_name='layer',
            name='file_time_pattern',
            field=models.CharField(blank=True, choices=[('YYY-MM-DD', '(?P<year>\\d\\d\\d\\d)(?P<month>\\d\\d)(?P<day>\\d\\d)'), ('YY-MM', '(?P<year>\\d\\d\\d\\d)(?P<month>\\d\\d)')], help_text='File Time Pattern', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='layer',
            name='file_type',
            field=models.CharField(choices=[('tif', 'Geotiff'), ('nc', 'NetCDF')], default='nc', help_text='File Type', max_length=100),
        ),
    ]
