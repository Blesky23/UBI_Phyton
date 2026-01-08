"""
run.py
----------------
Punkt wejścia aplikacji webowej.

Uruchomienie:
    python run.py

Po uruchomieniu:
    - aplikacja startuje na http://localhost:5000
    - możesz wejść przez przeglądarkę.
"""

from app import create_app

# Tworzymy instancję aplikacji Flask
app = create_app()

if __name__ == "__main__":
    # Uruchamiamy wbudowany serwer developerski Flaska
    app.run(
        debug=True,      # tryb developerski – pokazuje błędy w przeglądarce
        host="127.0.0.1",
        port=5000,
    )
