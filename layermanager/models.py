import os
import uuid

from condensedinlinepanel.edit_handlers import CondensedInlinePanel
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.models import Orderable
from wagtail.core.utils import safe_snake_case
from wagtail.snippets.models import register_snippet

from layermanager.utils import rgba_dict_to_hex, update_gsky_config

HOST_DATA_ROOT_PATH = getattr(settings, "HOST_DATA_ROOT_PATH")
CONTAINER_DATA_ROOT_PATH = getattr(settings, "CONTAINER_DATA_ROOT_PATH")

if not HOST_DATA_ROOT_PATH and os.path.isabs(HOST_DATA_ROOT_PATH):
    HOST_DATA_ROOT_PATH = os.path.abspath(HOST_DATA_ROOT_PATH)

GSKY_CONFIG = getattr(settings, "GSKY_CONFIG")


@register_snippet
class GeoCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.CharField(max_length=100,
                                   help_text=f"Will create this sub folder under : {HOST_DATA_ROOT_PATH}/")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @property
    def host_full_path(self):
        path = f"{HOST_DATA_ROOT_PATH}/{self.data_source}"
        return os.path.abspath(path)

    @property
    def container_full_path(self):
        return f"{CONTAINER_DATA_ROOT_PATH}/{self.data_source}"

    def save(self, *args, **kwargs):
        if not os.path.exists(self.host_full_path):
            os.makedirs(self.host_full_path)
        super(GeoCollection, self).save(*args, **kwargs)


@register_snippet
class LayerGroup(ClusterableModel):
    name = models.CharField(max_length=100)
    file_match = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    panels = [
        FieldPanel('name'),
        FieldPanel('file_match'),
        CondensedInlinePanel('layers', heading="Derived Layers", label="Derived Layer"),
    ]


class LayerGroupLayer(Orderable):
    parent = ParentalKey("LayerGroup", related_name='layers')
    is_default = models.BooleanField(default=False)
    layer = models.ForeignKey("Layer", on_delete=models.CASCADE, related_name="layer_group")

    def __str__(self):
        return self.layer.title


@register_snippet
class Layer(ClusterableModel):
    TIME_GENERATOR_CHOICES = (
        ('mas', 'MAS'),
    )

    TIME_INTERVAL_CHOICES = (
        ("day", "Daily"),
        ("week", "Weekly"),
        ("dekad", "Dekadal"),
        ("month", "Monthly"),
        ("season", "Seasonal"),
        ("year", "Yearly"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="Layer Title")
    name = models.CharField(max_length=100, help_text="Layer identifier", unique=True)
    variable = models.CharField(unique=True, max_length=100, help_text="Layer netcdf variable")
    collection = models.ForeignKey('GeoCollection', on_delete=models.PROTECT, related_name='layers')
    time_generator = models.CharField(max_length=100, default='mas', choices=TIME_GENERATOR_CHOICES)
    color_scale = models.ForeignKey('ColorScale', on_delete=models.PROTECT)
    time_interval = models.CharField(max_length=100, choices=TIME_INTERVAL_CHOICES, null=True, blank=True, )
    offset_value = models.FloatField(default=0)
    scale_value = models.FloatField(default=1)
    clip_value = models.FloatField()
    active = models.BooleanField(default=True)
    sub_path = models.CharField(max_length=100)
    file_match = models.CharField(max_length=100, null=True, blank=True)
    shard_name = models.CharField(max_length=100)
    enable_time_series = models.BooleanField(default=False)

    panels = [
        FieldPanel('title'),
        FieldPanel('name'),
        FieldPanel('variable'),
        FieldPanel('collection'),
        FieldPanel('time_generator'),
        FieldPanel('color_scale'),
        FieldPanel('time_interval'),
        FieldPanel('offset_value'),
        FieldPanel('scale_value'),
        FieldPanel('clip_value'),
        FieldPanel('active'),
        FieldPanel('sub_path'),
        FieldPanel('file_match'),
        FieldPanel('enable_time_series'),
        CondensedInlinePanel('derived_layers', heading="Derived Layers", label="Derived Layer"),
    ]

    def __str__(self):
        return f"{self.title} - {self.collection.name}"

    @property
    def gsky_layer(self):
        return {
            "name": self.name,
            "title": self.title,
            "data_source": self.container_full_path,
            "time_generator": self.time_generator,
            "rgb_products": [self.variable],
            "palette": self.color_scale.palette,
            "offset_value": self.offset_value,
            "scale_value": self.scale_value,
            "clip_value": self.clip_value
        }

    @property
    def gsky_process(self):
        gsky_wps_template_file = os.path.join(GSKY_CONFIG['GSKY_WPS_TEMPLATES_CONTAINER_PATH'], f"{self.name}.tpl")
        return {
            "data_source": self.container_full_path,
            "rgb_products": [self.variable],
            "metadata_url": f"{gsky_wps_template_file}"
        }

    @property
    def legend(self):
        return self.color_scale.legend

    @property
    def host_full_path(self):
        path = f"{self.collection.host_full_path}/{self.sub_path}"
        return os.path.abspath(path)

    @property
    def container_full_path(self):
        return f"{self.collection.container_full_path}/{self.sub_path}"

    def save(self, *args, **kwargs):
        # save shard name
        self.shard_name = safe_snake_case(self.name)

        if not os.path.exists(self.host_full_path):
            os.makedirs(self.host_full_path)
        super(Layer, self).save(*args, **kwargs)


class DerivedLayer(Orderable):
    METHODS_CHOICES = (
        ('sum', 'Sum'),
        ('mean', 'Mean'),
    )
    parent = ParentalKey(Layer, related_name='derived_layers')
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE)
    method = models.CharField(choices=METHODS_CHOICES, max_length=100, )
    dimension = models.CharField(max_length=100)

    def __str__(self):
        return self.layer.title


@register_snippet
class ColorScale(ClusterableModel):
    title = models.CharField(max_length=100)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interpolate = models.BooleanField(default=False)
    r = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    g = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    b = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    a = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])

    @property
    def other(self):
        return {"R": self.r, "G": self.g, "B": self.b, "A": self.a}

    @property
    def values(self):
        values = []
        color_values = self.color_values.order_by('threshold')
        for i, c_value in enumerate(color_values):
            value = c_value.value
            # if not the first one, add prev value for later comparison
            if i != 0:
                value['prev'] = color_values[i - 1].threshold
            values.append(value)
        return values

    @property
    def palette(self):
        values = self.values
        colors = []
        for i in range(256):
            v = self.get_color_for_index(i, values, self.other)
            colors.append(v)

        return {"interpolate": self.interpolate, "colours": colors}

    @property
    def legend(self):
        values = self.values
        return list(map(lambda item: {"value": item['threshold'], "color": rgba_dict_to_hex(item['color'])}, values))

    @staticmethod
    def get_color_for_index(index, values, other):
        for i, value in enumerate(values):
            # if it is the first one, check if it less that the threshold
            if i == 0:
                if index < value['threshold']:
                    return value['color']
                # we have only one value in the color list
                if len(values) == 1:
                    return other
                # no match continue
                continue
            # if no the first one, do comparison using also the prev value
            if value.get('prev'):
                if value['prev'] <= index < value['threshold']:
                    return value['color']
                # no match return the value for everything else
                if i == len(values) - 1:
                    return other

    panels = [
        FieldPanel('title'),
        CondensedInlinePanel('color_values', heading="Color Values", label="Color Value"),
        MultiFieldPanel([
            FieldPanel('r'),
            FieldPanel('g'),
            FieldPanel('b'),
            FieldPanel('a'),
        ], "Other"),
        FieldPanel('interpolate'),
    ]

    def __str__(self):
        return self.title


class ColorValue(Orderable):
    layer = ParentalKey('ColorScale', related_name='color_values')
    threshold = models.FloatField()
    name = models.CharField(max_length=100, blank=True, null=True)
    r = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    g = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    b = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    a = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])

    @property
    def value(self):
        return {"threshold": self.threshold, "color": {"R": self.r, "G": self.g, "B": self.b, "A": self.a}}

    def __str__(self):
        return f"{self.r} {self.g} {self.b}, {self.a}"


post_save.connect(update_gsky_config, sender=Layer)
