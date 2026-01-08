"""
config.py
----------------
Plik z konfiguracją aplikacji webowej UczeLni.

Tutaj trzymamy:
- ścieżkę do bazy danych SQLite,
- sekret aplikacji (do sesji logowania),
- stałe używane w różnych miejscach (np. role użytkowników).
"""

from pathlib import Path

# Ścieżka bazowa projektu (folder projekt_uczelni_web)
BASE_DIR = Path(__file__).parent

# Ścieżka do pliku bazy danych SQLite (uczelni.db w głównym katalogu)
DATABASE_PATH = BASE_DIR / "uczelni.db"

# URI bazy danych dla SQLAlchemy (format: sqlite:///ścieżka)
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

# Wyłączenie śledzenia zmian (oszczędza zasoby, niepotrzebne na co dzień)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Sekretny klucz do podpisywania cookies sesyjnych.
# W produkcji należy go trzymać w zmiennej środowiskowej / pliku .env.
SECRET_KEY = "super_tajny_klucz_dev_zmien_na_produkcji"

# Role użytkowników w systemie
ROLE_STUDENT = "student"
ROLE_LECTURER = "lecturer"
ROLE_ADMIN = "admin"

# Dane testowe – stworzymy tych użytkowników przy pierwszym starcie aplikacji.
TEST_USERS = [
    {
        "username": "admin",
        "email": "admin@uczelni.edu",
        "password": "admin123",
        "first_name": "Adam",
        "last_name": "Admin",
        "role": ROLE_ADMIN,
    },
    {
        "username": "prowadz1",
        "email": "jan.kowalski@uczelni.edu",
        "password": "pass123",
        "first_name": "Jan",
        "last_name": "Kowalski",
        "role": ROLE_LECTURER,
    },
    {
        "username": "student1",
        "email": "anna.nowak@student.uczelni.edu",
        "password": "pass123",
        "first_name": "Anna",
        "last_name": "Nowak",
        "role": ROLE_STUDENT,
    },
]
