import requests
import os
from dotenv import load_dotenv

# Cargar credenciales desde .env
load_dotenv()

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_PASSWORD = os.getenv("SHOPIFY_PASSWORD")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

# Función para obtener productos de Shopify
def get_products():
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/products.json"
    response = requests.get(url, auth=(SHOPIFY_API_KEY, SHOPIFY_PASSWORD))

    if response.status_code == 200:
        products = response.json().get("products", [])
        
        if not products:
            return ["No hay productos disponibles en este momento."]
        
        # Verifica la estructura del JSON y accede a la información correcta
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

# Ejecuta para ver qué devuelve
if __name__ == "__main__":
    productos = get_products()
    print(productos)





