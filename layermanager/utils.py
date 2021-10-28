import json
# import docker
import os
import re

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import SafeString

GSKY_CONFIG = getattr(settings, "GSKY_CONFIG")


def update_gsky_config(*args, **kwargs):
    from layermanager.models import Layer, LayerGroup
    layers = Layer.objects.filter(active=True)

    config = {
        "service_config": {
            "ows_hostname": GSKY_CONFIG["GSKY_OWS_HOST_NAME"],
            "ows_protocol": GSKY_CONFIG["GSKY_OWS_PROTOCOL"],
            "mas_address": GSKY_CONFIG["GSKY_MAS_ADDRESS"],
            "worker_nodes": GSKY_CONFIG["GSKY_WORKER_NODES"],
        },
        "layers": [],
        "processes": []
    }

    for layer in layers:
        config['layers'].append(layer.gsky_layer)
        if layer.enable_time_series:
            config['processes'].append({
                "data_sources": [layer.gsky_process],
                "identifier": f"{layer.name}GeometryDrill",
                "title": f"{layer.title} Geometry Drill",
                "abstract": "",
                "max_area": 10000,
                "complex_data": [
                    {
                        "identifier": "geometry",
                        "title": "Geometry",
                        "abstract": "",
                        "mime_type": "application/vnd.geo+json",
                        "schema": "http://geojson.org/geojson-spec.html",
                        "min_occurs": 1
                    }
                ],
                "literal_data": [
                    {
                        "identifier": "geometry_id",
                        "title": "Geometry ID"
                    }
                ]
            })

            wps_template_str = render_to_string("wps_template.tpl", {"layer": layer})

            gsky_wps_templates_host_path = os.path.abspath(GSKY_CONFIG['GSKY_WPS_TEMPLATES_HOST_PATH'])

            if not os.path.exists(gsky_wps_templates_host_path):
                os.makedirs(gsky_wps_templates_host_path)

            with open(f"{gsky_wps_templates_host_path}/{layer.name}.tpl", 'w') as wps_t:
                wps_t.write(wps_template_str)

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
            context['layers'].append(l_group_layers[0].layer)

    # handle layer
    for layer in layers:
        context['layers'].append(layer)

    for layer in context['layers']:
        if layer.use_file_pattern:

            file_time_pattern = SafeString(layer.file_time_pattern.replace("\\", "\\\\"))

            ruleset_str = render_to_string("rulesets.tpl",
                                           {"file_time_pattern": file_time_pattern, "extension": layer.file_type})

            rulesets_host_path = os.path.abspath(GSKY_CONFIG['GSKY_RULESETS_HOST_PATH'])

            if not os.path.exists(rulesets_host_path):
                os.makedirs(rulesets_host_path)

            with open(f"{rulesets_host_path}/{layer.name}.json", 'w') as rs_t:
                rs_t.write(ruleset_str)

    sh_template_str = render_to_string("ingest.sh.tpl", context)

    with open(GSKY_CONFIG['GSKY_INGEST_SCRIPT'], 'w') as sh:
        sh.write(sh_template_str)


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
