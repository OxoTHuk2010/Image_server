import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    DEBUG = os.getenv('DEBUG', 'false').strip().lower() in ('1','true','yes','on')

    #Настройка ограничений по файлам
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 #5mb
    ALLOWED_EXTENSIONS = {'.jpeg', '.jpg', '.png', '.gif'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/png',
        'image/gif'
    }

    #Настройка подключения к БД
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@postgres:5432/image_db')

    #Настройка пагинации
    ITEM_PER_PAGE = 10  # Значение по умолчанию
    MIN_ITEMS_PER_PAGE = 10  # Минимальное количество элементов на странице
    MAX_DISPLAY_ITEMS = 50  # Максимальное количество элементов на странице

    #Настройка рабочих директорий
    UPLOAD_FOLDER = 'images'
    LOGS_DIR = 'logs'
    BACKUP_DIR = 'backup'