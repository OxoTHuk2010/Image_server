import time
import random
from typing import List, Tuple, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config
from models import Image
from utils import log_info, log_error, log_succes

class Database():

    @staticmethod
    def get_connection(retries: int = 30, delay_sec: float = 1.0):
        """Соединение с ретраями — чтобы контейнер переживал старт Postgres."""
        last_err = None
        for _ in range(retries):
            try:       
                return psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
            except Exception as e:
                last_err = e
                time.sleep(delay_sec)
        raise Exception(f'Не удалось подключиться к БД: {last_err}')
    
    @staticmethod
    def init_db() -> None:
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
            log_info('База данный инициирована (Таблица images готова).')
        except Exception as e:
            log_error(f'Ошибка инициализации БД: {e}')
            raise
        finally:
            conn.close()

    @staticmethod
    def save_image(image: Image) -> Tuple[bool, Optional[int]]:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO images (filename, original_name, size, file_type)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """, (image.filename, image.original_name, image.size, image.file_type),
                )
                image_id = cursor.fetchone()[0]
            conn.commit()
            log_succes(f'Изображение сохранено в БД: {image.filename}, ID: {image_id}')

            return True, image_id
            
        except Exception as e:
            log_error(f"Ошибка сохранения в БД: {e}")
            return False, None
        finally:
            conn.close()

    @staticmethod
    def get_images(page: int = 1 , per_page: int = Config.ITEM_PER_PAGE) -> Tuple[List[Image], int]:
        conn = Database.get_connection()
        try:
            page = max(1, int(page))
            per_page = max(1, int(per_page))
            offset = (page - 1) * per_page

            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s", (per_page, offset))
                rows = cursor.fetchall()

                cursor.execute('SELECT COUNT(*) as total FROM images')
                total = cursor.fetchone()['total']

            images = [
                Image(
                    id = row['id'],
                    filename = row['filename'],
                    original_name = row['original_name'],
                    size = row['size'],
                    upload_time = row['upload_time'],
                    file_type = row['file_type']
                )
                for row in rows
            ]

            return images, total
            
        except Exception as e:
            log_error(f"Ошибка получения списка изображений: {e}")
            return [], 0
        finally:
            conn.close()

    @staticmethod
    def get_random() -> Optional[Image]:
        """Случайное изображение."""
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM images ORDER BY random() LIMIT 1;")
                row = cursor.fetchone()
                if not row:
                    return None

                image = Image(
                    id = row['id'],
                    filename = row['filename'],
                    original_name = row['original_name'],
                    size = row['size'],
                    upload_time = row['upload_time'],
                    file_type = row['file_type']
                )
            return image
            
        except Exception as e:
            log_error(f"Ошибка получения случайного изображения: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def delete_image_db(image_id: int) -> Tuple[bool, Optional[str]]:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT filename FROM images WHERE id = %s;", (image_id,))
                row = cursor.fetchone()
                if not row:
                    return False, None

                filename = row["filename"]
                cursor.execute("DELETE FROM images WHERE id = %s;", (image_id,))
            conn.commit()
            log_succes(f"Изображение удалено из БД: {filename}")
            return True, filename
        except Exception as e:
            log_error(f"Ошибка удаления из БД: {e}")
            return False, None
        finally:
            conn.close()
