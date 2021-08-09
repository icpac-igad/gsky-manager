# Generated by Django 3.2.4 on 2021-08-09 16:52

from django.db import migrations, models
import django.db.models.deletion
import uuid
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('layermanager', '0023_layergrouplayer'),
    ]

    operations = [
        migrations.CreateModel(
            name='LayerMetadata',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique UUID. Auto generated on creation.', primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(blank=True, max_length=255, null=True)),
                ('function', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('resolution', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('geographic_coverage', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('source', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('license', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('frequency_of_updates', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('cautions', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('citation', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('overview', wagtail.core.fields.RichTextField(blank=True, null=True)),
                ('download_data', models.URLField(blank=True, null=True)),
                ('learn_more', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='layer',
            name='metadata',
            field=models.ForeignKey(blank=True, help_text='Layer Metadata', null=True, on_delete=django.db.models.deletion.SET_NULL, to='layermanager.layermetadata'),
        ),
        migrations.AddField(
            model_name='layergroup',
            name='metadata',
            field=models.ForeignKey(blank=True, help_text='Layer Metadata', null=True, on_delete=django.db.models.deletion.SET_NULL, to='layermanager.layermetadata'),
        ),
    ]
