from rest_framework import serializers

from layermanager.models import Layer, LayerGroup, LayerGroupLayer


class LayerSerializer(serializers.ModelSerializer):
    isBoundary = serializers.SerializerMethodField()
    legendConfig = serializers.SerializerMethodField()

    class Meta:
        model = Layer
        fields = ['id', 'title', 'name', 'active', 'sub_category', 'time_interval', 'legendConfig', 'isBoundary']

    @staticmethod
    def get_legendConfig(obj):
        return obj.legend

    @staticmethod
    def get_isBoundary(obj):
        return False


class LayerGroupSerializer(serializers.ModelSerializer):
    layers = serializers.SerializerMethodField()
    default_layer_id = serializers.SerializerMethodField()

    class Meta:
        model = LayerGroup
        fields = ['id', 'name', 'layers', 'sub_category', 'default_layer_id']

    @staticmethod
    def get_layers(obj):
        layers = []
        layers_queryset = obj.layers.all()
        for layer_group_layer in layers_queryset:
            layer_data = LayerSerializer(layer_group_layer.layer).data
            layer_data['sub_category'] = obj.sub_category.id
            layers.append(layer_data)
        return layers

    @staticmethod
    def get_default_layer_id(obj):
        layer = obj.layers.filter(is_default=True).first()
        if not layer and obj.layers.all().exists():
            layer = obj.layers.all().first()

        if layer:
            return layer.layer.id

        return None
