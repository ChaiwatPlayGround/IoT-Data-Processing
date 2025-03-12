"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from sensor.views import ingest_sensor_data, get_aggregated_data, get_processed_data, upload_csv

urlpatterns = [
    path("admin/", admin.site.urls),
    path("upload-csv/", upload_csv, name="upload_csv"),
    path("sensor/data/", ingest_sensor_data, name="sensor-data"),
    path("sensor/processed/", get_processed_data, name="sensor-processed"),
    path("sensor/aggregated/", get_aggregated_data, name="sensor-aggregated"),
]
