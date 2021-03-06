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
from datetime import date

from layermanager.utils import rgba_dict_to_hex, update_gsky_config

HOST_DATA_ROOT_PATH = getattr(settings, "HOST_DATA_ROOT_PATH")
CONTAINER_DATA_ROOT_PATH = getattr(settings, "CONTAINER_DATA_ROOT_PATH")

if not HOST_DATA_ROOT_PATH and os.path.isabs(HOST_DATA_ROOT_PATH):
    HOST_DATA_ROOT_PATH = os.path.abspath(HOST_DATA_ROOT_PATH)

GSKY_CONFIG = getattr(settings, "GSKY_CONFIG")
OWS_BASE_URL = getattr(settings, "OWS_BASE_URL")


@register_snippet
class DatasetCategory(ClusterableModel):
    title = models.CharField(max_length=25)
    icon = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('icon'),
        FieldPanel('active'),
        FieldPanel('order'),
        CondensedInlinePanel('sub_categories', heading="Sub categories", label="Sub Category"),
    ]

    class Meta:
        ordering = ('order',)
        verbose_name_plural = "Data Categories"

    def __str__(self):
        return self.title


class DatasetSubCategory(Orderable):
    category = ParentalKey('DatasetCategory', related_name='sub_categories')
    title = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Data Sub Categories"
        ordering = ['sort_order']

    def __str__(self):
        return self.title


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    file_match = models.CharField(max_length=255)
    sub_category = models.ForeignKey(DatasetSubCategory, blank=True, null=True, on_delete=models.PROTECT,
                                     help_text="Sub Category")

    def __str__(self):
        return self.name

    panels = [
        FieldPanel('name'),
        FieldPanel('file_match'),
        FieldPanel('sub_category'),
        CondensedInlinePanel('layers', heading="Layers", label="Layer"),
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

    FILE_TYPE_CHOICES = (
        ('tif', "Geotiff"),
        ('nc', "NetCDF"),
    )

    FILE_TIME_PATTERN_CHOICES = (
        (
            "(?P<year>\\d\\d\\d\\d)(?P<month>\\d\\d)(?P<day>\\d\\d).*_(?P<namespace>[\\w\\d_]+)",
            "YYYYMMDD.*_namespace"),
        ("(?P<year>\\d\\d\\d\\d)(?P<month>\\d\\d).*_(?P<namespace>[\\w\\d_]+)", "YYMM.*_namespace"),
        ("_(?P<namespace>[\\w\\d_]+)", "filename_namespace"),
    )

    PIXEL_STAT_CHOICES = (
        ("mean", "Mean"),
        ("sum", "Sum"),
        ("minmaxmean", "Min, Max, Mean"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="Layer Title")
    sub_category = models.ForeignKey(DatasetSubCategory, blank=True, null=True, on_delete=models.PROTECT,
                                     help_text="Sub Category")
    name = models.CharField(max_length=100, help_text="Layer identifier", unique=True)
    variable = models.CharField(max_length=100, help_text="Layer variable")
    collection = models.ForeignKey('GeoCollection', on_delete=models.PROTECT, related_name='layers')
    time_generator = models.CharField(max_length=100, default='mas', choices=TIME_GENERATOR_CHOICES)
    color_scale = models.ForeignKey('ColorScale', on_delete=models.PROTECT)
    time_interval = models.CharField(max_length=100, choices=TIME_INTERVAL_CHOICES, null=True, blank=True, )
    active = models.BooleanField(default=True)
    gsky_active = models.BooleanField(default=True, help_text="Activate in GSKY", verbose_name="Active in GSKY")
    sub_path = models.CharField(max_length=100)
    file_match = models.CharField(max_length=100, null=True, blank=True)
    shard_name = models.CharField(max_length=100)
    enable_time_series = models.BooleanField(default=False)
    file_type = models.CharField(max_length=100, default="nc", choices=FILE_TYPE_CHOICES, help_text="File Type")
    use_file_time_pattern = models.BooleanField(default=False, help_text="Extract time details from file name")
    file_time_pattern = models.CharField(max_length=100, choices=FILE_TIME_PATTERN_CHOICES, blank=True, null=True,
                                         help_text="File Time Pattern")
    pixel_stat = models.CharField(max_length=100, choices=PIXEL_STAT_CHOICES, default='mean',
                                  help_text="Pixel Statistic to Query with WPS")

    panels = [
        FieldPanel('title'),
        FieldPanel('name'),
        FieldPanel('variable'),
        FieldPanel('file_type'),
        FieldPanel('use_file_time_pattern'),
        FieldPanel('file_time_pattern'),
        FieldPanel('collection'),
        FieldPanel('sub_category'),
        FieldPanel('time_generator'),
        FieldPanel('color_scale'),
        FieldPanel('time_interval'),
        FieldPanel('active'),
        FieldPanel('gsky_active'),
        FieldPanel('sub_path'),
        FieldPanel('file_match'),
        FieldPanel('enable_time_series'),
        FieldPanel('pixel_stat'),
        CondensedInlinePanel('derived_layers', heading="Derived Layers", label="Derived Layer"),
    ]

    def __str__(self):
        return f"{self.title} - {self.collection.name}"

    @property
    def wps_identifier(self):
        return f"{self.name}GeometryDrill"

    @property
    def wps_tpl_cols(self):
        if self.pixel_stat == "minmaxmean":
            return "min,max,mean"
        return self.variable

    @property
    def default(self):
        return True

    @property
    def use_file_pattern(self):
        return self.use_file_time_pattern and self.file_time_pattern

    @property
    def tile_url(self):
        default_wms_params = "service=WMS&request=GetMap&version=1.1.1&width=256&height=256&styles=&transparent=true&" \
                             "srs=EPSG:3857&bbox={bbox-epsg-3857}&format=image/png&time={time}"
        return f"{OWS_BASE_URL}?{default_wms_params}&layers={self.name}"

    @property
    def layerConfig(self):
        return {
            "source": {
                "tiles": [self.tile_url],
                "type": "raster"
            },
            "type": "raster"
        }

    @property
    def params(self):
        # We use today as the default and format time as gsky expects it to avoid errors.
        # The frontend should be able to pull all the timestamps and determine the most recent one
        # and use it to update the time param appropriately
        today_timestamp = date.today().strftime("%Y-%m-%dT00:00:00.000Z")
        return {
            "time": today_timestamp
        }

    @property
    def ruleset_path(self):
        return os.path.abspath(GSKY_CONFIG['GSKY_RULESETS_CONTAINER_PATH'])

    @property
    def gsky_layer(self):
        return {
            "name": self.name,
            "title": self.title,
            "data_source": self.container_full_path,
            "time_generator": self.time_generator,
            "rgb_products": [self.variable],
            "palette": self.color_scale.palette,
            "offset_value": self.color_scale.offset_value,
            "scale_value": self.color_scale.scale_value,
            "clip_value": self.color_scale.clip_value
        }

    @property
    def gsky_process(self):

        if self.variable:
            gsky_wps_template_file = os.path.join(GSKY_CONFIG['GSKY_WPS_TEMPLATES_CONTAINER_PATH'], f"{self.name}.tpl")
            return {
                "data_source": self.container_full_path,
                "rgb_products": [self.variable],
                "metadata_url": f"{gsky_wps_template_file}"
            }
        return None

    @property
    def legend(self):
        return {
            "title": self.title,
            "type": self.color_scale.legend_type,
            "items": self.color_scale.legend_items
        }

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
    LEGEND_TYPE_CHOICES = (
        ('basic', 'Basic'),
        ('choropleth', 'Choropleth'),
        ('gradient', 'Gradient'),
    )

    title = models.CharField(max_length=100)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    minimum_val = models.FloatField(default=0, verbose_name="Minimum Value")
    maximum_val = models.FloatField(verbose_name="Maximum Value")
    interpolate = models.BooleanField(default=False)
    legend_type = models.CharField(max_length=100, choices=LEGEND_TYPE_CHOICES, help_text="Legend Type")
    r = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    g = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    b = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    a = models.PositiveIntegerField(default=255, validators=[MaxValueValidator(255), ])
    the_rest_name = models.CharField(max_length=100, blank=True, null=True, help_text="Label",
                                     verbose_name="label")

    @property
    def min_value(self):
        return self.minimum_val

    @property
    def max_value(self):
        max_value = self.maximum_val
        if self.minimum_val == max_value:
            max_value += 0.1
        return max_value

    @property
    def scale_value(self):
        return 254 / (self.max_value - self.minimum_val)

    @property
    def offset_value(self):
        return -self.minimum_val

    @property
    def clip_value(self):
        return self.max_value + self.offset_value

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
            if i == 0:
                value["min_value"] = None
            else:
                value["min_value"] = color_values[i - 1].threshold
            value["max_value"] = value["threshold"]
            values.append(value)
        return values

    @property
    def palette(self):
        colors = []

        if self.interpolate:
            for value in self.values:
                colors.append(value['color'])
            colors.append(self.other)
        else:
            for i in range(256):
                rgba = self.get_color_for_index(i)
                colors.append(rgba)
        return {"interpolate": self.interpolate, "colours": colors}

    def get_color_for_index(self, index_value):
        for value in self.values:
            max_value = value["max_value"] + self.offset_value

            if max_value > self.clip_value:
                max_value = self.clip_value

            if max_value < 0:
                max_value = 0

            max_value = self.scale_value * max_value

            if value["min_value"] is None:
                if index_value <= max_value:
                    return self.values[0]["color"]

            if value["min_value"] is not None:
                min_value = value["min_value"] + self.offset_value

                if min_value > self.clip_value:
                    min_value = self.clip_value

                if min_value < 0:
                    min_value = 0

                min_value = self.scale_value * min_value

                if min_value < index_value <= max_value:
                    return value["color"]

        return self.other

    @property
    def legend_items(self):
        items = []
        values = self.values
        count = len(values)

        if count > 1:
            for i, value in enumerate(values):
                # skip the first one
                if i != 0:
                    item = {"name": value['name'] if value.get('name') else value['threshold'],
                            "color": rgba_dict_to_hex(value['color'])}
                    items.append(item)
            # the_rest_name = self.the_rest_name if self.the_rest_name else values[0]['name']
            #
            # rest_item = {"name": the_rest_name if the_rest_name else f"> {int(values[-1]['threshold'])}",
            #              "color": rgba_dict_to_hex(self.other)}
            # items.append(rest_item)
        else:
            the_rest_name = self.the_rest_name if self.the_rest_name else values[0]['name']
            rest_item = {"name": the_rest_name, "color": rgba_dict_to_hex(self.other)}
            items.append(rest_item)

        return items

    panels = [
        FieldPanel('title'),
        FieldPanel('legend_type'),
        FieldPanel('minimum_val'),
        FieldPanel('maximum_val'),
        CondensedInlinePanel('color_values', heading="Color Values", label="Color Value"),
        MultiFieldPanel([
            FieldPanel('r'),
            FieldPanel('g'),
            FieldPanel('b'),
            FieldPanel('a'),
            FieldPanel('the_rest_name'),
        ], "Other"),
        FieldPanel('interpolate'),
    ]

    def __str__(self):
        return self.title


class ColorValue(Orderable):
    layer = ParentalKey('ColorScale', related_name='color_values')
    threshold = models.FloatField()
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='label')
    r = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    g = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    b = models.PositiveIntegerField(validators=[
        MaxValueValidator(255),
    ])
    a = models.PositiveIntegerField(default=255, validators=[MaxValueValidator(255), ])

    @property
    def value(self):
        return {
            "threshold": self.threshold,
            "color": {"R": self.r, "G": self.g, "B": self.b, "A": self.a},
            "name": self.name
        }

    def __str__(self):
        return f"{self.r} {self.g} {self.b}, {self.a}"


post_save.connect(update_gsky_config, sender=Layer)
