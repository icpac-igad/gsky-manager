import logging
import os
from datetime import datetime
from glob import glob

from dataingestion.nc import clip_by_shp, create_derived
from layermanager.models import Layer, LayerGroup

logger = logging.getLogger(__name__)

TIME_FORMATS = {
    "day": {"format": "%Y%m%d", "index": -8},
    "week": {"format": "%Y%m%d", "index": -8},
    "month": {"format": "%Y%m", "index": -6},
    "year": {"format": "%Y%m", "index": -4}
}


def get_date_from_path(path, d_format):
    t = TIME_FORMATS[d_format]
    date_str = path[t['index']:]
    date = datetime.strptime(date_str, t['format'])
    return date, date_str


def process_layers(path):
    layers = Layer.objects.filter(layer_group__isnull=True)

    layer_groups = LayerGroup.objects.all()

    # match folders
    folders = sorted(glob(f"{path}/202?????"))

    for folder in folders:
        for layer in layers:
            if layer.time_interval and TIME_FORMATS.get(layer.time_interval):
                file_match = layer.file_match
                # match file
                file = glob(f"{folder}/**/{file_match}.nc", recursive=True)
                if file:
                    file = file[0]
                    logger.info(f"Processing layer {layer.name}...")
                    process_layer(file, folder, layer)

        for layer_group in layer_groups:
            file_match = layer_group.file_match
            group_layers = layer_group.layers.all()
            # match file
            file = glob(f"{folder}/**/{file_match}.nc", recursive=True)

            if file:
                file = file[0]
                for g_layer in group_layers:
                    g_layer = g_layer.layer
                    if g_layer.time_interval and TIME_FORMATS.get(g_layer.time_interval):
                        logger.info(f"Processing layer {g_layer.title} ...")
                        process_layer(file, folder, g_layer, is_group=True)


def process_layer(file_path, folder, layer, is_group=False):
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    date, date_str = get_date_from_path(folder, layer.time_interval)

    new_file_path = f"{layer.host_full_path}/{file_name}_{date_str}.nc"

    if is_group and os.path.exists(new_file_path):
        return

        # clip shapefile
    ds = clip_by_shp(file_path)

    ds.to_netcdf(new_file_path)
    ds.close()

    logger.info("Done Processing layer")

    if layer.derived_layers.all():
        for d_layer in layer.derived_layers.all():
            logger.info("Processing Derived layer")
            derived_layer = d_layer.layer
            # create layer by sum/mean across a dimension
            d_ds = create_derived(new_file_path, d_layer.method, d_layer.dimension)
            d_ds = d_ds.rename({layer.variable: derived_layer.variable})
            # clip again
            d_ds = clip_by_shp(d_ds)
            # save to netcdf
            d_ds.to_netcdf(f"{derived_layer.host_full_path}/{derived_layer.file_match}_{date_str}.nc")
            d_ds.close()
            logger.info("Done Processing Derived layer")


def run():
    process_layers("/Users/erickotenyo/Downloads/Data/ICPAC/FORECAST/WEEKLY")
