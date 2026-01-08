"""
app/auth.py
----------------
Logika związana z autoryzacją:
- haszowanie hasła,
- logowanie,
- tworzenie użytkownika (używane dla kont testowych).
"""

import hashlib
from datetime import datetime

from app import db
from app.models import User, UserRole


class AuthManager:
    """Klasa z metodami wspierającymi logowanie i rejestrację."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Zwraca hash hasła (SHA256).

        Uwaga: w projekcie produkcyjnym użyj raczej bcrypt / argon2,
        tutaj dla prostoty stosujemy SHA256.
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Sprawdza, czy podane hasło odpowiada zapisanemu hashowi.
        """
        return AuthManager.hash_password(password) == password_hash

    @staticmethod
    def login(username: str, password: str):
        """
        Próbuje zalogować użytkownika.

        Zwraca:
            (success: bool, user: User | None)
        """
        user = User.query.filter_by(username=username).first()

        if not user:
            return False, None

        if not AuthManager.verify_password(password, user.password_hash):
            return False, None

        # Aktualizujemy czas ostatniego logowania
        user.last_login = datetime.now()
        db.session.commit()

        return True, user

    @staticmethod
    def create_user(username: str, email: str, password: str,
                    first_name: str, last_name: str, role: str) -> bool:
        """
        Tworzy nowego użytkownika (używane przy starcie aplikacji dla kont testowych).

        Zwraca:
            True jeśli operacja się udała, False jeśli użytkownik już istnieje lub wystąpił błąd.
        """
        try:
            # Sprawdzamy, czy taki user już istnieje
            if User.query.filter_by(username=username).first():
                return False

            # Konwersja roli z tekstu na enum
            role_enum = UserRole(role)

            new_user = User(
                username=username,
                email=email,
                password_hash=AuthManager.hash_password(password),
                first_name=first_name,
                last_name=last_name,
                role=role_enum,
            )

            db.session.add(new_user)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Błąd podczas tworzenia użytkownika: {e}")
            db.session.rollback()
            return False
