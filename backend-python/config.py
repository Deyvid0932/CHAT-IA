# backend-python/config.py
import os

# Detectamos la ruta base de 'backend-python'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Definimos la ruta de la base de datos vectorial
DB_PATH = os.path.join(BASE_DIR, "dates_pdf")


