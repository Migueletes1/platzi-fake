from django.urls import path
from . import views

app_name = "productos_portafolio"

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),
    # URLs para AJAX
    path('products/add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('products/remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('get_cart_data/', views.get_cart_data, name='get_cart_data'),
]