import json
# import docker

from django.conf import settings

GSKY_CONFIG = getattr(settings, "GSKY_CONFIG")


def update_gsky_config(*args, **kwargs):
    from layermanager.models import Layer
    layers = Layer.objects.filter(active=True)

    config = {

        "service_config": {
            "ows_hostname": GSKY_CONFIG["GSKY_OWS_HOST_NAME"],
            "mas_address": GSKY_CONFIG["GSKY_MAS_ADDRESS"],
            "worker_nodes": GSKY_CONFIG["GSKY_WORKER_NODES"],
        },
        "layers": list(map(lambda layer: layer.gsky_layer, layers))
    }

    with open(GSKY_CONFIG['GSKY_CONFIG_FILE'], 'w') as fp:
        config_str = json.dumps(config)
        fp.write(config_str)


def rgba_dict_to_hex(rgba):
    return '#{:02x}{:02x}{:02x}'.format(rgba['R'], rgba['G'], rgba['B'], rgba['A'])

# def ingest_data(crawl_dir):
#     client = docker.from_env()
#     container = client.containers.get('gsky_server')
#     result = container.exec_run(f"/ingest_data {crawl_dir}")
#     print(result)

# def reload_ows_config():
#     client = docker.from_env()
#     container = client.containers.get('gsky_server')
#     result = container.exec_run("/reload_ows_config.sh")
#     return result




