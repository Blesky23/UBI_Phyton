"""
app/routes.py
----------------
Definicja tras HTTP (adresów URL) dla aplikacji.

Tutaj obsługujemy:
- stronę logowania (/ i /login),
- wylogowanie (/logout),
- dashboard po zalogowaniu (/dashboard).
"""


from flask import Blueprint, render_template, request, redirect, url_for, session

from app.auth import AuthManager
from app.models import User

from functools import wraps
from flask import abort

# Tworzymy dwa "blueprinty":
# - auth_bp: trasy związane z logowaniem
# - main_bp: główne widoki po zalogowaniu
auth_bp = Blueprint("auth", __name__)
main_bp = Blueprint("main", __name__)

def admin_required(view_func):
    """
    Dekorator sprawdzający, czy użytkownik jest zalogowany jako administrator.

    Użycie:
        @admin_required
        def admin_view():
            ...
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        role = session.get("role")
        if role != "admin":
            # Jeśli nie admin – zwracamy błąd 403 (brak uprawnień)
            return abort(403)
        return view_func(*args, **kwargs)

    return wrapped_view

@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Strona logowania.

    GET  – wyświetla formularz logowania.
    POST – próbuje zalogować użytkownika na podstawie danych z formularza.
    """
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        success, user = AuthManager.login(username, password)

        if success:
            # Zapisujemy podstawowe dane w sesji (po stronie serwera)
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role.value  # enum -> tekst

            # Po zalogowaniu przekierowujemy na dashboard
            return redirect(url_for("main.dashboard"))
        else:
            error = "Błędna nazwa użytkownika lub hasło."

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    """
    Wylogowanie użytkownika.

    Czyści dane z sesji i przekierowuje na stronę logowania.
    """
    session.clear()
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")


####################OD Tego momentu zmiany do WERYFIKACJI ADMINA
def dashboard():
    
    """
    Główny dashboard – widoczny tylko dla zalogowanych użytkowników.

    Jeżeli w sesji nie ma `user_id`, przekierowujemy na logowanie.
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    # Pobieramy zalogowanego użytkownika z bazy
    user = User.query.get(user_id)

    return render_template("dashboard.html", user=user)

@main_bp.route("/admin")
@admin_required
def admin_panel():
    """
    Główny panel administratora.

    Na razie wyświetla tylko prostą stronę z linkiem do zarządzania użytkownikami.
    Później dodamy tu liczniki (ilu studentów, ilu wykładowców itd.).
    """
    user_id = session.get("user_id")
    admin_user = User.query.get(user_id)
    return render_template("admin_panel.html", user=admin_user)


@main_bp.route("/admin/users", methods=["GET", "POST"])
@admin_required
def admin_users():
    """
    Strona do zarządzania użytkownikami.

    GET:
        - wyświetla listę użytkowników,
        - wyświetla formularz dodawania nowego użytkownika.

    POST:
        - próbuje utworzyć nowego użytkownika na podstawie danych z formularza.
    """
    from app.auth import AuthManager  # lokalny import, żeby uniknąć pętli zależności

    message = None
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        role = request.form.get("role", "student")

        if not username or not email or not password or not first_name or not last_name:
            error = "Wszystkie pola są wymagane."
        else:
            ok = AuthManager.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            if ok:
                message = "Użytkownik został utworzony."
            else:
                error = "Nie udało się utworzyć użytkownika (być może istnieje już taki login lub e‑mail)."

    # Pobierz wszystkich użytkowników z bazy
    users = User.query.order_by(User.id.asc()).all()

    return render_template("admin_users.html", users=users, message=message, error=error)


@main_bp.route("/admin/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def admin_toggle_user(user_id: int):
    """
    Przełączanie statusu użytkownika (aktywny/nieaktywny).

    Używane z przycisku w tabeli użytkowników.
    """
    from app import db

    user = User.query.get_or_404(user_id)

    # Nie pozwalamy wyłączyć samego siebie
    if user.id == session.get("user_id"):
        return redirect(url_for("main.admin_users"))

    user.is_active = not user.is_active
    db.session.commit()
    return redirect(url_for("main.admin_users"))

@main_bp.route("/admin/courses", methods=["GET", 'POST'])
@admin_required
def admin_courses():
    """
    Panel administratora: zarządzanie kursami.

    GET:
        - wyświetla listę kursów,
        - formularz dodawania nowego kursu.

    POST:
        - tworzy nowy kurs na podstawie danych z formularza.
    """
    from app import db
    from app.models import Course, User, UserRole

    message = None
    error = None

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        name = request.form.get("name", "").strip()
        ects = request.form.get("ects", "").strip()
        description = request.form.get("description", "").strip()
        lecturer_id = request.form.get("lecturer_id", "").strip()

        # Prosta walidacja
        if not code or not name or not ects or not lecturer_id:
            error = "Pola: kod, nazwa, ECTS i prowadzący są wymagane."
        else:
            try:
                ects_int = int(ects)
            except ValueError:
                error = "ECTS musi być liczbą całkowitą."
            else:
                # Sprawdź, czy kod kursu jest unikalny
                from app.models import Course
                existing = Course.query.filter_by(code=code).first()
                if existing:
                    error = f"Kurs o kodzie {code} już istnieje."
                else:
                    lecturer = User.query.get(int(lecturer_id))
                    if not lecturer or lecturer.role != UserRole.LECTURER:
                        error = "Wybrany prowadzący nie jest wykładowcą."
                    else:
                        new_course = Course(
                            code=code,
                            name=name,
                            ects=ects_int,
                            description=description or None,
                            lecturer_id=lecturer.id,
                        )
                        db.session.add(new_course)
                        db.session.commit()
                        message = "Kurs został utworzony."

    from app.models import Course, User, UserRole

    # Lista wszystkich kursów
    courses = Course.query.order_by(Course.code.asc()).all()

    # Lista wykładowców do wyboru w formularzu
    lecturers = User.query.filter_by(role=UserRole.LECTURER).order_by(User.last_name.asc()).all()

    return render_template(
        "admin_courses.html",
        courses=courses,
        lecturers=lecturers,
        message=message,
        error=error,
    )

@main_bp.route("/admin/courses/<int:course_id>/toggle", methods=["POST"])
@admin_required
def admin_toggle_course(course_id: int):
    """
    Przełącza status kursu (aktywny / nieaktywny).

    Dzięki temu zamiast usuwać kurs, możemy go tylko wyłączyć,
    a dane (np. oceny) zostają w bazie.
    """
    from app import db
    from app.models import Course

    course = Course.query.get_or_404(course_id)
    course.is_active = not course.is_active
    db.session.commit()

    return redirect(url_for("main.admin_courses"))

@main_bp.route("/admin/groups", methods=["GET", "POST"])
@admin_required
def admin_groups():
    """
    Panel administratora: zarządzanie grupami zajęciowymi.

    GET:
        - lista wszystkich grup,
        - formularz dodania nowej grupy.

    POST:
        - tworzy nową grupę na podstawie danych z formularza.
    """
    from app import db
    from app.models import ClassGroup, Course, User, UserRole

    message = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        course_id = request.form.get("course_id", "").strip()
        lecturer_id = request.form.get("lecturer_id", "").strip()
        semester = request.form.get("semester", "").strip()
        year = request.form.get("year", "").strip()

        if not name or not course_id or not lecturer_id:
            error = "Pola: nazwa grupy, kurs i prowadzący są wymagane."
        else:
            try:
                semester_int = int(semester) if semester else None
                year_int = int(year) if year else None
            except ValueError:
                error = "Semestr i rok muszą być liczbami."
            else:
                course = Course.query.get(int(course_id))
                lecturer = User.query.get(int(lecturer_id))

                if not course:
                    error = "Wybrany kurs nie istnieje."
                elif not lecturer or lecturer.role != UserRole.LECTURER:
                    error = "Wybrany prowadzący nie jest wykładowcą."
                else:
                    new_group = ClassGroup(
                        name=name,
                        course_id=course.id,
                        lecturer_id=lecturer.id,
                        semester=semester_int,
                        year=year_int,
                    )
                    db.session.add(new_group)
                    db.session.commit()
                    message = "Grupa została utworzona."

    from app.models import ClassGroup, Course, User, UserRole

    groups = (
        ClassGroup.query
        .order_by(ClassGroup.year.desc(), ClassGroup.semester.desc(), ClassGroup.name.asc())
        .all()
    )
    courses = Course.query.filter_by(is_active=True).order_by(Course.code.asc()).all()
    lecturers = User.query.filter_by(role=UserRole.LECTURER).order_by(User.last_name.asc()).all()

    return render_template(
        "admin_groups.html",
        groups=groups,
        courses=courses,
        lecturers=lecturers,
        message=message,
        error=error,
    )
@main_bp.route("/admin/groups/<int:group_id>/students", methods=["GET", "POST"])
@admin_required
def admin_group_students(group_id: int):
    """
    Panel admina: zarządzanie studentami w konkretnej grupie.
    """
    from app import db
    from app.models import ClassGroup, Enrollment, User, UserRole

    group = ClassGroup.query.get_or_404(group_id)

    message = None
    error = None

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        if not student_id:
            error = "Musisz wybrać studenta."
        else:
            student = User.query.get(int(student_id))
            if not student or student.role != UserRole.STUDENT:
                error = "Wybrany użytkownik nie jest studentem."
            else:
                existing = Enrollment.query.filter_by(
                    student_id=student.id,
                    group_id=group.id,
                    is_active=True,
                ).first()
                if existing:
                    error = "Ten student jest już zapisany do tej grupy."
                else:
                    enr = Enrollment(
                        student_id=student.id,
                        group_id=group.id,
                    )
                    db.session.add(enr)
                    db.session.commit()
                    message = "Student został dodany do grupy."

    # UWAGA: ten kod musi być poza if-em, wewnątrz funkcji
    enrollments = (
        Enrollment.query
        .filter_by(group_id=group.id, is_active=True)
        .join(User, Enrollment.student_id == User.id)
        .order_by(User.last_name.asc(), User.first_name.asc())
        .all()
    )

    students = (
        User.query
        .filter_by(role=UserRole.STUDENT, is_active=True)
        .order_by(User.last_name.asc(), User.first_name.asc())
        .all()
    )

    # I TO MUSI BYĆ OSTATNIE – zawsze zwracamy odpowiedź
    return render_template(
        "admin_group_students.html",
        group=group,
        enrollments=enrollments,
        students=students,
        message=message,
        error=error,
    )


@main_bp.route("/admin/enrollments/<int:enrollment_id>/remove", methods=["POST"])
@admin_required
def admin_remove_enrollment(enrollment_id: int):
    """
    Usuwa (dezaktywuje) zapis studenta do grupy.
    """
    from app import db
    from app.models import Enrollment

    enr = Enrollment.query.get_or_404(enrollment_id)
    group_id = enr.group_id

    enr.is_active = False
    db.session.commit()

    return redirect(url_for("main.admin_group_students", group_id=group_id))

def lecturer_required(view_func):
    """
    Dekorator sprawdzający, czy zalogowany użytkownik ma rolę 'lecturer'.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        role = session.get("role")
        if role != "lecturer":
            return abort(403)
        return view_func(*args, **kwargs)
    return wrapped_view


@main_bp.route("/lecturer/courses")
@lecturer_required
def lecturer_courses():
    """
    Panel wykładowcy: lista jego kursów i grup zajęciowych.
    """
    from app.models import Course, ClassGroup

    user_id = session.get("user_id")
    lecturer = User.query.get_or_404(user_id)

    # Kursy prowadzone przez tego wykładowcę
    courses = (
        Course.query
        .filter_by(lecturer_id=lecturer.id)
        .order_by(Course.code.asc())
        .all()
    )

    # Grupy prowadzone przez tego wykładowcę
    groups = (
        ClassGroup.query
        .filter_by(lecturer_id=lecturer.id)
        .order_by(ClassGroup.name.asc())
        .all()
    )

    return render_template(
        "lecturer_courses.html",
        lecturer=lecturer,
        courses=courses,
        groups=groups,
    )
