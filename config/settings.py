import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME', 'campuscart_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
)

SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key')

BASE_DIR = Path(__file__).resolve().parent
