import os
import subprocess
import datetime
import sys
from urllib.parse import urlparse

from config import Config
from utils import setup_logging, log_info, log_error

def _parse_db_url(db_url):
    """Парсит URL базы данных и возвращает компоненты."""
    parsed_url = urlparse(db_url)
    return {
        'user': parsed_url.username,
        'password': parsed_url.password,
        'host': parsed_url.hostname,
        'port': str(parsed_url.port or 5432),
        'db_name': parsed_url.path.lstrip('/')
    }

def create_backup():
    try:
        db_info = _parse_db_url(Config.DATABASE_URL)
        user = db_info['user']
        password = db_info['password']
        host = db_info['host']
        port = db_info['port']
        db_name = db_info['db_name']
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.sql'
        backup_path = os.path.join(Config.BACKUP_DIR, backup_filename)

        #Команда для создания бэкапа
        pg_dump_cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', db_name,
            '-f', backup_path
        ]

        result = subprocess.run(
            pg_dump_cmd,
            capture_output=True,
            text=True,
            env={**os.environ, 'PGPASSWORD': password}
        )

        if result.returncode == 0:
            file_size = os.path.getsize(backup_path)
            size_mb = file_size / (1024 * 1024)
            log_info(f'Бэкап успешно создан: {backup_filename}, размер: {size_mb:.2f} MB')
            return True, backup_filename
        else:
            log_error(f'Ошибка создания бэкапа: {result.stderr}')
            return False, result.stderr
        
    except Exception as e:
        log_error(f'Критическая ошибка при создании бэкапа: {e}')
        return False, str(e)

def restore_backup(backup_file):
    """Восстановление БД из бэкапа"""
    try:
        db_info = _parse_db_url(Config.DATABASE_URL)
        user = db_info['user']
        password = db_info['password']
        host = db_info['host']
        port = db_info['port']
        db_name = db_info['db_name']
        
        backup_path = os.path.join(Config.BACKUP_DIR, backup_file)
        
        if not os.path.exists(backup_path):
            log_error(f'Файл бэкапа не найден: {backup_path}')
            return False, 'Файл не найден'
        
        # Команда для восстановления
        psql_cmd = [
            'psql',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', db_name,
            '-f', backup_path
        ]
        
        result = subprocess.run(
            psql_cmd,
            capture_output=True,
            text=True,
            env={**os.environ, 'PGPASSWORD': password}
        )
        
        if result.returncode == 0:
            log_info(f'БД успешно восстановлена из: {backup_file}')
            return True, 'Восстановление завершено'
        else:
            log_error(f'Ошибка восстановления: {result.stderr}')
            return False, result.stderr
            
    except Exception as e:
        log_error(f'Ошибка при восстановлении: {e}')
        return False, str(e)

if __name__ == '__main__':
    import argparse
    setup_logging()

    parser = argparse.ArgumentParser(description='Утилита для создания и восстановления бэкапов базы данных PostgreSQL.')
    
    # Создаем субпарсеры для команд
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда для восстановления
    restore_parser = subparsers.add_parser('restore', help='Восстановить базу данных из файла бэкапа.')
    restore_parser.add_argument('backup_file', type=str, help='Имя файла бэкапа для восстановления.')

    args = parser.parse_args()

    if args.command == 'restore':
        success, result = restore_backup(args.backup_file)
        if success:
            print(f'Восстановление успешно завершено: {result}')
        else:
            print(f'Ошибка восстановления: {result}')
    else:
        # Действие по умолчанию, если команда не указана
        print("Создание нового бэкапа...")
        success, result = create_backup()
        if success:
            print(f'Бэкап успешно создан: {result}')
        else:
            print(f'Ошибка создания бэкапа: {result}')