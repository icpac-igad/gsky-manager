import os
import tempfile

import cdsapi
import urllib3
import xarray as xr
from django.conf import settings

from dataingestion.nc import clip_by_shp

urllib3.disable_warnings()

URL = "https://ads.atmosphere.copernicus.eu/api/v2"
ADS_KEY = getattr(settings, "ADS_KEY", "")


def fetch_ads_data(variable, date, path, to_float=True):
    c = cdsapi.Client(url=URL, key=ADS_KEY)

    temp_dir = tempfile.TemporaryDirectory()

    file_name = f"{temp_dir.name}/{date}.nc"

    request = {
        "dataset": "cams-global-atmospheric-composition-forecasts",
        "options": {
            'variable': f'{variable}',
            'date': f'{date}',
            'time': '00:00',
            'leadtime_hour': ['0', '24', '48', '72', '96', '120'],
            'type': 'forecast',
            'format': 'netcdf',
            'area': [-12.5, 21, 24, 52]
        }
    }

    try:
        # retrieve data
        response = c.retrieve(request.get("dataset"), request.get("options"), file_name)

        if os.path.exists(file_name):
            if to_float:
                ds = xr.open_dataset(file_name)
                # try to convert all types to float
                for var in ds.data_vars:
                    if var != "spatia_ref":
                        ds[var] = ds[var].astype(float)
                        ds[var].attrs['_FillValue'] = -9999.0

                ds.to_netcdf(file_name)
                ds.close()

            ds = clip_by_shp(file_name)

            ds.to_netcdf(f"{path}/{date}.nc")

            ds.close()

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
