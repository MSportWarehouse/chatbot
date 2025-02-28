from flask import Flask, request, jsonify
from flask_cors import CORS
from shopify_api import get_products, get_policies
import openai
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Allow only the Shopify domain
CORS(app, resources={r"/chat": {"origins": "https://msportwarehouse.com"}})

# Load credentials from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Enhanced system prompt with more context
SYSTEM_PROMPT = """
Eres PitStop AI, el asistente oficial de MSPORTWAREHOUSE, una tienda especializada en equipamiento deportivo para motorsports.
Debes responder utilizando solo la información proporcionada desde la base de datos de Shopify.
Menciona específicamente los productos, precios o políticas que aparecen en el contexto proporcionado.
Responde en español de manera amable y profesional.
Si te preguntan por descuentos activos, di que todos los descuentos aparecen publicados por nuestros canales oficiales o en la página web.
No contamos con tienda física actualmente, si preguntan nuestra ubicación di que solamente vendemos en línea. 
Si la información no está disponible, di: 
'Lo siento, no tengo esa información en este momento, pero puedes enviarnos un mensaje directo a través de nuestra página de Instagram @msportwarehouse o por correo electrónico a info@msportwarehouse.com.'
Nunca inventes información ni productos que no estén en el contexto proporcionado.
Los envíos tardan de 7-13 días laborales en procesarse, los costos de importación deben cubrirse por parte de el comprador en caso de que apliquen.
No hay cambios ni devoluciones en cascos, a menos de que estén dañados, para ello, debe contactarnos directamente a través de e-mail
Todas las guías de tallas están publicadas en cada uno de nuestros productos en la tienda en línea. 
Se pueden consultar reseñas/opiniones acerca de nuestros productos a través de TrustPilot
Aceptamos pago con Paypal o tarjetas de crédito
"""

@app.route('/chat', methods=['POST'])
def chat():
    """ Handles chat requests """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    
    if "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"].lower().strip()

    # Get all data from Shopify upfront
    productos = get_products()
    politicas = get_policies()
    
    # Create comprehensive context
    contexto_shopify = ""
    
    # Keywords for different categories
    keywords_map = {
        "playeras": ["playeras", "camisas", "t-shirt", "remeras", "ropa"],
        "cascos": ["casco", "cascos", "helmet", "protección"],
        "precios": ["precio", "cuánto cuesta", "coste", "costo", "vale"],
        "politicas": ["política", "garantía", "reembolso", "devoluciones", "envíos", "shipping"]
    }
    
    # Determine relevant categories based on user message
    relevant_categories = []
    for category, words in keywords_map.items():
        if any(word in user_message for word in words):
            relevant_categories.append(category)
    
    # If no specific categories are detected, include basic information
    if not relevant_categories:
        contexto_shopify = "Información general de la tienda:\n"
        if productos:
            contexto_shopify += f"- Tenemos {len(productos)} productos en total.\n"
        contexto_shopify += "- Somos especialistas en equipamiento para motorsports.\n"
    
    # Add category-specific information to the context
    for category in relevant_categories:
        if category == "playeras":
            playeras = [p for p in productos if any(term in p.lower() for term in ["playera", "oversized", "t-shirt", "camisa", "remera"])]
            if playeras:
                contexto_shopify += f"\nPlayeras disponibles:\n" + "\n".join(playeras[:7])
            else:
                contexto_shopify += "\nNo hay playeras disponibles en este momento."
                
        elif category == "cascos":
            cascos = [p for p in productos if any(term in p.lower() for term in ["casco", "helmet", "arai", "bell", "schuberth"])]
            if cascos:
                contexto_shopify += f"\nCascos disponibles:\n" + "\n".join(cascos[:7])
            else:
                contexto_shopify += "\nNo hay cascos disponibles en este momento."
                
        elif category == "precios":
            if productos:
                contexto_shopify += f"\nProductos con precios:\n" + "\n".join(productos[:7])
            else:
                contexto_shopify += "\nNo hay información de precios disponible."
                
        elif category == "politicas":
            if politicas:
                contexto_shopify += f"\nPolíticas de la tienda:\n" + "\n".join(politicas[:5])
            else:
                contexto_shopify += "\nNo encontré información sobre políticas."
    
    # Always use OpenAI with the appropriate context
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Consulta del usuario: {user_message}"},
                {"role": "assistant", "content": f"Información disponible de Shopify:\n{contexto_shopify}"}
            ],
            temperature=0.7,
            max_tokens=500
        )

        bot_reply = response.choices[0].message.content

    except Exception as e:
        print(f"Error en OpenAI API: {str(e)}")
        bot_reply = "Lo siento, no puedo responder en este momento debido a un problema técnico. Por favor, intenta de nuevo más tarde o contáctanos directamente."

    return jsonify({"response": bot_reply})


if __name__ == "__main__":
    app.run(debug=True)














