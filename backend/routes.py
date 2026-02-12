from config import Config
from flask import render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models import Image
from utils import (
    is_allowed_extension,
    format_file_size,
    get_file_extension,
    save_file,
    delete_file,
    log_error,
    log_succes
)
from database import Database

def register_routes(app):
    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True}), 200

    @app.post('/api/upload')
    def upload_file():
        """Загрузка изображения"""

        if "file" not in request.files:
            return jsonify({"error": "Файл не выбран"}), 400

        file = request.files["file"]
        if not file or file.filename == "":
            return jsonify({"error": "Файл не найден"}), 400

        if not is_allowed_extension(file.filename):
            return jsonify({"error": "Неподдерживаемое расширение файла"}), 400
        
        try:
            file_data = file.read()
            file_size = len(file_data)

            if file_size > Config.MAX_CONTENT_LENGTH:
                max_size = format_file_size(Config.MAX_CONTENT_LENGTH)
                return jsonify({'error': f"Файл слишком большй. Максимальный размер файла {max_size}"}), 400
            
            success, result = save_file(file.filename, file_data)
            if not success:
                return jsonify({'error': f"Ошибка сохранения файла: {result}"}), 500
            
            new_filename = result
            file_type = get_file_extension(file.filename).replace('.','')
            image = Image(
                filename = new_filename,
                original_name = secure_filename(file.filename),
                size = file_size,
                file_type = file_type
            )

            success, image_id = Database.save_image(image)
            if not success:
                delete_file(new_filename)
                return jsonify({'error': "Ошибка сохранения метаданных в Бд "}), 500
            
            log_succes(f'Изображение сохранено: {new_filename}')

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
            return jsonify({'error': str(e)}), 500
        

    @app.delete("/api/images/<int:image_id>")
    def delete_image(image_id: int):
        """Удаление изображения по ID."""
        success, filename = Database.delete_image_db(image_id)
        if not success or not filename:
            return jsonify({"error": "Изображение не найдено"}), 404

        if not delete_file(filename):
            return jsonify({"error": "Не удалось удалить файл с диска"}), 500

        return jsonify({"success": True, "message": "Изображение удалено"}), 200

    @app.get('/api/images')
    def list_image():
        """Список изображений с пагинацией: /api/images?page=1&per_page=10"""
        page = request.args.get("page", "1")
        per_page = request.args.get("per_page", str(Config.ITEM_PER_PAGE))
        images, total = Database.get_images(int(page), int(per_page))
        return jsonify({
            "success": True,
            "images": [img.to_dict() for img in images],
            "total": total,
            "page": int(page),
            "per_page": int(per_page),
        }), 200

    @app.get("/api/random")
    def random_image():
        """Случайное изображение для слайдшоу."""
        img = Database.get_random()
        if not img:
            return jsonify({"success": True, "image": None}), 200
        return jsonify({"success": True, "image": img.to_dict()}), 200
    
    @app.get("/images/<path:filename>")
    def serve_images(filename: str):
        """Fallback (если запускать без Nginx)."""
        return send_from_directory(Config.UPLOAD_FOLDER, filename)