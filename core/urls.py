from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("tracks/", views.track_list, name="track_list"),
    path("tracks/<slug:slug>/", views.track_detail, name="track_detail"),
    path("about/", views.about, name="about"),
]
