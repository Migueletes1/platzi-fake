import requests
from django.shortcuts import render, redirect
from django.forms import formset_factory
from .forms import ProductForm

base_url = "https://api.escuelajs.co/api/v1/"

def product_list(request):
    try:
        response = requests.get(f"{base_url}products/", timeout=20)
        response.raise_for_status()
        productos = response.json()
    except requests.RequestException:
        productos = []

    categorias = sorted({p["category"]["name"] for p in productos})

    selected = request.GET.get("category", "All")
    if selected != "All":
        productos = [p for p in productos if p["category"]["name"] == selected]

    context = {
        "productos": productos,
        "categorias": ["All"] + categorias,
        "selected": selected,
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

# Nueva vista para editar un producto
def product_edit(request, product_id):
    product = None
    categories = []

    # Obtener el producto existente
    try:
        resp_prod = requests.get(f"{base_url}products/{product_id}", timeout=10)
        resp_prod.raise_for_status()
        product = resp_prod.json()
    except requests.RequestException:
        # Si no se encuentra el producto, redirigir al listado o mostrar un error
        return redirect("productos_portafolio:product_list")

    # Obtener categorías (siempre)
    try:
        resp_cat = requests.get(f"{base_url}categories/", timeout=10)
        resp_cat.raise_for_status()
        cats_json = resp_cat.json()
        categories = [(c["id"], c["name"]) for c in cats_json]
    except requests.RequestException:
        # Manejar error si no se pueden obtener las categorías
        pass # O puedes añadir un mensaje de error al formulario

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
        # Pre-llenar el formulario con los datos del producto
        form = ProductForm(
            initial={
                "title": product.get("title"),
                "price": product.get("price"),
                "description": product.get("description"),
                "category": product.get("category", {}).get("id"), # Asegúrate de obtener el ID de la categoría
                "image": product.get("images", [])[0] if product.get("images") else "",
            },
            categories=categories,
        )

    # Renderizar el nuevo template de edición
    return render(request, "productos_portafolio/product_edit.html", {"form": form, "product_id": product_id})

# ... (la vista product_delete y cualquier otra vista) ...
def product_delete(request, product_id):
    try:
        requests.delete(f"{base_url}products/{product_id}", timeout=10).raise_for_status()
    except requests.RequestException as e:
        print(f"Error deleting product: {e}")

    return redirect("productos_portafolio:product_list")