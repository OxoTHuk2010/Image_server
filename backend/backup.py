import argparse
import datetime
import os
import subprocess
from typing import Dict, Tuple
from urllib.parse import urlparse

from config import Config
from utils import setup_logging, log_info, log_error


def _parse_db_url(db_url: str) -> Dict[str, str]:
    """Парсит URL базы данных и возвращает компоненты."""
    parsed_url = urlparse(db_url)
    return {
        "user": parsed_url.username or "",
        "password": parsed_url.password or "",
        "host": parsed_url.hostname or "",
        "port": str(parsed_url.port or 5432),
        "db_name": parsed_url.path.lstrip("/"),
    }


def create_backup() -> Tuple[bool, str]:
    """
    Создает бэкап базы данных PostgreSQL с использованием утилиты pg_dump.

    Формирует имя файла с временной меткой, сохраняет его в директорию
    для бэкапов и логирует результат.

    Returns:
        Кортеж (True, имя_файла) в случае успеха.
        Кортеж (False, сообщение_об_ошибке) в случае неудачи.
    """
    try:
        db_info = _parse_db_url(Config.DATABASE_URL)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.sql"
        backup_path = os.path.join(Config.BACKUP_DIR, backup_filename)

        pg_dump_cmd = [
            "pg_dump",
            "-h",
            db_info["host"],
            "-p",
            db_info["port"],
            "-U",
            db_info["user"],
            "-d",
            db_info["db_name"],
            "-f",
            backup_path,
        ]

        result = subprocess.run(
            pg_dump_cmd,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PGPASSWORD": db_info["password"]},
        )

        if result.returncode == 0:
            file_size = os.path.getsize(backup_path)
            size_mb = file_size / (1024 * 1024)
            log_info(
                f"Бэкап успешно создан: {backup_filename}, размер: {size_mb:.2f} MB"
            )
            return True, backup_filename
        else:
            log_error(f"Ошибка создания бэкапа: {result.stderr}")
            return False, result.stderr

    except Exception as e:
        log_error(f"Критическая ошибка при создании бэкапа: {e}", exc_info=True)
        return False, str(e)


def restore_backup(backup_file: str) -> Tuple[bool, str]:
    """
    Восстанавливает базу данных из указанного файла бэкапа.

    Использует утилиту psql для восстановления.

    Args:
        backup_file: Имя файла бэкапа в директории Config.BACKUP_DIR.

    Returns:
        Кортеж (True, сообщение) в случае успеха.
        Кортеж (False, сообщение_об_ошибке) в случае неудачи.
    """
    try:
        db_info = _parse_db_url(Config.DATABASE_URL)
        backup_path = os.path.join(Config.BACKUP_DIR, backup_file)

        if not os.path.exists(backup_path):
            log_error(f"Файл бэкапа не найден: {backup_path}")
            return False, "Файл не найден"

        psql_cmd = [
            "psql",
            "-h",
            db_info["host"],
            "-p",
            db_info["port"],
            "-U",
            db_info["user"],
            "-d",
            db_info["db_name"],
            "-f",
            backup_path,
        ]

        result = subprocess.run(
            psql_cmd,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PGPASSWORD": db_info["password"]},
        )

        if result.returncode == 0:
            log_info(f"БД успешно восстановлена из: {backup_file}")
            return True, "Восстановление завершено"
        else:
            log_error(f"Ошибка восстановления: {result.stderr}")
            return False, result.stderr

    except Exception as e:
        log_error(f"Ошибка при восстановлении: {e}", exc_info=True)
        return False, str(e)


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Утилита для создания и восстановления бэкапов базы данных PostgreSQL."
    )

    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    restore_parser = subparsers.add_parser(
        "restore", help="Восстановить базу данных из файла бэкапа."
    )
    restore_parser.add_argument(
        "backup_file", type=str, help="Имя файла бэкапа для восстановления."
    )

    args = parser.parse_args()

    if args.command == "restore":
        success, res_msg = restore_backup(args.backup_file)
        if success:
            print(f"Восстановление успешно завершено: {res_msg}")
        else:
            print(f"Ошибка восстановления: {res_msg}")
    else:
        print("Создание нового бэкапа...")
        success, res_msg = create_backup()
        if success:
            print(f"Бэкап успешно создан: {res_msg}")
        else:
            print(f"Ошибка создания бэкапа: {res_msg}")
