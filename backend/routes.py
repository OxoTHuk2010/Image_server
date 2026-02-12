from config import Config
from flask import render_template, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from models import Image
from utils import (
    is_allowed_extension, format_file_size, get_file_extension,
    save_file, delete_file, log_error, log_info, log_succes
)
from database import Database, delete_image_db, get_images

def register_routes(app):
    
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """
        Принимает изображение, изменяем имя, выполняем базовую валидацию, сохраняем информацию об изображении в БД, сохраняем само изображение, при успешной записи в БД, отдаёт информацию о сохранённом изображении.
        """

        if 'file' not in request.files:
            return jsonify({'error': 'Файл не выбран'}), 400
        
        file = request.files['file']

        if file.filename == '':
            log_error('Filename is empty')
            return jsonify({'error': 'File not found'}), 400
        
        if not is_allowed_extension(file.filename):
            log_error('File format not support')
            return jsonify({'error': 'File not support'}), 400
        
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
                return jsonify({'error': "Ошибка сохранения в Бд "}), 500
            
            log_succes(f'Изображение сохранено {new_filename}')

            return jsonify({
                'success': True,
                'message': "Файл успешно сохранён",
                'image': {
                    'id': image_id,
                    'filename': new_filename,
                    'original_name': secure_filename(file.filename),
                    'size': format_file_size(file_size),
                    'url': f"/images/{new_filename}",
                    'delete_url': f'/api/delete/{image_id}'
                }
            }), 201

        except Exception as e:
            log_error(f"Ошибка загрузки файла: {e}")
            return jsonify({'error': str(e)}), 500
        

    @app.route('/api/delete/<int:image_id>', methods=['POST'])
    def delete_image(image_id):
        """
        Принимает id изображения и удаляет его из БД и директории с изображениями , отдаём успех в случае если удалено
        """

        try:
            success, filename = delete_image_db(image_id)

            if not success:
                log_error(f"Ошибка удаления {image_id}")
                return jsonify({'error': f"Ошибка удаления {image_id}"}), 500
            
            deleted = delete_file(filename)
            if not deleted:
                log_error(f"Ошибка удаления файла {filename}")
                return jsonify({'error': f"Ошибка удаления {image_id}"}), 500

            return jsonify({
                'success': True,
                'message': "Изображение удалено"
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/list?<int:page_number>', methods=['GET'])
    def list_image(page):
        """
        Принимает номер страницы, получаем информацию по изображениям из БД , отдаём список изображения и итоговое количество изображений , для постраничного отображения 
        """
        try:
            images, total =  get_images(page, Config.ITEM_PER_PAGE)

            return jsonify({
                'success': True,
                'message': "Список изображений",
                'images': images,
                'total': total
            }), 201 
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/random', methods=['GET'])
    def get_random_image():
        """
        Получаем текущее количество изображений в БД , генерируем рандомный id и по нему получаем изображение, отдаём изображение с диска для слайдшоу на главной странице и информацию об изображении
        """
        try:
            image = get_random_image()

            send_from_directory(Config.UPLOAD_FOLDER, image.filename)

            return jsonify({
                'success': True,
                'message': "Случайное изображение",
                'image': image.to_dict()
            }), 201 
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500