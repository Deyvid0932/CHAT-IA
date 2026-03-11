import ollama
import re

from services.database import model, obtener_conexion


def clean_ai_response(text):

    text = text.replace('*', '')

    text = re.sub(r'(?<!\d)\. ([A-ZÁÉÍÓÚÑ])', r'.\n\n\1', text)

    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

def get_ollama_chat_response(pregunta, contexto, conciseness, speed):
    instrucciones_estilo = {
        "concise": "Sé muy breve, directo y usa listas numeradas si es necesario. Máximo 2-3 frases.",
        "balanced": "Proporciona una respuesta equilibrada, clara y directa.",
        "detailed": "Explica con detalle, profundidad y paso a paso."
    }
    estilo = instrucciones_estilo.get(conciseness, instrucciones_estilo["balanced"])

    opciones = {
        "fast": {"num_predict": 256, "temperature": 0.1},
        "normal": {"num_predict": 756, "temperature": 0.7}
    }
    config = opciones.get(speed, opciones["normal"])

    system_prompt = (
        f"Eres un asistente experto. Estilo requerido: {estilo}\n"
        "REGLAS CRÍTICAS DE FORMATO: No uses asteriscos (**) ni negritas. "
        "Trata de responder el ultimo pdf del usuario donde este sea de foma descendente el ultimo ande como primero y que no se combine la informacion si se llea al minimo de caracteres y resetees "
        "Escribe cada oración en una línea nueva tras un punto. "
        "REGLAS DE CONTEXTO: Utiliza prioritariamente la información de los 'DATOS DEL ARCHIVO' proporcionados. "
        "Si hay varios archivos, prioriza el que aparezca primero en el texto (es el más reciente). "
        "Si la respuesta no está en el contexto, responde con cultura general. "
        "PROHIBICIÓN ABSOLUTA: No menciones jamás las palabras 'PDF', 'documento', 'contexto' , 'información proporcionada' o frases sobre la falta de información en el PDF. "
        "Si no sabes algo por el contexto, NO te justifiques, simplemente responde lo que sepas. "
        "AISLAMIENTO: Ignora archivos de sesiones anteriores. Solo importa el contexto enviado ahora. "
        "Si la respuesta es muy larga trata de acortarla pero termina la idea. "
        "CIERRE: Termina siempre con una pregunta de seguimiento relevante sin mencionar archivos."
    )

    messages = [
        {"role": "system", "content": system_prompt}  # El "Jefe" da las órdenes aquí
    ]

    # Preparamos el contenido del usuario
    contenido_usuario = ""
    if contexto:
        # Ya no limitamos a 10000 caracteres
        contenido_usuario += f"DATOS DEL ARCHIVO:\n{contexto}\n\n"

    contenido_usuario += f"PREGUNTA DEL USUARIO: {pregunta}"

    messages.append({"role": "user", "content": contenido_usuario})

    # Llamada a Ollama con la estructura de roles
    response = ollama.chat(
        model='llama3',
        messages=messages,
        options=config
    )

    raw_response = response['message']['content']
    return clean_ai_response(raw_response)


def buscar_chunks_relevantes(chat_id, pregunta_usuario):
    db = obtener_conexion()
    cursor = db.cursor(dictionary=True)

    # Traemos todos los chunks del chat
    cursor.execute("SELECT contenido_chunk FROM documentos_chunks WHERE chat_id = %s", (chat_id,))
    todos_los_chunks = cursor.fetchall()

    if not todos_los_chunks:
        return ""

    textos = [c['contenido_chunk'] for c in todos_los_chunks]

    # Convertimos pregunta y chunks a vectores
    embeddings_chunks = model.encode(textos)
    embedding_pregunta = model.encode([pregunta_usuario])

    # Calculamos similitud (esto es matemáticas de vectores)
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    similitudes = cosine_similarity(embedding_pregunta, embeddings_chunks)[0]

    # Tomamos los 3 mejores índices
    indices_top = np.argsort(similitudes)[-3:][::-1]

    contexto_final = "\n".join([textos[i] for i in indices_top])

    cursor.close()
    db.close()
    return contexto_final