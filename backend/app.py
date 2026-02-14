from flask import Flask
from flask_cors import CORS

from config import Config
from database import Database
from routes import register_routes
from utils import ensure_directories, setup_logging


def create_app() -> Flask:
    """
    Создаёт и настраивает экземпляр Flask-приложения.

    Эта функция является фабрикой приложения. Она выполняет следующие шаги:
    1. Создаёт экземпляр Flask.
    2. Загружает конфигурацию из объекта Config.
    3. Инициализирует CORS.
    4. В контексте приложения выполняет:
       - Создание необходимых директорий (для логов, загрузок).
       - Инициализацию пула соединений с БД.
       - Инициализацию схемы БД (создание таблиц).
       - Настройку логирования.
    5. Регистрирует все маршруты (endpoints).

    Returns:
        Готовый к запуску экземпляр Flask-приложения.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

    CORS(app)

    with app.app_context():
        print("Инициализация рабочих директорий...")
        ensure_directories()
        print("Инициализация пула соединений с БД...")
        Database.init_pool()
        print("Инициализация схемы БД...")
        Database.init_db()
        print("Настройка логирования...")
        setup_logging()

    register_routes(app)
    print("Маршруты зарегистрированы.")
    return app


if __name__ == "__main__":
    print("Запуск Flask-сервера...")
    flask_app = create_app()
    flask_app.run(debug=bool(Config.DEBUG), host="0.0.0.0", port=8000)
