import os
import chromadb

current_dir = os.path.dirname(os.path.abspath(__file__))

backend_dir = os.path.dirname(current_dir)

db_path = os.path.join(backend_dir, "dates_pdf")

client = chromadb.PersistentClient(path=db_path)

col = client.get_or_create_collection(name="document_chunk")