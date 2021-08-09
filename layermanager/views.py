from gskymanager.utils import get_object_or_none
from layermanager.serializers import LayerSerializer, LayerGroupSerializer, DatasetCategorySerializer, \
    LayerMetadataSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from layermanager.models import Layer, LayerGroup, DatasetCategory, LayerMetadata


def get_categories(request):
    categories_queryset = DatasetCategory.objects.filter(active=True)
    categories_serializer = DatasetCategorySerializer(categories_queryset, many=True)

    return JsonResponse(categories_serializer.data, safe=False)


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
            "metadata": layer_group['metadata'],
            "category": layer_group['category'],
            "sub_category": layer_group['sub_category'],
            "isMultiLayer": True,
            "layer": layer_group['default_layer_id'],
            "layers": layer_group['layers']
        }

        data.append(dataset)

    for layer in layers_serializer.data:
        dataset = {
            "id": layer['id'],
            "name": layer['name'],
            "metadata": layer['metadata'],
            "layer": layer['id'],
            "category": layer['category'],
            "sub_category": layer['sub_category'],
            "layers": [layer]
        }

        data.append(dataset)

    return JsonResponse(data, safe=False)


def get_metadata_list(request):
    metadata_queryset = LayerMetadata.objects.all()
    metadata_serializer = LayerMetadataSerializer(metadata_queryset, many=True)

    return JsonResponse(metadata_serializer.data, safe=False)


def get_metadata_by_id(request, pk):
    metadata_obj = get_object_or_none(LayerMetadata, pk=pk)

    if metadata_obj:
        metadata_serializer = LayerMetadataSerializer(metadata_obj)

        return JsonResponse(metadata_serializer.data, safe=False)

    return JsonResponse({"error": f"Metadata with id '{pk}' does not exist"}, status=404, safe=False)
