import os
from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000') 