import os
import logging
import uuid
from config import Config
from werkzeug.utils import secure_filename

#Логирование
def setup_logging():
    log_format = '[%(asctime)s] %(levelname)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    log_file = os.path.join(Config.LOGS_DIR, 'app.log')

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def log_info(message):
    logging.info(message)

def log_error(message, exc_info=False):
    logging.error(message, exc_info=exc_info)

def log_succes(message):
    logging.info(f'Успех: {message}')

#Создаём рабочие директори
def ensure_directories():
    print(f'CWD: {os.getcwd()}')
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)
    os.makedirs(Config.LOGS_DIR, exist_ok=True)


def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

def is_allowed_extension(filename):
    ext = get_file_extension(filename)
    return ext in Config.ALLOWED_EXTENSIONS

def is_valid_file_size(file_size):
    return 0 < file_size <= Config.MAX_CONTENT_LENGTH

def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.2f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.2f} MB'
    
def generate_unique_filename(original_filename):
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f'{unique_id}{ext}'

def save_file(filename, file_content):
    try:
        original_name = secure_filename(filename)
        new_filename = generate_unique_filename(original_name)
        file_path = os.path.join(Config.UPLOAD_FOLDER, new_filename)

        with open(file_path, 'wb') as f:
            f.write(file_content)

        log_succes(f'Файл сохранён: {new_filename} (оригинал: "{original_name}")')
        return True, new_filename
    except Exception as e:
        error_msg = f'Ошибка сохранения файла: {e}'
        log_error(error_msg)
        return False, error_msg
    
def delete_file(filename) -> bool:
        try:
            save_name = secure_filename(filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, save_name)

            if os.path.exists(file_path):
                os.remove(file_path)
                log_succes(f'Файл удалён: {save_name}')
                return True
            log_error(f'Файл для удаления не найден: {save_name}')
            return False
        except Exception as e:
            log_error(f'Ошибка удаления файла: {save_name}: {e}')
            return False
