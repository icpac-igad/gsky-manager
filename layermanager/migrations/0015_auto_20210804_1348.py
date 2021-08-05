# Generated by Django 3.2.4 on 2021-08-04 13:48

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('layermanager', '0014_layer_enable_time_series'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatasetCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=25)),
                ('icon', models.CharField(blank=True, max_length=100)),
                ('order', models.PositiveIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Data Categories',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='DatasetSubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('title', models.CharField(max_length=50)),
                ('active', models.BooleanField(default=True)),
                ('category', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_categories', to='layermanager.datasetcategory')),
            ],
            options={
                'verbose_name_plural': 'Data Sub Categories',
                'ordering': ['sort_order'],
            },
        ),
        migrations.AddField(
            model_name='layer',
            name='sub_category',
            field=models.ForeignKey(blank=True, help_text='Sub Category', null=True, on_delete=django.db.models.deletion.PROTECT, to='layermanager.datasetsubcategory'),
        ),
    ]