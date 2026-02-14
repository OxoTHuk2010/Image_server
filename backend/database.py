import time
from typing import List, Optional, Tuple

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from config import Config
from models import Image
from utils import log_error, log_info, log_success


class Database:
    """Класс для всех взаимодействий с базой данных."""

    _pool: Optional[pool.SimpleConnectionPool] = None

    @staticmethod
    def init_pool(min_conn: int = 1, max_conn: int = 10):
        """
        Инициализирует пул соединений с базой данных.

        Пытается подключиться в течение 2 минут перед тем, как вызвать исключение.

        Args:
            min_conn: Минимальное количество соединений в пуле.
            max_conn: Максимальное количество соединений в пуле.

        Raises:
            Exception: Если не удалось инициализировать пул соединений.
        """
        last_err = None
        for _ in range(60):  # Попытки подключения в течение ~2 минут
            try:
                Database._pool = pool.SimpleConnectionPool(
                    min_conn,
                    max_conn,
                    dsn=Config.DATABASE_URL,
                    cursor_factory=RealDictCursor,
                )
                log_info("Пул соединений с БД успешно инициализирован.")
                return
            except psycopg2.OperationalError as e:
                last_err = e
                time.sleep(2)
        raise Exception(f"Не удалось инициализировать пул соединений: {last_err}")

    @staticmethod
    def get_connection():
        """
        Получает одно соединение из пула.

        Выполняет несколько попыток, чтобы дождаться готовности БД.

        Raises:
            Exception: Если не удалось получить соединение.

        Returns:
            Соединение с базой данных.
        """
        last_err = None
        for _ in range(60):
            try:
                if Database._pool:
                    return Database._pool.getconn()
                raise Exception("Пул соединений не инициализирован.")
            except Exception as e:
                last_err = e
                time.sleep(2)
        raise Exception(f"Не удалось подключиться к БД: {last_err}")

    @staticmethod
    def put_connection(conn):
        """
        Возвращает соединение обратно в пул.

        Args:
            conn: Соединение, которое нужно вернуть.
        """
        if Database._pool:
            Database._pool.putconn(conn)

    @staticmethod
    def init_db() -> None:
        """
        Инициализирует схему БД. Создает таблицу 'images', если она не существует.

        Raises:
            Exception: Если произошла ошибка при выполнении SQL-запроса.
        """
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS images(
                        id SERIAL PRIMARY KEY,
                        filename TEXT NOT NULL UNIQUE,
                        original_name TEXT NOT NULL,
                        size INTEGER NOT NULL,
                        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_type TEXT NOT NULL
                    );
                    """
                )
            conn.commit()
            log_info("База данных инициирована (Таблица images готова).")
        except Exception as e:
            log_error(f"Ошибка инициализации БД: {e}")
            raise
        finally:
            Database.put_connection(conn)

    @staticmethod
    def save_image(image: Image) -> Tuple[bool, Optional[int]]:
        """
        Сохраняет метаданные изображения в базу данных.

        Args:
            image: Объект Image с данными для сохранения.

        Returns:
            Кортеж (True, image_id), если сохранение успешно.
            Кортеж (False, None), если произошла ошибка.
        """
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO images (filename, original_name, size, file_type)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (image.filename, image.original_name, image.size, image.file_type),
                )
                image_id = cursor.fetchone()["id"]
            conn.commit()
            log_success(f"Изображение сохранено в БД: {image.filename}, ID: {image_id}")
            return True, image_id
        except Exception as e:
            conn.rollback()
            log_error(f"Ошибка сохранения в БД: {e}")
            return False, None
        finally:
            Database.put_connection(conn)

    @staticmethod
    def get_images(
        page: int = 1, per_page: int = Config.ITEM_PER_PAGE
    ) -> Tuple[List[Image], int]:
        """
        Получает постраничный список изображений из БД.

        Args:
            page: Номер страницы (начиная с 1).
            per_page: Количество элементов на странице.

        Returns:
            Кортеж, содержащий список объектов Image и общее количество записей.
        """
        conn = Database.get_connection()
        try:
            offset = (page - 1) * per_page
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s",
                    (per_page, offset),
                )
                rows = cursor.fetchall()

                cursor.execute("SELECT COUNT(*) as total FROM images")
                total = cursor.fetchone()["total"]

            images = [Image(**row) for row in rows]
            return images, total
        except Exception as e:
            conn.rollback()
            log_error(f"Ошибка получения списка изображений: {e}")
            return [], 0
        finally:
            Database.put_connection(conn)

    @staticmethod
    def get_random() -> Optional[Image]:
        """
        Возвращает случайное изображение из базы данных.

        Returns:
            Объект Image или None, если таблица пуста.
        """
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM images ORDER BY random() LIMIT 1;")
                row = cursor.fetchone()
                if not row:
                    return None
                return Image(**row)
        except Exception as e:
            conn.rollback()
            log_error(f"Ошибка получения случайного изображения: {e}")
            return None
        finally:
            Database.put_connection(conn)

    @staticmethod
    def delete_image_db(image_id: int) -> Tuple[bool, Optional[str]]:
        """
        Удаляет запись об изображении из БД по ID.

        Args:
            image_id: ID изображения для удаления.

        Returns:
            Кортеж (True, filename), если удаление успешно.
            Кортеж (False, None), если изображение не найдено или произошла ошибка.
        """
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT filename FROM images WHERE id = %s;", (image_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return False, None

                filename = row["filename"]
                cursor.execute("DELETE FROM images WHERE id = %s;", (image_id,))
            conn.commit()
            log_success(f"Изображение удалено из БД: {filename}")
            return True, filename
        except Exception as e:
            conn.rollback()
            log_error(f"Ошибка удаления из БД: {e}")
            return False, None
        finally:
            Database.put_connection(conn)
