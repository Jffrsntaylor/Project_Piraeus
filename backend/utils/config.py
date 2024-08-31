import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv not found, using os.environ directly")

class Config:
    API_KEY = os.getenv('API_KEY')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    DATABASE_URL = os.getenv('DATABASE_URL')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_CONTAINERS = int(os.getenv('MAX_CONTAINERS', 1000))
    OPTIMIZATION_INTERVAL = int(os.getenv('OPTIMIZATION_INTERVAL', 300))

config = Config()
