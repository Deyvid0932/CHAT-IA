import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from routes import pdf, chat
from services.database import get_connection, create_tables

# Log Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
load_dotenv()

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This happens on startup
    logger.info("🔍 Verifying database connection...")

    app.state.modelo_rag = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model saved in the App's global state")

    db = get_connection()
    if db and db.is_connected():
        logger.info("MySQL connection successful!")
        create_tables()
        db.close()
    else:
        logger.error("ERROR: MySQL not available.")
    yield
    # This happens on shutdown
    logger.info("Closing backend...")

app = FastAPI(title="IA_PDF Backend", lifespan=lifespan)

# Improved CORS
origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf.router)
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
