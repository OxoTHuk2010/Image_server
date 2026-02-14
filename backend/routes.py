from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from config import Config
from database import Database
from models import Image
from utils import (delete_file, format_file_size, get_file_extension,
                   is_allowed_extension, log_error, log_success, save_file)


def register_routes(app: Flask):
    """
    Регистрирует все маршруты (endpoints) для Flask-приложения.

    Args:
        app: Экземпляр Flask-приложения.
    """

    @app.get('/')
    def index():
        """Отдаёт главную HTML-страницу."""
        return render_template('index.html')

    @app.get("/api/health")
    def health():
        """Проверяет работоспособность сервиса."""
        return jsonify({"ok": True}), 200

    @app.post('/api/upload')
    def upload_file():
        """
        Обрабатывает загрузку файла изображения.

        Проверяет файл на соответствие требованиям (размер, тип),
        сохраняет его на диск с уникальным именем и записывает метаданные в БД.

        Returns:
            JSON с информацией о сохраненном файле или ошибке.
        """
        if "file" not in request.files:
            return jsonify({"error": "Файл не выбран"}), 400

        file = request.files["file"]

        if not file or not file.filename:
            return jsonify({"error": "Файл не найден"}), 400

        if not is_allowed_extension(file.filename):
            return jsonify({"error": "Неподдерживаемое расширение файла"}), 400

        if file.content_type not in Config.ALLOWED_MIME_TYPES:
            return jsonify({"error": "Неподдерживаемый тип файла"}), 400

        try:
            file_data = file.read()
            file_size = len(file_data)

            if file_size > Config.MAX_CONTENT_LENGTH:
                max_size = format_file_size(Config.MAX_CONTENT_LENGTH)
                return jsonify({'error': f"Файл слишком большой. Максимальный размер файла {max_size}"}), 400

            success, result = save_file(file.filename, file_data)
            if not success:
                return jsonify({'error': f"Ошибка сохранения файла: {result}"}), 500

            new_filename = result
            file_type = get_file_extension(file.filename).replace('.', '')
            image = Image(
                filename=new_filename,
                original_name=secure_filename(file.filename),
                size=file_size,
                file_type=file_type
            )

            success, image_id = Database.save_image(image)
            if not success:
                delete_file(new_filename)
                return jsonify({'error': "Ошибка сохранения метаданных в БД"}), 500

            log_success(f'Изображение сохранено: {new_filename}')

            return jsonify({
                'success': True,
                'message': "Файл успешно сохранён",
                'image': {
                    'id': image_id,
                    'filename': new_filename,
                    'original_name': secure_filename(file.filename),
                    'size': file_size,
                    'size_human': format_file_size(file_size),
                    'url': f"/images/{new_filename}",
                }
            }), 201

        except Exception as e:
            log_error(f"Ошибка загрузки файла: {e}", exc_info=True)
            return jsonify({'error': "Внутренняя ошибка сервера при загрузке файла"}), 500

    @app.delete("/api/images/<int:image_id>")
    def delete_image(image_id: int):
        """
        Удаляет изображение по его ID.

        Удаляет метаданные из БД и соответствующий файл с диска.

        Args:
            image_id: ID изображения для удаления.

        Returns:
            JSON с подтверждением успеха или сообщением об ошибке.
        """
        success, filename = Database.delete_image_db(image_id)

        if not success or not filename:
            return jsonify({"error": "Изображение не найдено"}), 404

        if not delete_file(filename):
            # В этом случае запись в БД уже удалена. Это пограничный случай,
            # который требует внимания администратора (файл-сирота на диске).
            return jsonify({"error": "Не удалось удалить файл с диска, хотя запись в БД удалена"}), 500

        return jsonify({"success": True, "message": "Изображение удалено"}), 200

    @app.get('/api/images')
    def list_images():
        """
        Возвращает постраничный список загруженных изображений.

        Принимает query-параметры `page` и `per_page`.

        Returns:
            JSON с массивом изображений и информацией о пагинации.
        """
        try:
            page = int(request.args.get("page", "1"))
            per_page = int(request.args.get("per_page", str(Config.ITEM_PER_PAGE)))

            # Валидация параметров пагинации
            page = max(1, page)
            per_page = min(max(per_page, Config.MIN_ITEMS_PER_PAGE), Config.MAX_DISPLAY_ITEMS)

            images, total = Database.get_images(page, per_page)
            return jsonify({
                "success": True,
                "images": [img.to_dict() for img in images],
                "total": total,
                "page": page,
                "per_page": per_page,
            }), 200
        except (ValueError, TypeError):
            return jsonify({"error": "Неверные параметры пагинации"}), 400

    @app.get("/api/random")
    def random_image():
        """
        Возвращает одно случайное изображение из базы данных.

        Returns:
            JSON с данными одного изображения или null, если их нет.
        """
        img = Database.get_random()
        if not img:
            return jsonify({"success": True, "image": None}), 200
        return jsonify({"success": True, "image": img.to_dict()}), 200

    @app.get("/images/<path:filename>")
    def serve_image(filename: str):
        """
        Отдаёт статический файл изображения из папки загрузок.

        Этот маршрут используется в основном для локальной разработки без Nginx
        или как fallback. В продакшене файлы должен отдавать Nginx.

        Args:
            filename: Имя файла изображения.
        """
        return send_from_directory(Config.UPLOAD_FOLDER, filename)