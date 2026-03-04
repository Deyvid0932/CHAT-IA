import ollama
import re

def clean_ai_response(text):

    text = text.replace('*', '')

    text = re.sub(r'(?<!\d)\. ([A-ZÁÉÍÓÚÑ])', r'.\n\n\1', text)

    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Limpiamos espacios en blanco innecesarios
    return text.strip()

def get_ollama_chat_response(pregunta, contexto, conciseness, speed):
    instrucciones_estilo = {
        "concise": "Sé muy breve, directo y usa listas numeradas si es necesario. Máximo 2-3 frases.",
        "balanced": "Proporciona una respuesta equilibrada, clara y directa.",
        "detailed": "Explica con detalle, profundidad y paso a paso."
    }
    estilo = instrucciones_estilo.get(conciseness, instrucciones_estilo["balanced"])

    opciones = {
        "fast": {"num_predict": 256, "temperature": 0.2},
        "normal": {"num_predict": 756, "temperature": 0.7}
    }
    config = opciones.get(speed, opciones["normal"])

    # Instrucción de formato crítica: No usar asteriscos ni markdown, y saltos de línea tras puntos.
    formato_limpio = (
        "IMPORTANTE: No uses asteriscos (**) ni negritas en tu respuesta. "
        "Escribe cada oración en una línea nueva después de un punto final. "
        "Usa párrafos cortos y evita bloques densos de texto."
    )

    instruccion_contexto = (
        "PRIORIDAD DE CONTEXTO: Utiliza exclusivamente el 'Contexto' proporcionado para responder. Si la información necesaria está allí, menciona explícitamente que la respuesta proviene del PDF analizado. Si no está, responde usando tus conocimientos generales pero omite cualquier mención a la falta de información en el archivo o al PDF mismo."
        "VERIFICACIÓN DE IDENTIDAD DEL ARCHIVO: Antes de generar cualquier respuesta, valida si el contenido del contexto actual corresponde a un nuevo documento. Si el usuario sube un archivo diferente, descarta inmediatamente la información de archivos anteriores. Debes analizar el contenido actual desde cero antes de emitir un juicio."
        "COMPARACIÓN ESTRICTA: Al realizar comparaciones, básate únicamente en los documentos que el usuario ha proporcionado en la sesión activa. No mezcles datos de registros antiguos guardados en la base de datos que no hayan sido referenciados explícitamente en la pregunta actual."
        "INTEGRIDAD DE LA RESPUESTA: Prohibido usar frases como 'En el contexto del PDF, no hay información específica'. Si el PDF no tiene la respuesta, simplemente responde de forma natural con tu conocimiento base sin justificar la ausencia en el archivo."
        "PROTOCOLO DE ANÁLISIS PREVIO: (NUEVA REGLA) Antes de responder, realiza un escaneo interno del texto proporcionado para confirmar que estás tratando con la información más reciente. Si detectas que el tema o el contenido ha cambiado respecto a la interacción anterior, prioriza los datos del nuevo documento para evitar respuestas erróneas basadas en archivos obsoletos."
    )

    instruccion_seguimiento = (
        "Al final de tu respuesta, añade SIEMPRE una breve pregunta sugerida "
        "para que el usuario siga explorando el PDF y si no hay en la base de datos el tema tienes la libertad de hacer preguntas. "
        "REGLA OBLIGATORIA: Termina tu respuesta con una pregunta de seguimiento basada en el tema"
    )

    prompt = f"{formato_limpio}\n\n{instruccion_contexto}\n\n{instruccion_seguimiento}\n\nInstrucción de estilo: {estilo}"

    if contexto:
        # Aumentamos a 8000 si es necesario para más contexto
        prompt += f"Contexto del PDF:\n{contexto[:8000]}\n\n"
    prompt += f"Pregunta: {pregunta}"

    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': prompt}
    ], options=config)

    raw_response = response['message']['content']
    
    # Aplicamos la limpieza final por si la IA ignora las instrucciones del prompt
    return clean_ai_response(raw_response)


def generate_pdf_summary():

    response = ollama.chat(model='llama3', messages=[
        {'role': 'user'}
    ])
    
    return clean_ai_response(response['message']['content'])
