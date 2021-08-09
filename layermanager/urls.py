from django.urls import path

from layermanager.views import (get_categories, get_layers, get_metadata_by_id, get_metadata_list)

urlpatterns = [
    path('categories/', get_categories, name="categories_list"),
    path('layers/', get_layers, name="layers_list"),
    path('metadata/', get_metadata_list, name="metadata_list"),
    path('metadata/<uuid:pk>/', get_metadata_by_id, name="metadata_detail"),
]
