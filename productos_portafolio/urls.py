from django.urls import path
from . import views

app_name = "productos_portafolio"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("create/", views.product_create, name="product_create"),
    # Nuevas rutas para editar y eliminar, incluyendo el ID del producto
    path("edit/<int:product_id>/", views.product_edit, name="product_edit"),
    path("delete/<int:product_id>/", views.product_delete, name="product_delete"),
]
