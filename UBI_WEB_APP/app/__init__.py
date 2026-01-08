"""
app/__init__.py
----------------
Ten plik tworzy obiekt aplikacji Flask i inicjalizuje:
- połączenie z bazą danych (Flask-SQLAlchemy),
- tabele w bazie,
- użytkowników testowych,
- rejestruje trasy (routes) w aplikacji.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY, TEST_USERS

# Tworzymy globalny obiekt SQLAlchemy, który później wykorzystają modele.
db = SQLAlchemy()


def create_app():
    """
    Funkcja fabrykująca aplikację Flask.

    Zwraca:
        Flask: skonfigurowana instancja aplikacji.
    """
    app = Flask(__name__)

    # Konfiguracja aplikacji z pliku config.py
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = SECRET_KEY

    # Inicjalizacja rozszerzenia SQLAlchemy z naszą aplikacją
    db.init_app(app)

    # Kontekst aplikacji – dzięki niemu możemy wykonywać operacje na bazie
    with app.app_context():
        from app import models  # importuje modele, żeby SQLAlchemy je znał

        # Tworzymy tabele w bazie, jeśli jeszcze nie istnieją
        db.create_all()

        # Dodajemy użytkowników testowych tylko, gdy baza jest pusta
        from app.models import User
        from app.auth import AuthManager

        if User.query.first() is None:
            for u in TEST_USERS:
                AuthManager.create_user(
                    username=u["username"],
                    email=u["email"],
                    password=u["password"],
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    role=u["role"],
                )

    # Rejestrujemy blueprinty (zestawy tras) z routes.py
    from app.routes import auth_bp, main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

