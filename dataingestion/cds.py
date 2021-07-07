import os
import tempfile

import cdsapi
import urllib3
import xarray as xr

from dataingestion.nc import clip_by_shp
from gskymanager.utils import get_object_or_none
from layermanager.models import Layer
from django.conf import settings

urllib3.disable_warnings()

URL = "https://ads.atmosphere.copernicus.eu/api/v2"
ADS_KEY = getattr(settings, "ADS_KEY", "")


def fetch_tcco(date, to_float=False):
    c = cdsapi.Client(url=URL, key=ADS_KEY)

    temp_dir = tempfile.TemporaryDirectory()

    file_name = f"{temp_dir.name}/{date}.nc"

    request = {
        "dataset": "cams-global-atmospheric-composition-forecasts",
        "options": {
            'variable': 'total_column_carbon_monoxide',
            'date': f'{date}',
            'time': '00:00',
            'leadtime_hour': '0',
            'type': 'forecast',
            'format': 'netcdf',
        }
    }

    try:
        # retrieve data
        response = c.retrieve(request.get("dataset"), request.get("options"), file_name)

        layer = get_object_or_none(Layer, name="total_column_carbon_monoxide")

        if layer and os.path.exists(file_name):

            ds = xr.open_dataset(file_name)

            # try to convert all types to float
            for var in ds.data_vars:
                if var != "spatia_ref":
                    ds[var] = ds[var].astype(float)

            ds.to_netcdf(file_name)
            ds.close()

            ds = clip_by_shp(file_name)

            ds.to_netcdf(f"{layer.host_full_path}/{date}.nc")

            return True

        # either file or layer missing
        return False

    except Exception as e:
        # we have an error
        print(e)
        return False
    finally:
        # clean up temporary directory
        temp_dir.cleanup()
