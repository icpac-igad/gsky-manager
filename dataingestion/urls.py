from django.urls import path

from .views import ingest_data

urlpatterns = [
    path('ingest/', ingest_data, name="ingest_data"),
]
