from django.urls import path

from layermanager.views import get_layers

urlpatterns = [
    path('layers/', get_layers, name="layers"),
]
