from flask import Flask, request, jsonify
from flask_cors import CORS
from shopify_api import get_products, get_policies
import openai
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Permitir solo peticiones desde Shopify
CORS(app, resources={r"/chat": {"origins": "https://msportwarehouse.com"}})

# Cargar credenciales desde .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: Falta la clave API de OpenAI. Verifica tu archivo .env.")

# Definir el prompt del chatbot con más contexto
SYSTEM_PROMPT = """
Eres PitStop AI, el asistente oficial de MSPORTWAREHOUSE, una tienda especializada en equipamiento deportivo para motorsports.
Debes responder utilizando solo la información proporcionada desde la base de datos de Shopify.
Menciona específicamente los productos, precios o políticas que aparecen en el contexto proporcionado, de acuerdo con la información que obtengas de la API de shopify.
Responde en español de manera amable y profesional.
Solamente vendemos cascos y playeras

Reglas específicas:
- Si preguntan por descuentos, responde que los descuentos aparecen solo en nuestros canales oficiales o la web.
- No contamos con tienda física, solo vendemos en línea.
- Si no tienes información, responde: 
  "Lo siento, no tengo esa información en este momento. Puedes enviarnos un mensaje a Instagram @msportwarehouse o por correo a info@msportwarehouse.com."
- No inventes información ni productos que no estén en la base de datos.
- Los envíos tardan de 7 a 13 días laborales, y los costos de importación corren por parte del comprador si aplican.
- No hay devoluciones en cascos, a menos que estén dañados (contactar por email).
- Todas las guías de tallas están en la web en cada producto.
- Se pueden ver opiniones de los productos en TrustPilot.
- Métodos de pago aceptados: PayPal y tarjetas de crédito.
"""

# Mapear categorías de productos
PRODUCT_CATEGORIES = {
    "playeras": ["playera", "playeras", "camisas", "t-shirt", "remeras", "ropa", "polera", "jersey"],
    "cascos": ["casco", "cascos", "helmet", "protección", "integral", "modular"],
    "accesorios": ["accesorio", "accesorios", "gadget", "complemento"]
}

# Palabras clave para consultas específicas
QUERY_KEYWORDS = {
    "precios": ["precio", "cuánto cuesta", "coste", "costo", "vale", "valor"],
    "politicas": ["política", "garantía", "reembolso", "devoluciones", "envíos", "entrega"],
    "general": ["productos", "artículos", "catálogo", "disponible", "qué tienes", "que venden"]
}

def get_products_by_category(category):
    """Obtiene productos de Shopify filtrados por categoría."""
    try:
        all_products = get_products()  # Llamada segura a la API
    except Exception as e:
        print(f"❌ Error obteniendo productos de Shopify: {e}")
        return []
    
    # Definir keywords de categorías
    category_keywords = {
        "playeras": ["playera", "t-shirt", "camisa", "jersey", "oversized"],
        "cascos": ["casco", "helmet", "arai", "bell", "schuberth"],
        "accesorios": ["guantes", "zapatos", "traje", "botas", "gafas", "faja"]
    }

    if category not in category_keywords:
        return []

    return [product for product in all_products if any(kw in product.lower() for kw in category_keywords[category])]

@app.route('/chat', methods=['POST'])
def chat():
    """ Maneja las peticiones de chat del usuario. """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    if "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"].lower().strip()
    print(f"📩 Mensaje recibido: {user_message}")

    context = build_context(user_message)
    print(f"📌 Contexto generado:\n{context}")

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Consulta del usuario: {user_message}"},
                {"role": "assistant", "content": f"Información de Shopify:\n{context}"}
            ],
            temperature=0.7,
            max_tokens=500
        )

        bot_reply = response.choices[0].message.content if response.choices else "No pude generar una respuesta."
        print(f"🤖 Respuesta generada: {bot_reply}")

    except Exception as e:
        print(f"❌ Error en OpenAI API: {str(e)}")
        bot_reply = "Lo siento, hubo un problema técnico. Inténtalo más tarde."

    return jsonify({"response": bot_reply})


def build_context(user_message):
    """ Genera contexto basado en la consulta del usuario. """
    context = ""
    products = get_products()  # Obtiene los productos de Shopify como lista de strings

    if not products:
        return "No hay información de productos en este momento."

    matched_products = []

    # Detectar si el usuario pregunta específicamente por playeras
    if any(keyword in user_message.lower() for keyword in ["playera", "playeras", "t-shirt", "camisa", "remera", "polo"]):
        context += "¡Claro que sí! Tenemos disponibles las siguientes playeras:\n"

        for product in products:
            product_lower = product.lower()
            # Busca cualquier coincidencia con palabras clave
            if any(keyword in product_lower for keyword in ["playera", "t-shirt", "camisa", "remera", "polo", "oversized"]):
                matched_products.append(f"🛒 {product}")

        if matched_products:
            context += "\n".join(matched_products[:5])  # Muestra todas las playeras encontradas
        else:
            context += "No encontré playeras en este momento."

        return context  # Termina aquí para evitar añadir más información irrelevante

    # Si la consulta es general sobre productos, devolver un listado
    if any(keyword in user_message.lower() for keyword in ["productos", "qué tienes", "qué venden", "disponible", "catálogo"]):
        context += "Aquí tienes algunos de nuestros productos:\n"
        for product in products[:5]:  # Mostrar solo los primeros 5 productos
            context += f"🛒 {product}\n"
        return context

    # Si la consulta menciona un producto específico, devolver solo ese
    for product in products:
        product_lower = product.lower()

        if any(keyword in product_lower for keyword in user_message.split()):
            matched_products.append(f"🛒 {product}")

    if matched_products:
        context += "\n".join(matched_products[:5])
    else:
        context = "No encontré información sobre ese producto."

    return context


if __name__ == "__main__":
    app.run(debug=True)

