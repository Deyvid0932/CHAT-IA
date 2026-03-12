import chromadb
from config import DB_PATH

client = chromadb.PersistentClient(path=DB_PATH)

print("📁 Colecciones existentes:", client.list_collections())

col = client.get_collection(name="document_chunks")

results = col.get(
    limit=5,
    include=["documents", "metadatas"]
)

print("\n🔍 CONTENIDO EN CHROMADB:")
for i in range(len(results['ids'])):
    print(f"--- Registro {i+1} ---")
    print(f"ID: {results['ids'][i]}")
    print(f"Metadata: {results['metadatas'][i]}")
    print(f"Texto (resumen): {results['documents'][i][:100]}...")
    print("-" * 20)