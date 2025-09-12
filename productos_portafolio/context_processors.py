from django.urls import reverse
import requests

def cart_items_count(request):
    cart_product_ids = request.session.get('cart', [])
    # Aquí deberías obtener los productos de la API usando los IDs en la sesión
    # Para simplificar, asumiremos que tienes los datos en tu vista de lista
    return {'cart_count': len(cart_product_ids)}