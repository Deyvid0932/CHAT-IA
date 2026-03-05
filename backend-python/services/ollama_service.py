import ollama
import re

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
        "Escribe cada oración en una línea nueva tras un punto. "
        "REGLAS DE CONTEXTO: Si la respuesta no está en el PDF, responde con cultura general. "
        "PROHIBICIÓN ABSOLUTA: No menciones jamás las palabras 'PDF', 'documento', 'contexto' , 'información proporcionada' o 'No hay información específica sobre la prioridad de contexto o el estilo de respuesta en el PDF proporcionado.'. "
        "Si no sabes algo por el PDF, NO te justifiques, simplemente responde lo que sepas. "
        "AISLAMIENTO: Ignora archivos anteriores. Solo importa el contexto enviado ahora. "
        "CIERRE: Termina siempre con una pregunta de seguimiento relevante sin mencionar archivos."
    )

    messages = [
        {"role": "system", "content": system_prompt}  # El "Jefe" da las órdenes aquí
    ]

    # Preparamos el contenido del usuario
    contenido_usuario = ""
    if contexto:
        # Si hay contexto, lo etiquetamos claramente pero sin darle prioridad si el usuario pregunta otra cosa
        contenido_usuario += f"DATOS DEL ARCHIVO:\n{contexto[:8000]}\n\n"

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
