import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_NAME = os.getenv('MONGODB_NAME', 'top5_analytics')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # API Keys
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    INSTAGRAM_CLIENT_ID = os.getenv('INSTAGRAM_CLIENT_ID')
    TIKTOK_CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY')
    
    # Celery
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = REDIS_URL
