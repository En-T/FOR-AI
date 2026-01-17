from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class School(models.Model):
    GRADUATION_CLASS_CHOICES = [
        (4, "4"),
        (9, "9"),
        (11, "11"),
    ]

    name = models.CharField(max_length=255, verbose_name="Название школы")
    director = models.CharField(max_length=255, verbose_name="ФИО директора")
    graduation_class = models.IntegerField(
        choices=GRADUATION_CLASS_CHOICES, verbose_name="Выпускной класс"
    )
    location = models.TextField(verbose_name="Расположение/адрес")

    education_dept_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schools",
        verbose_name="Пользователь отдела образования",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserProfile(models.Model):
    ROLE_SUPERUSER = "superuser"
    ROLE_EDUCATION_DEPT = "education_dept"
    ROLE_SCHOOL_ADMIN = "school_admin"

    ROLE_CHOICES = [
        (ROLE_SUPERUSER, "Superuser"),
        (ROLE_EDUCATION_DEPT, "Отдел образования"),
        (ROLE_SCHOOL_ADMIN, "Администратор школы"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="Пользователь"
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_SCHOOL_ADMIN, verbose_name="Роль"
    )
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="school_admin_profiles",
        verbose_name="Школа",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_role_display()})"


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название предмета")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название класса")
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="classes", verbose_name="Школа"
    )
    graduation_class = models.IntegerField(
        choices=School.GRADUATION_CLASS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Выпускной класс",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
        ordering = ["school", "name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "name"], name="uniq_class_name_per_school")
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.graduation_class is None and self.school_id is not None:
            self.graduation_class = self.school.graduation_class
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.school.name} — {self.name}"


class Student(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")

    student_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="students", verbose_name="Класс"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Учащийся"
        verbose_name_plural = "Учащиеся"
        ordering = ["last_name", "first_name", "patronymic"]

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join([p for p in parts if p]).strip()

    def __str__(self) -> str:
        return self.full_name


class Teacher(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="teachers", verbose_name="Школа"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"
        ordering = ["last_name", "first_name", "patronymic"]

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join([p for p in parts if p]).strip()

    def __str__(self) -> str:
        return self.full_name


class ClassSubjectGroup(models.Model):
    LEVEL_BASIC = "basic"
    LEVEL_ADVANCED = "advanced"

    LEVEL_CHOICES = [
        (LEVEL_BASIC, "Базовый"),
        (LEVEL_ADVANCED, "Повышенный"),
    ]

    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="subject_groups",
        verbose_name="Класс",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="class_subject_groups",
        verbose_name="Предмет",
    )
    teachers = models.ManyToManyField(
        Teacher, related_name="class_subject_groups", blank=True, verbose_name="Учителя"
    )

    level = models.CharField(
        max_length=20, choices=LEVEL_CHOICES, default=LEVEL_BASIC, verbose_name="Уровень"
    )
    group_number = models.PositiveIntegerField(default=1, verbose_name="Номер подгруппы")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Подгруппа для предмета в классе"
        verbose_name_plural = "Подгруппы для предметов в классах"
        ordering = ["class_obj", "subject", "group_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_obj", "subject", "group_number"],
                name="uniq_subject_group_number",
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.class_obj} — {self.subject} — {self.get_level_display()}"
            f" (группа {self.group_number})"
        )


class StudentSubjectGroup(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="subject_group_links",
        verbose_name="Учащийся",
    )
    subject_group = models.ForeignKey(
        ClassSubjectGroup,
        on_delete=models.CASCADE,
        related_name="student_links",
        verbose_name="Подгруппа",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Распределение учащегося по подгруппе"
        verbose_name_plural = "Распределения учащихся по подгруппам"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject_group"], name="uniq_student_subject_group"
            )
        ]

    def __str__(self) -> str:
        return f"{self.student} → {self.subject_group}"


class Grade(models.Model):
    QUARTER_Q1 = "q1"
    QUARTER_Q2 = "q2"
    QUARTER_Q3 = "q3"
    QUARTER_Q4 = "q4"
    QUARTER_EXAM = "exam"
    QUARTER_YEAR = "year"
    QUARTER_FINAL = "final"

    QUARTER_CHOICES = [
        (QUARTER_Q1, "Первая четверть"),
        (QUARTER_Q2, "Вторая четверть"),
        (QUARTER_Q3, "Третья четверть"),
        (QUARTER_Q4, "Четвертая четверть"),
        (QUARTER_EXAM, "Экзаменационная"),
        (QUARTER_YEAR, "Годовая"),
        (QUARTER_FINAL, "Итоговая"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="grades", verbose_name="Учащийся"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="grades", verbose_name="Предмет"
    )

    quarter = models.CharField(max_length=10, choices=QUARTER_CHOICES, verbose_name="Период")
    grade = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Оценка",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        ordering = ["student", "subject", "quarter"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject", "quarter"], name="uniq_grade_per_period"
            )
        ]

    def __str__(self) -> str:
        grade_str = str(self.grade) if self.grade is not None else "—"
        return f"{self.student} — {self.subject} — {self.get_quarter_display()}: {grade_str}"


class AuditLog(models.Model):
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"

    ACTION_CHOICES = [
        (ACTION_CREATE, "Создание"),
        (ACTION_UPDATE, "Редактирование"),
        (ACTION_DELETE, "Удаление"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Пользователь",
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="Действие")
    model_name = models.CharField(max_length=100, verbose_name="Модель")
    object_id = models.PositiveBigIntegerField(verbose_name="ID объекта")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время")
    details = models.JSONField(default=dict, blank=True, verbose_name="Детали")

    class Meta:
        verbose_name = "Журнал действий"
        verbose_name_plural = "Журнал действий"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        user_str = self.user.username if self.user else "system"
        return f"{user_str}: {self.action} {self.model_name}#{self.object_id}"
