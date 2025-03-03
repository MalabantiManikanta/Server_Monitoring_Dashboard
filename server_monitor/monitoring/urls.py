from django.urls import path
from monitoring.views import dashboard

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
]
