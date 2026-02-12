import psycopg2

from typing import List, Tuple, Optional
from config import Config
from models import Image
from utils import log_info, log_error, log_succes
from random import random

class Database():

    @staticmethod
    def get_connection():
        return psycopg2.connect(Config.DATABASE_URL)
    
    @staticmethod
    def init_db():
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS images(
                        id SERIAL PRIMARY KEY,
                        filename TEXT NOT NULL UNIQUE,
                        original_name TEXT NOT NULL,
                        size INTEGER NOT NULL,
                        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_type TEXT NOT NULL
                        );
                """)
                conn.commit()
                log_info('База данный инициирована')
        except Exception as e:
            log_error(f'Error init {e}')
        finally:
            conn.close()

    @staticmethod
    def save_image(image: Image) -> Tuple[bool, Optional[int]]:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO images (filename, original_name, size, file_type)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (image.filename, image.original_name, image.size, image.file_type))
                image_id = cursor.fetchone()[0]
                conn.commit()
                log_succes(f'Изображение сохранено в БД: {image.filename}, ID: {image_id}')

                return True, image_id
            
        except Exception as e:
            log_error(f'Save error in DB {e}')
            return False, None
        finally:
            conn.close()

    @staticmethod
    def get_images(page: int = 1 , per_page: int = Config.ITEM_PER_PAGE) -> Tuple[List[Image], int]:
        conn = Database.get_connection()
        try:
            offset = (page - 1) * per_page

            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s", (per_page, offset))
                rows = cursor.fetchall()
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
                cursor.execute('SELECT COUNT(*) as total FROM images')
                total = cursor.fetchone()['total']

                return images, total
            
        except Exception as e:
            log_error(f'Error get image {e}')
            return [], 0
        finally:
            conn.close()

    @staticmethod
    def get_random() -> Image:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(id) as total FROM images")
                total = cursor.fetchone()['total']

                rand = random.randint(1, total)
                cursor.execute("SELECT * FROM images WHERE id = %s", (rand))
                row = cursor.fetchall()
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
            log_error(f'Error get random image {e}')
            return {}
        finally:
            conn.close()
    
    @staticmethod
    def delete_image_db(image_id: int) -> Tuple[bool, Optional[str]]:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT filename FROM images WHERE id = %s", (image_id,))
                row = cursor.fetchone()
                if not row:
                    return False, None
                
                filename = row[0]
                cursor.execute('DELETE FROM images WHERE id = %s', (image_id,))
                conn.commit()

                log_succes(f"Изображение удалено из БД: {filename}")
                return True, filename
        except Exception as e:
            log_error(f'Error deleted from DB {e}')
            return False, None
        finally:
            conn.close()
    
