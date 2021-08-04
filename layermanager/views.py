from layermanager.serializers import LayerSerializer, LayerGroupSerializer
from django.http import JsonResponse

from layermanager.models import Layer, LayerGroup


def get_layers(request):
    layer_group_queryset = LayerGroup.objects.all()
    layers_queryset = Layer.objects.filter(layer_group__isnull=True)

    layer_groups_serializer = LayerGroupSerializer(layer_group_queryset, many=True)
    layers_serializer = LayerSerializer(layers_queryset, many=True)

    data = []

    for layer_group in layer_groups_serializer.data:
        dataset = {
            "id": layer_group['id'],
            "name": layer_group['name'],
            "sub_category": layer_group['sub_category'],
            "layer": layer_group['default_layer_id'],
            "layers": layer_group['layers']
        }

        data.append(dataset)

    for layer in layers_serializer.data:
        dataset = {
            "id": layer['id'],
            "name": layer['title'],
            "layer": layer['id'],
            "sub_category": layer['sub_category'],
            "layers": [layer]
        }

        data.append(dataset)

    return JsonResponse(data, safe=False)
