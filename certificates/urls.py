from django.urls import path
from . import views

app_name = "certificates"

urlpatterns = [
    path("offer-letter/preview/", views.offer_letter_preview, name="offer_letter_preview"),
    path("offer-letter/download/", views.offer_letter_download, name="offer_letter_download"),
    path("offer-letter/image/", views.offer_letter_image, name="offer_letter_image"),
    path("certificate/preview/", views.certificate_preview, name="certificate_preview"),
    path("certificate/download/", views.certificate_download, name="certificate_download"),
    path("certificate/image/", views.certificate_image, name="certificate_image"),
]
