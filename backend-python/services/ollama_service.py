import ollama
import re
import chromadb

from config import DB_PATH



def clean_ai_response(text):

    text = text.replace('*', '')

    text = re.sub(r'(?<!\d)\. ([A-ZÁÉÍÓÚÑ])', r'.\n\n\1', text)

    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

def get_ollama_chat_response(question, context, conciseness, speed):
    style_instructions = {
        "concise": "Be very brief and direct. Use numbered lists if necessary. Maximum 3-4 sentences.",
        "balanced": "Provide a balanced, clear, and direct response.",
        "detailed": "Explain in detail, providing depth and a step-by-step breakdown."
    }
    style = style_instructions.get(conciseness, style_instructions["balanced"])

    options = {
        "fast": {"num_predict": 256, "temperature": 0},
        "normal": {"num_predict": 756, "temperature": 0}
    }
    config = options.get(speed, options["normal"])

    system_prompt = (
        f"""
        [INSTRUCCIÓN CRUCIAL]
        Eres un asistente que SOLO tiene permitido usar la información del CONTEXTO suministrado abajo. 
        Si la respuesta no está en el CONTEXTO, responde estrictamente: "Lo siento, no encuentro esa información en el documento".
        Prohibido usar conocimientos externos.
        """
        f"Eres un asistente experto. Estilo requerido: {style}\n"
        "REGLA DE IDIOMA: Responde SIEMPRE en el mismo idioma que utilice el usuario en su pregunta (Español).\n"
        "REGLAS DE FORMATO CRÍTICAS: No uses asteriscos (**) ni texto en negrita.\n"
        "Escribe cada oración en una línea nueva después de cada punto.\n"
        "REGLAS DE CONTEXTO: Usa los datos proporcionados como fuente primaria.\n"
        "CIERRE: Termina siempre con una pregunta de seguimiento relevante."    )

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Prepare user content
    user_content = ""
    if context:
        user_content += f"FILE DATA:\n{context}\n\n"

    user_content += f"USER QUESTION: {question}"

    messages.append({"role": "user", "content": user_content})

    # Ollama call
    response = ollama.chat(
        model='llama3',
        messages=messages,
        options=config
    )

    raw_response = response['message']['content']
    return clean_ai_response(raw_response)


def search_relevant_chunks(chat_id, user_question):
    client = chromadb.PersistentClient(path=DB_PATH)
    col = client.get_collection(name="document_chunks")


    results = col.query(
        query_texts=[user_question],
        n_results=3,
        where={"chat_id": str(chat_id)}
    )

    if results['documents'] and len(results['documents'][0]) > 0:
        final_context = "\n\n".join(results['documents'][0])

        print("DEBUG: La IA va a leer estos fragmentos:")
        for i, doc in enumerate(results['documents'][0]):
            print(f"Fragmento {i + 1}: {doc[:100]}...")

        return final_context



    return "No encontré información relevante."