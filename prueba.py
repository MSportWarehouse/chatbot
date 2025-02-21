import requests
import os
from dotenv import load_dotenv

# Cargar credenciales desde .env
load_dotenv()

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_PASSWORD = os.getenv("SHOPIFY_PASSWORD")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

# Construir la URL de la API de Shopify
SHOPIFY_API_URL = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/products.json"

# Hacer una petición a Shopify usando las credenciales
response = requests.get(SHOPIFY_API_URL, auth=(SHOPIFY_API_KEY, SHOPIFY_PASSWORD))

if response.status_code == 200:
    productos = response.json().get("products", [])
    print("✅ Conexión exitosa con Shopify. Productos disponibles:")
    for product in productos:
        print(f"- {product['title']} (${product['variants'][0]['price']})")
else:
    print(f"❌ Error al conectar con Shopify: {response.status_code}, {response.text}")
