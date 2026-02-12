from flask import Flask
from flask_cors import CORS
from config import Config
from utils import ensure_directories, setup_logging
from routes import register_routes
from database import Database




def create_app():
    app = Flask(__name__)
    #Настраиваем приложение
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH


    CORS(app)

    with app.app_context():
        print('Инициализация рабочих директорий')
        ensure_directories()
        Database.init_db()
        print('Настройка логирования')
        setup_logging()
    register_routes(app)
    return app


if __name__ == '__main__':
    print("Запуск сервера")
    app = create_app()
    app.run(debug=bool(Config.DEBUG), host='0.0.0.0', port=8000)
