import logging
import os
import uuid
from typing import Tuple

from werkzeug.utils import secure_filename

from config import Config


def setup_logging():
    """Настраивает базовую конфигурацию логирования для проекта."""
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


def log_info(message: str):
    """Логирует информационное сообщение."""
    logging.info(message)


def log_error(message: str, exc_info: bool = False):
    """Логирует сообщение об ошибке, опционально с информацией об исключении."""
    logging.error(message, exc_info=exc_info)


def log_success(message: str):
    """Логирует сообщение об успешном выполнении операции."""
    logging.info(f'Успех: {message}')


def ensure_directories():
    """Проверяет наличие и при необходимости создает рабочие директории."""
    print(f'CWD: {os.getcwd()}')
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)
    os.makedirs(Config.LOGS_DIR, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """
    Возвращает расширение файла в нижнем регистре.

    Args:
        filename: Имя файла.

    Returns:
        Расширение файла (например, '.png').
    """
    return os.path.splitext(filename)[1].lower()


def is_allowed_extension(filename: str) -> bool:
    """
    Проверяет, является ли расширение файла разрешенным.

    Args:
        filename: Имя файла.

    Returns:
        True, если расширение разрешено, иначе False.
    """
    return get_file_extension(filename) in Config.ALLOWED_EXTENSIONS


def is_valid_file_size(file_size: int) -> bool:
    """
    Проверяет, находится ли размер файла в допустимых пределах.

    Args:
        file_size: Размер файла в байтах.

    Returns:
        True, если размер допустим, иначе False.
    """
    return 0 < file_size <= Config.MAX_CONTENT_LENGTH


def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла в человекочитаемый вид (B, KB, MB).

    Args:
        size_bytes: Размер файла в байтах.

    Returns:
        Строка с отформатированным размером.
    """
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.2f} KB'
    return f'{size_bytes / (1024 * 1024):.2f} MB'


def generate_unique_filename(original_filename: str) -> str:
    """
    Генерирует уникальное имя файла на основе UUID, сохраняя расширение.

    Args:
        original_filename: Оригинальное имя файла.

    Returns:
        Новое уникальное имя файла.
    """
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f'{unique_id}{ext}'


def save_file(filename: str, file_content: bytes) -> Tuple[bool, str]:
    """
    Сохраняет содержимое файла на диск с уникальным именем.

    Args:
        filename: Оригинальное имя файла.
        file_content: Содержимое файла в виде байтов.

    Returns:
        Кортеж (True, new_filename), если сохранение успешно.
        Кортеж (False, error_message), если произошла ошибка.
    """
    try:
        original_name = secure_filename(filename)
        new_filename = generate_unique_filename(original_name)
        file_path = os.path.join(Config.UPLOAD_FOLDER, new_filename)

        with open(file_path, 'wb') as f:
            f.write(file_content)

        log_success(f'Файл сохранён: {new_filename} (оригинал: "{original_name}")')
        return True, new_filename
    except Exception as e:
        error_msg = f'Ошибка сохранения файла: {e}'
        log_error(error_msg)
        return False, error_msg


def delete_file(filename: str) -> bool:
    """
    Удаляет файл из директории загрузок.

    Args:
        filename: Имя файла для удаления.

    Returns:
        True, если файл успешно удален, иначе False.
    """
    try:
        safe_name = secure_filename(filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, safe_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            log_success(f'Файл удалён: {safe_name}')
            return True
        log_error(f'Файл для удаления не найден: {safe_name}')
        return False
    except Exception as e:
        log_error(f'Ошибка удаления файла: {safe_name}: {e}')
        return False
