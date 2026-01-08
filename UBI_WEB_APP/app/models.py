"""
app/models.py
----------------
Modele bazy danych (SQLAlchemy).

Na początek:
- User: użytkownik systemu (student, wykładowca, admin).
"""

from datetime import datetime
import enum

from app import db


class UserRole(str, enum.Enum):
    """Enum opisujący role użytkownika w systemie."""
    STUDENT = "student"
    LECTURER = "lecturer"
    ADMIN = "admin"


class User(db.Model):
    """
    Model użytkownika.

    Pole `role` określa, czy ktoś jest studentem, wykładowcą czy administratorem.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"

    @property
    def full_name(self) -> str:
        """Zwraca imię i nazwisko w jednej linijce."""
        return f"{self.first_name} {self.last_name}"

    # Pomocnicze metody do sprawdzania ról:
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def is_lecturer(self) -> bool:
        return self.role == UserRole.LECTURER

    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT

class Course(db.Model):
    """
    Kurs (przedmiot), np. 'Programowanie 1', 'Matematyka dyskretna'.

    - prowadzony przez jednego wykładowcę (User o roli LECTURER),
    - może mieć wiele grup (ClassGroup).
    """
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # np. INF101
    name = db.Column(db.String(120), nullable=False)
    ects = db.Column(db.Integer, default=0)  # punkty ECTS
    description = db.Column(db.Text, nullable=True)

    lecturer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lecturer = db.relationship("User", backref="courses", foreign_keys=[lecturer_id])

    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Course {self.code} - {self.name}>"

class ClassGroup(db.Model):
    """
    Grupa zajęciowa w ramach kursu.

    Przykład:
        Kurs: 'Programowanie 1'
        Grupa: 'Grupa A (laboratoria poniedziałek 8:00)'
    """
    __tablename__ = "class_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  # np. 'Grupa A'
    semester = db.Column(db.Integer, nullable=True)
    year = db.Column(db.Integer, nullable=True)

    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    course = db.relationship("Course", backref="groups")

    # prowadzący tej grupy (może być ten sam co główny wykładowca kursu)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lecturer = db.relationship("User", backref="groups", foreign_keys=[lecturer_id])

    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f"<ClassGroup {self.name} ({self.course.code})>"
    

class Enrollment(db.Model):
    """
    Zapis studenta do konkretnej grupy kursu.

    Dzięki temu wiemy:
    - który student chodzi do której grupy,
    - na podstawie tego wyświetlimy listę studentów w grupie,
    - będziemy też przypisywać oceny.
    """
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    student = db.relationship("User", foreign_keys=[student_id], backref="enrollments")

    group_id = db.Column(db.Integer, db.ForeignKey("class_groups.id"), nullable=False)
    group = db.relationship("ClassGroup", backref="enrollments")

    created_at = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Enrollment student={self.student_id}, group={self.group_id}>"


class Lesson(db.Model):
    """
    Pojedyncze zajęcia w kalendarzu.

    Np.:
        Grupa 'Programowanie 1 - A'
        Data: 2026-03-15
        Godziny: 08:00 - 09:30
        Sala: 201
    """
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("class_groups.id"), nullable=False)
    group = db.relationship("ClassGroup", backref="lessons")

    title = db.Column(db.String(120), nullable=False)  # np. 'Wykład', 'Laboratoria'
    room = db.Column(db.String(50), nullable=True)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    is_canceled = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Lesson {self.title} ({self.start_time})>"

class Grade(db.Model):
    """
    Ocena studenta w ramach grupy/kursu.

    Umożliwia:
    - wystawianie wielu ocen (np. 'Kolokwium 1', 'Projekt'),
    - późniejsze liczenie średniej.
    """
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    student = db.relationship("User", foreign_keys=[student_id], backref="grades")

    group_id = db.Column(db.Integer, db.ForeignKey("class_groups.id"), nullable=False)
    group = db.relationship("ClassGroup", backref="grades")

    label = db.Column(db.String(80), nullable=False)  # np. 'Kolokwium 1'
    value = db.Column(db.Float, nullable=False)       # np. 4.5
    weight = db.Column(db.Float, default=1.0)         # waga w średniej

    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Grade {self.label}: {self.value} ({self.student_id})>"
