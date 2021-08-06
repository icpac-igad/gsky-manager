from rest_framework import serializers

from layermanager.models import Layer, LayerGroup, DatasetCategory, DatasetSubCategory


class DatasetSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetSubCategory
        fields = ['id', 'active', 'title', 'sort_order']


class DatasetCategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = DatasetCategory
        fields = ['id', 'icon', 'title', 'active', 'sub_categories']

    @staticmethod
    def get_sub_categories(obj):
        sub_categories = obj.sub_categories.filter(active=True)
        serializer = DatasetSubCategorySerializer(sub_categories, many=True)
        return serializer.data


class LayerSerializer(serializers.ModelSerializer):
    isBoundary = serializers.SerializerMethodField()
    legendConfig = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    dataset = serializers.SerializerMethodField()
    layerConfig = serializers.ReadOnlyField()
    params = serializers.ReadOnlyField()
    default = serializers.ReadOnlyField()
    name = serializers.SerializerMethodField()
    layer_name = serializers.SerializerMethodField()
    fetchTimestamps = serializers.SerializerMethodField()
    data_path = serializers.SerializerMethodField()

    class Meta:
        model = Layer
        fields = [
            'id',
            'dataset',
            'default',
            'active',
            'name',
            'layer_name',
            'category',
            'sub_category',
            'time_interval',
            'layerConfig',
            'legendConfig',
            'isBoundary',
            'params',
            'fetchTimestamps',
            'data_path'
        ]

    @staticmethod
    def get_name(obj):
        return obj.title

    @staticmethod
    def get_layer_name(obj):
        return obj.name

    @staticmethod
    def get_dataset(obj):
        return obj.id

    @staticmethod
    def get_fetchTimestamps(obj):
        return True

    @staticmethod
    def get_data_path(obj):
        return obj.container_full_path

    @staticmethod
    def get_category(obj):
        if obj.sub_category:
            return obj.sub_category.category.id
        return None

    @staticmethod
    def get_legendConfig(obj):
        return obj.legend

    @staticmethod
    def get_isBoundary(obj):
        return False


class LayerGroupSerializer(serializers.ModelSerializer):
    layers = serializers.SerializerMethodField()
    default_layer_id = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = LayerGroup
        fields = ['id', 'name', 'layers', 'category', 'sub_category', 'default_layer_id']

    @staticmethod
    def get_layers(obj):
        layers = []
        layers_queryset = obj.layers.all()
        for layer_group_layer in layers_queryset:
            layer_data = LayerSerializer(layer_group_layer.layer).data
            layer_data['category'] = obj.sub_category.category.id
            layer_data['dataset'] = obj.id
            layer_data['default'] = layer_group_layer.is_default
            layer_data['isMultiLayer'] = True
            if not layer_data['default']:
                layer_data['nestedLegend'] = True
            layer_data['sub_category'] = obj.sub_category.id
            layers.append(layer_data)
        return layers

    @staticmethod
    def get_category(obj):
        if obj.sub_category:
            return obj.sub_category.category.id
        return None

    @staticmethod
    def get_default_layer_id(obj):
        layer = obj.layers.filter(is_default=True).first()
        if not layer and obj.layers.all().exists():
            layer = obj.layers.all().first()

        if layer:
            return layer.layer.id

        return None
