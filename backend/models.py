from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any


@dataclass
class Image:
    """
    Дата-класс, представляющий метаданные изображения в системе.

    Attributes:
        id: Уникальный идентификатор изображения в базе данных.
        filename: Уникальное имя файла, под которым он сохранен на диске.
        original_name: Оригинальное имя файла, загруженного пользователем.
        size: Размер файла в байтах.
        upload_time: Дата и время загрузки файла.
        file_type: Тип файла (расширение, например, 'jpg', 'png').
    """
    id: Optional[int] = None
    filename: str = ''
    original_name: str = ''
    size: int = 0
    upload_time: Optional[datetime] = None
    file_type: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект Image в словарь, готовый для сериализации в JSON.

        Returns:
            Словарь с полями объекта.
        """
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'size': self.size,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'file_type': self.file_type,
            'url': f'/images/{self.filename}'
        }