import requests
import os
from dotenv import load_dotenv

# Cargar credenciales desde .env
load_dotenv()

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_PASSWORD = os.getenv("SHOPIFY_PASSWORD")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

HEADERS = {
    "Content-Type": "application/json"
}

# Función para obtener productos de Shopify
def get_products():
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/products.json"
    response = requests.get(url, auth=(SHOPIFY_API_KEY, SHOPIFY_PASSWORD), headers=HEADERS)

    if response.status_code == 200:
        products = response.json().get("products", [])
        
        if not products:
            return ["No hay productos disponibles en este momento."]
        
        product_list = []
        for p in products:
            title = p.get("title", "Producto sin nombre")
            variants = p.get("variants", [])

            if variants:
                price = variants[0].get("price", "Precio no disponible")
                product_list.append(f"{title} - ${price}")
            else:
                product_list.append(f"{title} - Precio no disponible")

        return product_list
    else:
        print("Error al obtener productos de Shopify:", response.status_code, response.text)
        return ["Error al obtener productos."]

# Función para obtener el estado de las órdenes
def get_orders():
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/orders.json"
    response = requests.get(url, auth=(SHOPIFY_API_KEY, SHOPIFY_PASSWORD), headers=HEADERS)

    if response.status_code == 200:
        orders = response.json().get("orders", [])
        return [f"Orden {o['id']} - Estado: {o.get('financial_status', 'Desconocido')}" for o in orders]
    else:
        print("Error al obtener órdenes:", response.status_code, response.text)
        return ["Error al obtener órdenes."]

# # Función para obtener descuentos

# Función para obtener eventos de marketing
def get_marketing_events():
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/marketing_events.json"
    response = requests.get(url, auth=(SHOPIFY_API_KEY, SHOPIFY_PASSWORD), headers=HEADERS)

    if response.status_code == 200:
        events = response.json().get("marketing_events", [])
        return [f"Evento: {e.get('name', 'Sin nombre')} - Tipo: {e.get('event_type', 'Desconocido')}" for e in events]
    else:
        print("Error al obtener eventos de marketing:", response.status_code, response.text)
        return ["Error al obtener eventos de marketing."]

# Función para obtener políticas de la tienda
def get_policies():
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/policies.json"
    response = requests.get(url, auth=(SHOPIFY_API_KEY, SHOPIFY_PASSWORD), headers=HEADERS)

    if response.status_code == 200:
        policies = response.json()
        return [f"{key.capitalize().replace('_', ' ')}: {value}" for key, value in policies.items()]
    else:
        print("Error al obtener políticas:", response.status_code, response.text)
        return ["Error al obtener políticas."]
    
def get_products_by_category(category):
    """
    Fetches products by category from Shopify.
    
    Args:
        category (str): The category name to filter products by
            (e.g., 'playeras', 'cascos', 'guantes', etc.)
    
    Returns:
        list: A list of product strings with their details for the specified category
    """
    # Get all products first
    all_products = get_products()
    
    # Define keyword mappings for categories to filter products
    category_keywords = {
        "playeras": ["playera", "t-shirt", "camisa", "remera", "jersey", "polera", "oversized"],
        "cascos": ["casco", "helmet", "arai", "bell", "schuberth", "integral", "modular"],
        "guantes": ["guante", "glove", "alpinestars", "protection", "hand"],
        "trajes": ["traje", "suit", "overol", "mono", "racing suit", "alpinestars", "sparco"],
        "zapatos": ["zapato", "shoe", "boot", "bota", "calzado", "sparco", "alpinestars"],
        "accesorios": ["accesorio", "accessory", "gadget", "complemento", "soporte", "holder"]
    }
    
    # Check if the category exists in our mapping
    if category not in category_keywords:
        return []
    
    # Filter products that match the category keywords
    filtered_products = []
    keywords = category_keywords[category]
    
    for product in all_products:
        # Convert to lowercase for case-insensitive matching
        product_lower = product.lower()
        
        # Check if any keyword matches
        if any(keyword in product_lower for keyword in keywords):
            filtered_products.append(product)
    
    return filtered_products

# Ejecuta para ver qué devuelve
if __name__ == "__main__":
    print("📦 Productos:", get_products())
    print("📦 Órdenes:", get_orders())
    print("�📢 Eventos de Marketing:", get_marketing_events())
    print("📜 Políticas:", get_policies())





