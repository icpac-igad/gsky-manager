import os

import geopandas as gpd
import rioxarray as rxr
import xarray
import xarray as xr
from django.conf import settings
from shapely.geometry import mapping


def clip_by_shp(dataset):
    shp_path = os.path.join(settings.SHP_FILES_ROOT, "gha/gha.shp")
    gdf = gpd.read_file(shp_path)

    ds = write_projection(dataset)

    ds = ds.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True)

    del ds.x.attrs['axis']
    del ds.x.attrs['long_name']
    del ds.x.attrs['standard_name']
    del ds.x.attrs['units']

    del ds.y.attrs['axis']
    del ds.y.attrs['long_name']
    del ds.y.attrs['standard_name']
    del ds.y.attrs['units']

    # ds.x.attrs['units'] = "degrees_east"
    # ds.y.attrs['units'] = "degrees_north"

    return ds


def write_projection(ds):
    if not isinstance(ds, xarray.Dataset):
        ds = rxr.open_rasterio(ds, decode_times=False)

    ds = ds.rio.write_crs("epsg:4326", inplace=True)

    ds.spatial_ref.attrs[
        'crs_wkt'] = "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AXIS[\"Longitude\",EAST],AXIS[\"Latitude\",NORTH],AUTHORITY[\"EPSG\",\"4326\"]]"
    ds.spatial_ref.attrs[
        'spatial_ref'] = "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AXIS[\"Longitude\",EAST],AXIS[\"Latitude\",NORTH],AUTHORITY[\"EPSG\",\"4326\"]]"
    # ds.x.attrs['units'] = "degrees_east"
    # ds.y.attrs['units'] = "degrees_north"

    # rioxarray has issues with assigning multiple units for multi-temporal data.
    # we only need one
    if isinstance(ds, xarray.DataArray):
        units = ds.attrs.get('units')
        if units and isinstance(units, tuple):
            ds.attrs['units'] = units[0]
    return ds


def create_derived(data_path, method, dimension):
    with xr.open_dataset(data_path) as ds:
        try:
            if method == 'sum':
                ds = ds.sum(dim=dimension)
            elif method == 'mean':
                ds = ds.mean(dim=dimension)
            else:
                # TODO: implement other computations
                raise NotImplementedError()
        except Exception as e:
            raise e
        return ds
