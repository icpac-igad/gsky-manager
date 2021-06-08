import logging
import os
from datetime import datetime
from glob import glob
import numpy as np

from dataingestion.nc import clip_by_shp, create_derived
from layermanager.models import Layer, LayerGroup

logger = logging.getLogger(__name__)

TIME_FORMATS = {
    "day": {"format": "%Y%m%d", "index": -8},
    "week": {"format": "%Y%m%d", "index": -8},
    "month": {"format": "%Y%m", "index": -6},
    "year": {"format": "%Y%m", "index": -4}
}

PATTERN = "202?????"


def get_date_from_path(path, d_format):
    t = TIME_FORMATS[d_format]
    date_str = path[t['index']:]
    date = datetime.strptime(date_str, t['format'])
    return date, date_str


def process_layers(path, skip_existing=False):
    layers = Layer.objects.filter(layer_group__isnull=True, active=True)

    processed_some = False

    layer_groups = LayerGroup.objects.all()

    # match folders
    folders = sorted(glob(f"{path}/{PATTERN}"))

    if not folders:
        logger.info(f"[INGEST]: No folders matching pattern '{PATTERN}'")

    for folder in folders:
        for layer in layers:
            if layer.time_interval and TIME_FORMATS.get(layer.time_interval):
                file_match = layer.file_match
                # match file
                file = glob(f"{folder}/**/{file_match}.nc", recursive=True)
                if file:
                    file = file[0]
                    logger.info(f"[INGEST]: Processing layer {layer.name}, {file}...")
                    process_layer(file, folder, layer, skip_existing=skip_existing)
                    processed_some = True

        for layer_group in layer_groups:
            file_match = layer_group.file_match
            group_layers = layer_group.layers.filter(layer__active=True)
            # match file
            file = glob(f"{folder}/**/{file_match}.nc", recursive=True)

            if file:
                file = file[0]
                for g_layer in group_layers:
                    g_layer = g_layer.layer
                    if g_layer.time_interval and TIME_FORMATS.get(g_layer.time_interval):
                        logger.info(f"[INGEST]: Processing layer {g_layer.title}, {file} ...")
                        saved = process_layer(file, folder, g_layer, is_group=True, skip_existing=skip_existing)
                        if not processed_some and saved:
                            processed_some = True
    return processed_some


def process_layer(file_path, folder, layer, is_group=False, skip_existing=False):
    saved = False
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    date, date_str = get_date_from_path(folder, layer.time_interval)

    new_file_path = f"{layer.host_full_path}/{file_name}_{date_str}.nc"

    if skip_existing and os.path.exists(new_file_path):
        logger.info("Skipped Existing")
        return

    if is_group and os.path.exists(new_file_path):
        return

        # clip shapefile
    ds = clip_by_shp(file_path)

    if layer.time_interval == 'week':
        t = np.datetime64(date)
        ds = ds.expand_dims(time=[t])

    ds.to_netcdf(new_file_path)
    ds.close()
    saved = True

    logger.info("[INGEST]: Done Processing layer")

    if layer.derived_layers.all():
        for d_layer in layer.derived_layers.all():
            logger.info(f"[INGEST]: Processing Derived layer {d_layer.layer}, {new_file_path}")
            derived_layer = d_layer.layer
            # create layer by sum/mean across a dimension
            d_ds = create_derived(new_file_path, d_layer.method, d_layer.dimension)
            d_ds = d_ds.rename({layer.variable: derived_layer.variable})
            # clip again
            d_ds = clip_by_shp(d_ds)

            if derived_layer.time_interval == 'week':
                t = np.datetime64(date)
                d_ds = d_ds.expand_dims(time=[t])

            # save to netcdf
            d_ds.to_netcdf(f"{derived_layer.host_full_path}/{derived_layer.file_match}_{date_str}.nc",
                           encoding={derived_layer.variable: {"_FillValue": -9999.0, "grid_mapping": "spatial_ref"}})
            d_ds.close()
            saved = True
            logger.info("[INGEST]: Done Processing Derived layer")

    return saved
