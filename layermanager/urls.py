from django.urls import path

from layermanager.views import get_categories, get_layers

urlpatterns = [
    path('categories/', get_categories, name="categories"),
    path('layers/', get_layers, name="layers"),
]
