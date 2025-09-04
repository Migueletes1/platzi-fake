from django.urls import path
from . import views

app_name = "productos_portafolio"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("create/", views.product_create, name="product_create"),
]
