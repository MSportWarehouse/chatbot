from flask import Flask, request, jsonify
from shopify_api import get_products
import openai
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Cargar credenciales desde .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Instrucciones para el bot
SYSTEM_PROMPT = """
- Solo debes responder con información verificada sobre https://msportwarehouse.com/
- Si no sabes la respuesta, di: 'Lo siento, no tengo esa información en este momento, pero puedes enviar un mensaje directo a través de nuestra página de Instagram o por correo electrónico.'
- No inventes información sobre productos o servicios que no existen en la tienda.
- Mantén las respuestas cortas y claras.
- No proporciones información personal o sensible.
- No proporciones información sobre la competencia.
- No proporciones información sobre el funcionamiento interno de Msportwarehouse.
- No proporciones información sobre la plataforma de chat.
- No proporciones información sobre el funcionamiento interno de OpenAI.
- Vendemos cascos de la marca Arai para competencias de automovilismo y karting.
- Vendemos playeras de corte oversized unisex con diseños de la marca Msportwarehouse todos con temas de automovilismo.
- El envío es gratis solamente en México.
- Nunca puedes mencionar acerca de nuestro inventario o productos que no existen en la tienda porque no se pueden vender.
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "").lower()

    # Detectar palabras clave en la consulta del usuario
    keywords_playeras = ["playeras", "camisas", "t-shirt", "remeras"]
    keywords_cascos = ["casco", "cascos", "helmet"]
    keywords_precios = ["precio", "cuánto cuesta", "coste"]

    productos = get_products()  # Obtener productos de Shopify

    if any(word in user_message for word in keywords_playeras):
        # Filtrar playeras
        playeras = [p for p in productos if "oversized" in p.lower() or "t-shirt" in p.lower()]
        if playeras:
            bot_reply = "Aquí tienes algunas playeras disponibles:\n" + "\n".join(playeras[:5])
        else:
            bot_reply = "No encontré playeras disponibles en este momento."

    elif any(word in user_message for word in keywords_cascos):
        # Filtrar cascos
        cascos = [p for p in productos if "arai" in p.lower() or "bell" in p.lower() or "schuberth" in p.lower()]
        if cascos:
            bot_reply = "Estos son algunos cascos que tenemos disponibles:\n" + "\n".join(cascos[:5])
        else:
            bot_reply = "No encontré cascos disponibles en este momento."

    elif any(word in user_message for word in keywords_precios):
        # Muestra cualquier producto con su precio si preguntan por precios en general
        if productos:
            bot_reply = "Aquí tienes algunos productos con sus precios:\n" + "\n".join(productos[:5])
        else:
            bot_reply = "No tengo información de precios en este momento."

    else:
        # Llamada a OpenAI con contexto de sistema
        client = openai.OpenAI()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response.choices[0].message.content

    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)








