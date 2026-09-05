from django.urls import path
from . import views

app_name = "company"

urlpatterns = [
    path("login/", views.company_login, name="login"),
    path("logout/", views.company_logout, name="logout"),
    path("", views.overview, name="overview"),
    path("tracks/", views.track_list, name="track_list"),
    path("tracks/new/", views.track_create, name="track_create"),
    path("tracks/<int:pk>/edit/", views.track_edit, name="track_edit"),
    path("tracks/<int:pk>/delete/", views.track_delete, name="track_delete"),
    path("tracks/<int:track_pk>/tasks/", views.task_list, name="task_list"),
    path("tracks/<int:track_pk>/tasks/new/", views.task_create, name="task_create"),
    path("tracks/<int:track_pk>/tasks/<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("tracks/<int:track_pk>/tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("templates/certificate/", views.certificate_template_upload, name="certificate_template_upload"),
    path("templates/offer-letter/", views.offer_letter_template_upload, name="offer_letter_template_upload"),
]
