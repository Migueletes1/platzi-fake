import requests
from django.shortcuts import render, redirect
from django.forms import formset_factory
from django.http import JsonResponse
from .forms import ProductForm

base_url = "https://api.escuelajs.co/api/v1/"

def product_list(request):
    try:
        response = requests.get(f"{base_url}products/", timeout=20)
        response.raise_for_status()
        productos = response.json()
    except requests.RequestException:
        productos = []

    # Extraer categorías únicas
    categorias = sorted({p["category"]["name"] for p in productos})

    # Filtrar por categoría si existe el parámetro GET
    selected = request.GET.get("category", "All")
    if selected != "All":
        productos = [p for p in productos if p["category"]["name"] == selected]

    # Lógica de búsqueda
    search_query = request.GET.get("q")
    if search_query:
        productos = [
            p for p in productos
            if search_query.lower() in p["title"].lower() or search_query.lower() in p["description"].lower()
        ]
    
    # Obtener los productos del carrito para la plantilla
    cart_product_ids = request.session.get('cart', [])
    cart_products = [p for p in productos if p['id'] in cart_product_ids]

    context = {
        "productos": productos,
        "categorias": ["All"] + categorias,
        "selected": selected,
        "cart_products": cart_products,
        "search_query": search_query,
    }
    return render(request, "productos_portafolio/product_list.html", context)

def product_create(request):
    try:
        resp_cat = requests.get(f"{base_url}categories/", timeout=10)
        resp_cat.raise_for_status()
        cats_json = resp_cat.json()
        categories = [(c["id"], c["name"]) for c in cats_json]
    except requests.RequestException:
        categories = []

    if request.method == "POST":
        form = ProductForm(request.POST, categories=categories)
        if form.is_valid():
            payload = {
                "title": form.cleaned_data["title"],
                "price": float(form.cleaned_data["price"]),
                "description": form.cleaned_data["description"],
                "categoryId": int(form.cleaned_data["category"]),
                "images": [form.cleaned_data["image"]],
            }
            try:
                resp_post = requests.post(
                    f"{base_url}products/", json=payload, timeout=10
                )
                resp_post.raise_for_status()
                return redirect("productos_portafolio:product_list")
            except requests.RequestException:
                form.add_error(None, "Error al crear el producto en la API")
    else:
        form = ProductForm(categories=categories)

    return render(request, "productos_portafolio/product_create.html", {"form": form})

def product_edit(request, product_id):
    try:
        resp_prod = requests.get(f"{base_url}products/{product_id}", timeout=10)
        resp_prod.raise_for_status()
        product = resp_prod.json()
    except requests.RequestException:
        return redirect("productos_portafolio:product_list")

    try:
        resp_cat = requests.get(f"{base_url}categories/", timeout=10)
        resp_cat.raise_for_status()
        cats_json = resp_cat.json()
        categories = [(c["id"], c["name"]) for c in cats_json]
    except requests.RequestException:
        categories = []

    if request.method == "POST":
        form = ProductForm(request.POST, categories=categories)
        if form.is_valid():
            payload = {
                "title": form.cleaned_data["title"],
                "price": float(form.cleaned_data["price"]),
                "description": form.cleaned_data["description"],
                "categoryId": int(form.cleaned_data["category"]),
                "images": [form.cleaned_data["image"]],
            }
            try:
                resp_put = requests.put(
                    f"{base_url}products/{product_id}", json=payload, timeout=10
                )
                resp_put.raise_for_status()
                return redirect("productos_portafolio:product_list")
            except requests.RequestException:
                form.add_error(None, "Error al actualizar el producto en la API")
    else:
        form = ProductForm(
            initial={
                "title": product.get("title"),
                "price": product.get("price"),
                "description": product.get("description"),
                "category": product.get("category", {}).get("id"),
                "image": product.get("images", [])[0] if product.get("images") else "",
            },
            categories=categories,
        )

    return render(request, "productos_portafolio/product_edit.html", {"form": form, "product_id": product_id})

def product_delete(request, product_id):
    try:
        requests.delete(f"{base_url}products/{product_id}", timeout=10).raise_for_status()
    except requests.RequestException as e:
        print(f"Error deleting product: {e}")

    return redirect("productos_portafolio:product_list")

# Vista para agregar al carrito con AJAX
def add_to_cart(request, product_id):
    if request.method == "POST":
        if 'cart' not in request.session:
            request.session['cart'] = []
        
        if product_id not in request.session['cart']:
            request.session['cart'].append(product_id)
            request.session.modified = True
            
        return JsonResponse({"status": "success", "cart_count": len(request.session['cart'])})
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

# Vista para eliminar un producto del carrito con AJAX
def remove_from_cart(request, product_id):
    if request.method == "POST":
        if 'cart' in request.session:
            try:
                request.session['cart'].remove(product_id)
                request.session.modified = True
            except ValueError:
                pass
            
        return JsonResponse({"status": "success", "cart_count": len(request.session['cart'])})
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

# Nueva vista para obtener el contenido del carrito (para renderizarlo con JS)
def get_cart_data(request):
    try:
        response = requests.get(f"{base_url}products/", timeout=20)
        response.raise_for_status()
        all_products = response.json()
    except requests.RequestException:
        all_products = []

    cart_product_ids = request.session.get('cart', [])
    cart_products = [p for p in all_products if p['id'] in cart_product_ids]

    # Prepara los datos del carrito para JSON
    cart_data = [{
        'id': p['id'],
        'title': p['title'],
        'price': p['price'],
        'image': p['images'][0] if p['images'] else ''
    } for p in cart_products]

    return JsonResponse({"cart_products": cart_data, "cart_count": len(cart_product_ids)})