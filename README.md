# UBI_Phyton - Projekt na studia w języku Python

Celem tego projektu jest stworzenie aplikacji WEBowej w języku Python oraz HTML.

Twórcy : Kacper Łach, Julia Sosnowska
# Opis Główny projektu

## Struktura projektu 
Poniżej przedstawiono układ plików i katalogów w projekcie. Podział ten zapewnia modularność i łatwość w utrzymaniu kodu.

```text
UBI_Phyton/
├── app/                        # Główny pakiet aplikacji
│   ├── __init__.py             # Inicjalizacja (Application Factory), konfiguracja rozszerzeń
│   ├── auth.py                 # Logika uwierzytelniania (Haszowanie haseł, AuthManager)
│   ├── extensions.py           # Globalne obiekty rozszerzeń (rozwiązuje 'circular imports')
│   ├── models.py               # Modele głównej bazy danych (User, Course, Enrollment, Grade)
│   ├── models_payment.py       # Modele dla osobnej bazy płatności (Payment)
│   ├── routes.py               # Kontroler - definicje tras URL i obsługa żądań
│   │
│   ├── static/                 # Zasoby statyczne
│   │   ├── css/                # Arkusze stylów (style.css)
│   │   └── img/                # Grafiki i ikony
│   │
│   └── templates/              # Szablony HTML (Jinja2)
│       ├── base.html           # Szablon bazowy (Layout, Menu nawigacyjne)
│       ├── login.html          # Widok logowania
│       ├── dashboard.html      # Panel główny użytkownika
│       └── admin/              # Widoki panelu administratora
│
├── instance/                   # Bazy danych (lokalne)
│   ├── ubi.db                  # Główna baza SQLite
│   └── payments.db             # Baza płatności SQLite
│
├── run.py                      # Plik startowy aplikacji
├── config.py                   # Konfiguracja zmiennych środowiskowych
├── requirements.txt            # Zależności projektu (biblioteki Python)
└── README.md                   # Dokumentacja
```




  
## Główne Technologie wykorzystane w tym projekcie

| Komponent | Technologia | Opis |
| :--- | :--- | :--- |
| **Backend** | Python 3, Flask | Logika aplikacji, routing, API. |
| **Baza Danych** | SQLite, SQLAlchemy | ORM obsługujący dwie bazy danych (Główną i Płatności). |
| **Auth** | Flask-Login | Zarządzanie sesjami i rolami użytkowników. |
| **Frontend** | Jinja2, HTML5, CSS3 | Dynamiczne szablony HTML. |
| **Powiadomienia** | Flask-Mail | Obsługa wysyłki e-maili systemowych. |

## Funkcje zaimplenetowane w projekcie
- System ról(Student/Nauczyciel/Administrator)
- Autentykacja i logowanie użtkowników ( narazie działa jedynie na administratorze)
- Zarządzaniei kursami i planem zajęć
- Dashboardy specyficzne dla ról
- Panel płatności
## Fukcje in progress
- Wysyłanie wiadomości email : nie działa rozpoznawanie użytkownika przez co aplikacja nie wie do kogo ma wysłac mail
- Wyświetlanie kalendarza u uczniów oraz wykładowców : aplikacja nie rozpoznaje konkrtnego użytkownika
## Opis Poszczególnych technologii
### Backend
- Python - Główny język programu
- Flask - framework webowy do budowy aplikacji oraz dróg
- Flask-Login - zarządzanie sesjami użytkowników i autoryzacją
- Flask-SGLAlchemy - Obsługa bazy danych
- SQLite - Baza danych
## Frontend
- HTML/CSS – struktura i stylizacja interfejsu
- JavaScript – interaktywność po stronie klienta
- Jinja2 – silnik szablonów Flask do renderowania dynamicznych stron HTML
# Opis Wybranych struktur w aplikajci
## 📂 Architektura: Analiza pliku `routes.py`
Plik `app/routes.py` jest sercem logiki nawigacyjnej aplikacji. Odpowiada za odbieranie żądań od użytkownika i kierowanie ich do odpowiednich funkcji.

### Moduły (Blueprints)
Kod podzielony jest na dwa główne "pod-aplikacje" (Blueprints):
1. **`auth_bp`** – Obsługuje wszystko, co związane z uwierzytelnianiem (logowanie/wylogowanie).
2. **`main_bp`** – Obsługuje główną logikę aplikacji (dashboard, panel admina, kursy).

### Funkcje i Endpointy (Opis techniczny)

#### Sekcja Autoryzacji (`auth_bp`)
| Ścieżka URL | Funkcja Python | Opis działania |
| :--- | :--- | :--- |
| `/login` | `login()` | Obsługuje metody **GET** (wyświetlenie formularza) i **POST** (weryfikacja danych). Wykorzystuje klasę `AuthManager` do sprawdzenia hasła i tworzy sesję użytkownika. |
| `/logout` | `logout()` | Czyści sesję (`session.clear()`) i wylogowuje użytkownika. |

####  Sekcja Główna (`main_bp`)
| Ścieżka URL | Funkcja Python | Opis działania |
| :--- | :--- | :--- |
| `/dashboard` | `dashboard()` | Główny pulpit nawigacyjny. Weryfikuje, czy użytkownik jest zalogowany i renderuje odpowiedni widok w zależności od roli (Student/Nauczyciel). |

####  Sekcja Administratora (Wymaga `@admin_required`)
Dostęp do tych funkcji mają tylko użytkownicy z rolą `admin`.

| Ścieżka URL | Funkcja Python | Opis działania |
| :--- | :--- | :--- |
| `/admin` | `admin_panel()` | Wyświetla hub administracyjny (menu zarządzania). |
| `/admin/users` | `admin_users()` | **CRUD Użytkowników**. Pozwala przeglądać listę kont oraz tworzyć nowych użytkowników (walidacja e-maila i loginu). |
| `/admin/users/<id>/toggle` | `admin_toggle_user()` | Aktywacja/Dezaktywacja konta użytkownika. Blokuje możliwość zbanowania samego siebie. |
| `/admin/courses` | `admin_courses()` | Zarządzanie przedmiotami. Pozwala dodać nowy kurs (Nazwa, ECTS, Prowadzący) oraz przeglądać istniejące. |
| `/admin/add_user_to_group` | `add_user_to_group()` | Przypisuje studenta do konkretnej grupy zajęciowej (tworzy relację w tabeli `Enrollment`). |

###  Dekoratory i Bezpieczeństwo
W pliku zdefiniowano niestandardowy dekorator **`@admin_required`**.
Działa on jako "bramka bezpieczeństwa" – przed wykonaniem jakiejkolwiek funkcji administracyjnej sprawdza, czy `session["role"] == "admin"`. Jeśli nie – wyrzuca błąd **403 Forbidden**.

---

## 📂 Architektura: Analiza pliku `__init__.py`
Plik `app/__init__.py` pełni rolę **Application Factory** (Fabryki Aplikacji). Jest punktem startowym, który konfiguruje cały projekt, inicjalizuje bazę danych oraz łączy wszystkie moduły w całość.

### Moduły i Rozszerzenia
Plik inicjalizuje globalne obiekty rozszerzeń, które są następnie współdzielone przez całą aplikację:

| Obiekt | Biblioteka | Opis działania |
| :--- | :--- | :--- |
| `db` | **Flask-SQLAlchemy** | Główny obiekt bazy danych. Obsługuje połączenie i operacje na modelach. |
| `login_manager` | **Flask-Login** | Zarządca sesji. Decyduje o tym, jak ładować użytkownika i gdzie przekierować niezalogowanych. |
| `mail` | **Flask-Mail** | Klient poczty. Skonfigurowany do wysyłania e-maili przez serwer SMTP (Gmail). |

### 'Funkcja `create_app()`
Jest to główna funkcja "fabryczna". Jej zadaniem jest utworzenie i zwrócenie gotowego obiektu aplikacji Flask.

#### 1. Konfiguracja
Ustawia kluczowe parametry aplikacji pobrane z pliku `config.py` oraz zdefiniowane lokalnie:
*   **Baza Danych**: Ustawia URI głównej bazy oraz dodatkowej bazy `payments_db` (binds).
*   **Bezpieczeństwo**: Konfiguruje `SECRET_KEY` (do szyfrowania sesji).
*   **Poczta**: Konfiguruje serwer SMTP Gmail (port 587, TLS, dane logowania).

#### 2. Inicjalizacja (init_app)
Wiąże globalne obiekty rozszerzeń z konkretną instancją aplikacji (`db.init_app(app)`, `mail.init_app(app)`).
*   Ustawia `login_view = 'auth.login'` – każdy niezalogowany użytkownik próbujący wejść na chronioną stronę zostanie tu przekierowany.

#### 3. Kontekst Aplikacji i Baza Danych
W bloku `with app.app_context()`:
*   Importuje modele (`app.models` oraz opcjonalnie `app.models_payment`).
*   **`db.create_all()`**: Automatycznie tworzy tabele w bazie danych, jeśli jeszcze nie istnieją.
*   **Seedowanie**: Sprawdza, czy baza jest pusta. Jeśli tak – automatycznie dodaje użytkowników testowych (z listy `TEST_USERS`).

#### 4. Rejestracja Blueprintów
Łączy logikę zdefiniowaną w innych plikach z główną aplikacją:
*   Rejestruje `auth_bp` (logowanie).
*   Rejestruje `main_bp` (główna funkcjonalność).

###  Funkcja `load_user(user_id)`
Funkcja wymagana przez **Flask-Login**.
*   Działa przy każdym odświeżeniu strony.
*   Pobiera ID użytkownika z ciasteczka sesyjnego.
*   Szuka użytkownika w bazie danych (`User.query.get`) i zwraca go, dzięki czemu w `routes.py` możemy używać `current_user`.
---
## 📂 Architektura: Analiza pliku `models.py`
Plik `app/models.py` definiuje schemat bazy danych przy użyciu biblioteki **SQLAlchemy**. Znajdują się tu klasy reprezentujące tabele oraz relacje między nimi.

### Użyte biblioteki
| Biblioteka | Zastosowanie |
| :--- | :--- |
| **db.Model** | Klasa bazowa SQLAlchemy, z której dziedziczą wszystkie modele. |
| **UserMixin** | (z `flask_login`) Dodaje do modelu `User` wymagane metody (`is_authenticated`, `get_id` itp.) dla systemu logowania. |
| **enum.Enum** | Użyte do zdefiniowania stałych typów ról użytkowników (`UserRole`). |
| **datetime** | Do automatycznego zapisywania czasu utworzenia rekordu (`created_at`). |

### Modele i Tabele

#### 1. Użytkownik (`class User`)
Centralna tabela systemu (`users`). Przechowuje dane każdego użytkownika, niezależnie od roli.
*   **Pola**: `username`, `email`, `password_hash`, `first_name`, `last_name`, `role`, `is_active`.
*   **Logika**: Zawiera metody pomocnicze `is_admin()`, `is_lecturer()`, `is_student()`, które ułatwiają sprawdzanie uprawnień w kodzie aplikacji.
*   **Role**: Zdefiniowane w enum `UserRole` (Student, Wykładowca, Admin).

#### 2. Kurs (`class Course`)
Reprezentuje przedmiot akademicki (np. "Programowanie Obiektowe").
*   **Pola**: `code` (np. INF101), `name`, `ects` (punkty), `description`.
*   **Relacje**:
    *   Przypisany do **jednego wykładowcy** (`lecturer_id`).
    *   Może mieć **wiele grup zajęciowych** (relacja jeden-do-wielu z `ClassGroup`).

#### 3. Grupa Zajęciowa (`class ClassGroup`)
Konkretna instancja kursu, np. "Grupa Laboratoryjna A".
*   **Pola**: `name` (np. "Grupa 1"), `semester`, `year`.
*   **Relacje**:
    *   Należy do jednego `Course`.
    *   Ma przypisanego prowadzącego (może być inny niż główny wykładowca kursu).
    *   Posiada listę zapisanych studentów (poprzez `Enrollment`).

#### 4. Zapis na zajęcia (`class Enrollment`)
Tabela łącząca (tabela asocjacyjna) w relacji wiele-do-wielu między `User` (student) a `ClassGroup`.
*   **Cel**: Pozwala zapisać studenta do konkretnej grupy.
*   **Pola**: `student_id`, `group_id`, `created_at`.
*   **Logika**: Dzięki temu modelowi wiemy, kto chodzi na jakie zajęcia.

#### 5. Lekcja (`class Lesson`)
Pojedyncze spotkanie w kalendarzu.
*   **Cel**: Umożliwia stworzenie planu zajęć.
*   **Pola**: `title` (np. "Wykład 1"), `room` (sala), `start_time`, `end_time`.
*   **Relacja**: Przypisana do konkretnej `ClassGroup`.

#### 6. Ocena (`class Grade`)
Przechowuje wyniki studentów.
*   **Pola**: `value` (np. 4.5), `weight` (waga oceny), `label` (opis, np. "Kolokwium").
*   **Relacje**: Łączy `student_id` z `group_id`, co pozwala wystawić ocenę konkretnemu studentowi w ramach konkretnej grupy.

### Diagram Relacji (ERD - Opis słowny)
*   **User (Wykładowca)** 1 --- ∞ **Course**
*   **Course** 1 --- ∞ **ClassGroup**
*   **User (Student)** 1 --- ∞ **Enrollment** ∞ --- 1 **ClassGroup**
*   **ClassGroup** 1 --- ∞ **Lesson**
*   **ClassGroup** 1 --- ∞ **Grade**

## 📂 Architektura: Analiza pliku `auth.py`l
Plik `app/auth.py` zawiera logikę biznesową (Business Logic) odpowiedzialną za bezpieczeństwo i zarządzanie tożsamością użytkowników. Oddziela on "jak" (logika) od "gdzie" (widoki w `routes.py`).

### Klasa `AuthManager`
Klasa ta grupuje metody statyczne, co ułatwia ich używanie w innych miejscach projektu bez konieczności tworzenia instancji obiektu.

#### 1. Bezpieczeństwo haseł
*   **`hash_password(password)`**: Zamienia jawne hasło (np. "haslo123") na bezpieczny ciąg znaków (hash) przy użyciu algorytmu **SHA-256**. Dzięki temu w bazie danych nie są przechowywane prawdziwe hasła.
*   **`verify_password(password, password_hash)`**: Sprawdza, czy hasło podane przy logowaniu pasuje do hasha zapisanego w bazie danych.

#### 2. Logika Logowania
*   **`login(username, password)`**:
    1. Pobiera użytkownika z bazy danych na podstawie loginu (`User.query.filter_by`).
    2. Jeśli użytkownik nie istnieje – zwraca błąd.
    3. Jeśli istnieje – weryfikuje hasło za pomocą `verify_password`.
    4. Jeśli hasło jest poprawne – **aktualizuje pole `last_login`** (czas ostatniego logowania) w bazie i zwraca sukces.

#### 3. Tworzenie konta
*   **`create_user(...)`**: Kompleksowa funkcja do rejestracji nowych użytkowników (używana przez Admina oraz przy seedowaniu bazy).
    *   Przyjmuje: login, email, hasło, imię, nazwisko i rolę.
    *   **Walidacja**: Sprawdza, czy użytkownik o takim loginie już istnieje (aby uniknąć duplikatów).
    *   **Transformacja**: Zamienia rolę tekstową (np. "admin") na typ wyliczeniowy `UserRole`.
    *   **Transakcyjność**: Jeśli wystąpi błąd podczas zapisu do bazy (`db.session.add`), funkcja wykonuje `rollback` (cofa zmiany), aby nie uszkodzić danych.

### Użyte biblioteki
| Biblioteka | Zastosowanie |
| :--- | :--- |
| **hashlib** | Standardowa biblioteka Pythona używana tutaj do generowania skrótów (hashy) haseł (SHA-256). |
| **datetime** | Do zapisu czasu ostatniego logowania. |
---


## 📂 Architektura: Analiza pliku `extensions.py`
Plik `app/extensions.py` pełni rolę **magazynu globalnych obiektów rozszerzeń**. Jego głównym celem jest rozwiązanie problemu tzw. "circular imports" (importów cyklicznych), które często zdarzają się w aplikacjach Flask.

### Dlaczego ten plik istnieje?
W większych aplikacjach często mamy sytuację:
1. `app/__init__.py` importuje `models.py` (żeby znać tabele).
2. `models.py` potrzebuje obiektu `db` (żeby zdefiniować kolumny).
3. Gdyby `db` było definiowane w `__init__.py`, powstałoby błędne koło: `init` -> `models` -> `init`.

Rozwiązaniem jest wydzielenie obiektu `db` do osobnego pliku (`extensions.py`), który jest importowany przez oba te miejsca.

### Zdefiniowane obiekty

| Obiekt | Biblioteka | Opis działania |
| :--- | :--- | :--- |
| `db` | **Flask-SQLAlchemy** | Pusta instancja bazy danych (`SQLAlchemy()`). <br>Na tym etapie nie jest jeszcze połączona z żadną aplikacją. Połączenie następuje dopiero w `create_app` za pomocą metody `db.init_app(app)`. |

### Kod 
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```
---

## 📂 Struktura i Analiza Plików

### 1. Kontroler: `app/routes.py`
Serce nawigacji. Definiuje adresy URL i obsługuje żądania HTTP.
*   **Blueprints**: Podział na `auth_bp` (logowanie) i `main_bp` (reszta systemu).
*   **Autoryzacja**:
    *   `/login`, `/logout`: Logika wejścia/wyjścia.
    *   `@admin_required`: Autorski dekorator blokujący dostęp niepowołanym osobom do panelu admina.
*   **Funkcje Admina**:
    *   `/admin/users`: CRUD użytkowników (tworzenie, blokowanie kont).
    *   `/admin/courses`: Zarządzanie przedmiotami i przypisywanie studentów do grup.

### 2. Fabryka Aplikacji: `app/__init__.py`
Punkt startowy aplikacji ("Application Factory").
*   Inicjalizuje globalne rozszerzenia: `db`, `login_manager`, `mail`.
*   Konfiguruje aplikację (klucze sekretne, parametry SMTP Gmaila).
*   Łączy bazy danych (główną oraz dodatkową `payments_db`).
*   Automatycznie tworzy tabele (`db.create_all()`) i użytkowników testowych przy pierwszym uruchomieniu.

### 3. Modele Danych: `app/models.py`
Schemat głównej bazy danych.
*   **`User`**: Użytkownik z rolą (Enum: Student, Wykładowca, Admin). Metody pomocnicze: `is_admin()`, `is_student()`.
*   **`Course`**: Przedmiot akademicki (np. "Programowanie").
*   **`ClassGroup`**: Konkretna grupa zajęciowa (np. "Lab 1").
*   **`Enrollment`**: Tabela łącząca Studenta z Grupą (kto gdzie chodzi).
*   **`Lesson` & `Grade`**: Plan zajęć i oceny.

### 4. Moduł Płatności: `app/models_payment.py`
Model dla **osobnej bazy danych** (`payments.db`).
*   Używa mechanizmu `__bind_key__ = 'payments_db'`, aby odseparować dane finansowe od danych osobowych/dydaktycznych.
*   Tabela `Payment` przechowuje historię wpłat (kwota, waluta, status, data).

### 5. Logika Biznesowa: `app/auth.py`
Czysta logika uwierzytelniania, oddzielona od widoków.
*   **`hash_password`**: Szyfrowanie haseł algorytmem SHA-256 (hashlib).
*   **`verify_password`**: Bezpieczne sprawdzanie hasła przy logowaniu.
*   **`create_user`**: Rejestracja użytkownika z walidacją unikalności loginu.

### 6. Frontend: `app/templates/base.html`
Szablon bazowy Jinja2.
*   Definiuje wspólny szkielet HTML (nagłówek, stopka).
*   **Inteligentne Menu**: Pasek nawigacji zmienia się dynamicznie w zależności od roli (np. Student widzi "Płatności", a Wykładowca "Moje kursy").

### 7. Rozszerzenia: `app/extensions.py`
Plik rozwiązujący problem "circular imports".
*   Inicjalizuje pusty obiekt `db = SQLAlchemy()`, który jest importowany przez modele i `__init__.py`.

---


## Wymagania
- Python 3.10+
- Biblioteki: [lista z requirements.txt, np. flask, numpy]

## Instalacja
```bash
git clone https://github.com/Blesky23/UBI_Phyton.git
cd UBI_Phyton
pip install -r requirements.txt
