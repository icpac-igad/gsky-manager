import json
# import docker

from django.conf import settings
from django.template.loader import render_to_string

GSKY_CONFIG = getattr(settings, "GSKY_CONFIG")


def update_gsky_config(*args, **kwargs):
    from layermanager.models import Layer, LayerGroup
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

    context = {'layers': []}

    layers = Layer.objects.filter(layer_group__isnull=True, active=True)
    layer_groups = LayerGroup.objects.all()

    # handle layer groups
    for l_group in layer_groups:
        l_group_layers = l_group.layers.filter(layer__active=True)
        if l_group_layers:
            context['layers'].append(l_group_layers[0])

    # handle layer
    for layer in layers:
        context['layers'].append(layer)

    template = render_to_string("ingest.sh.html", context)

    with open(GSKY_CONFIG['GSKY_INGEST_SCRIPT'], 'w') as sh:
        sh.write(template)


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
