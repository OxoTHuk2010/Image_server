import os
import subprocess
import datetime
import sys

from config import Config
from utils import setup_logging, log_info, log_error

def create_backup():
    try:
        db_url = Config.DATABASE_URL
        db_url = db_url.replace('postgresql://', '')
        
        parts = db_url.split('@')
        
        user_pass = parts[0]
        host_port_db = parts[1]

        user, password = user_pass.split(':') 

        host_port, db_name = host_port_db.split('/')

        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host,port = host_port, '5432'
        
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

        log_info(f'Создание бэкапа выполнено успешно: {backup_filename}')

        result = subprocess.run(
            pg_dump_cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            file_size = os.path.getsize(backup_path)
            size_mb = file_size / (1024 * 1024)
            log_info(f'Бэекап создан {backup_filename} {size_mb}')

            return True, backup_filename
        else:
            log_error(f'Ошибка: {result.stderr}')
            return False, result.stderr
        
    except Exception as e:
        log_error(f'Error {e}')
        return False, str(e)

def restore_backup(backup_file):
    """Восстановление БД из бэкапа"""
    try:
        db_url = Config.DATABASE_URL
        db_url = db_url.replace('postgresql://', '')
        
        parts = db_url.split('@')
        
        user_pass = parts[0]
        host_port_db = parts[1]

        user, password = user_pass.split(':') 

        host_port, db_name = host_port_db.split('/')

        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host, port = host_port, '5432'
        
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
    setup_logging()

    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if len(sys.argv) > 2:
            backup_file = sys.argv[2]
            success, result = restore_backup(backup_file)
            if success:
                print(f'Восстановление успешно: {result}')
            else:
                print(f'Ошибка восстановления: {result}')
        else:
            print('Укажите файл восстановления')

    else:
        success, result = create_backup()
        if success:
            print('Бекап успешно создан')
        else:
            print('Ошибка создания бэкапа')