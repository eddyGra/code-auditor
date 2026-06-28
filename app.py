import os
from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)

# Inicializamos el cliente de Anthropic con la API key de las variables del entorno

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auditar', methods=['POST'])
def auditar_codigo():
    data = request.get_json()
    codigo = data.get('codigo', '')
    lenguaje = data.get('lenguaje','desconocido')

    if not codigo.strip():
        return jsonify({'error': 'No se proporciono ningun codigo para auditar'}),400

    # Construimos un prompt del sistema estrico para que Claude actue como un auditor experto
    prompt_sistema = (
            "Eres un auditor de seguridad de software esperto y un ingeniero de control de calidad"
            "Tu tarea es analizar el codigo proporcionado por el usuario, identificar vulnerabilidades de seguridad"
            "(Como inyecciones SQL, XSS, desbordamientos, mala gestion de memoria, secretos expuestos, etc)"
            "y proponer solucioes detalladas. Se claro, directo y estructurado en tu respuesta"
            )

    prompt_usuario = f"Por favor, audita el siguiente codigo escrito en {lenguaje}:\n\n```\n{codigo}\n```"

    try:

        response = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                system=prompt_sistema,
                messages=[
                    {"role": "user", "content": prompt_usuario}
                    ]
                )
        resultado_auditoria = response.content[0].text
        return jsonify({'resultado': resultado_auditoria})

    except Exception as e:
        return jsonify({'error': f"Error al comunicarse con la API de claude: {str(e)}"}), 500

if __name__=='__main__':

    app.run(debug=True, port=5000)
