import sys
import os
# Subimos un nivel para encontrar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH
import chromadb

client = chromadb.PersistentClient(path=DB_PATH)
col = client.get_collection(name="document_chunk")

# Prueba con una palabra que sepas que está en tus PDFs
query = "Cuál es el objetivo principal"
results = col.query(query_texts=[query], n_results=2)

print("\n🔍 Resultados encontrados en ChromaDB:")
for i, doc in enumerate(results['documents'][0]):
    print(f"\n📄 Fragmento {i+1}:")
    print(doc[:200] + "...") # Solo mostramos el inicio