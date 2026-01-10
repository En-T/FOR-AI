from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class StudyLevel(models.TextChoices):
    BASIC = "basic", "Базовый"
    ADVANCED = "advanced", "Повышенный"


class Quarter(models.TextChoices):
    Q1 = "q1", "Первая"
    Q2 = "q2", "Вторая"
    Q3 = "q3", "Третья"
    Q4 = "q4", "Четвертая"
    EXAM = "exam", "Экзаменационная"
    YEAR = "year", "Годовая"
    FINAL = "final", "Итоговая"


class AuditAction(models.TextChoices):
    CREATE = "CREATE", "CREATE"
    UPDATE = "UPDATE", "UPDATE"
    DELETE = "DELETE", "DELETE"


class School(models.Model):
    name = models.CharField(max_length=255)
    principal = models.CharField(max_length=255, blank=True)
    graduation_class = models.CharField(max_length=64, blank=True)
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"

    def __str__(self) -> str:
        return self.name


class SchoolAdminProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="school_admin_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admins")

    class Meta:
        verbose_name = "Администратор школы"
        verbose_name_plural = "Администраторы школ"

    def __str__(self) -> str:
        return f"{self.user} ({self.school})"


class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        unique_together = ("school", "name")

    def __str__(self) -> str:
        return self.name


class SchoolClass(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
        unique_together = ("school", "name")

    def __str__(self) -> str:
        return self.name


class PersonNameMixin(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True)

    class Meta:
        abstract = True

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join([p for p in parts if p]).strip()


class Teacher(PersonNameMixin):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teachers")

    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"
        indexes = [
            models.Index(fields=["school", "last_name", "first_name"], name="teacher_school_name_idx"),
        ]

    def __str__(self) -> str:
        return self.full_name


class Student(PersonNameMixin):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="students")

    class Meta:
        verbose_name = "Учащийся"
        verbose_name_plural = "Учащиеся"
        indexes = [
            models.Index(fields=["school_class", "last_name", "first_name"], name="student_class_name_idx"),
        ]

    @property
    def school(self) -> School:
        return self.school_class.school

    def __str__(self) -> str:
        return self.full_name


class ClassTeacherAssignment(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="assignments")
    study_level = models.CharField(max_length=16, choices=StudyLevel.choices, default=StudyLevel.BASIC)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Назначение учителя"
        verbose_name_plural = "Назначения учителей"
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "subject", "teacher", "study_level"],
                name="uniq_assignment_per_teacher",
            ),
        ]

    def clean(self) -> None:
        if self.subject_id and self.school_class_id:
            if self.subject.school_id != self.school_class.school_id:
                raise ValidationError("Предмет должен принадлежать той же школе, что и класс")
        if self.teacher_id and self.school_class_id:
            if self.teacher.school_id != self.school_class.school_id:
                raise ValidationError("Учитель должен принадлежать той же школе, что и класс")

    def __str__(self) -> str:
        return f"{self.school_class} — {self.subject} ({self.get_study_level_display()}) — {self.teacher}"


class AssignmentStudent(models.Model):
    assignment = models.ForeignKey(ClassTeacherAssignment, on_delete=models.CASCADE, related_name="student_links")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="assignment_links")

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="assignment_student_links")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignment_student_links")
    study_level = models.CharField(max_length=16, choices=StudyLevel.choices)

    class Meta:
        verbose_name = "Участник подгруппы"
        verbose_name_plural = "Участники подгрупп"
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student"], name="uniq_student_per_assignment"),
            models.UniqueConstraint(
                fields=["student", "school_class", "subject", "study_level"],
                name="uniq_student_per_class_subject_level",
            ),
        ]

    def clean(self) -> None:
        if self.student_id and self.school_class_id and self.student.school_class_id != self.school_class_id:
            raise ValidationError("Учащийся должен принадлежать указанному классу")
        if self.assignment_id:
            if self.assignment.school_class_id != self.school_class_id:
                raise ValidationError("Неконсистентные данные: school_class")
            if self.assignment.subject_id != self.subject_id:
                raise ValidationError("Неконсистентные данные: subject")
            if self.assignment.study_level != self.study_level:
                raise ValidationError("Неконсистентные данные: study_level")

    def save(self, *args, **kwargs):
        if self.assignment_id:
            self.school_class_id = self.assignment.school_class_id
            self.subject_id = self.assignment.subject_id
            self.study_level = self.assignment.study_level
        self.full_clean()
        return super().save(*args, **kwargs)


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grades")
    assignment = models.ForeignKey(ClassTeacherAssignment, on_delete=models.CASCADE, related_name="grades")
    quarter = models.CharField(max_length=16, choices=Quarter.choices)
    grade = models.PositiveSmallIntegerField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        constraints = [
            models.UniqueConstraint(fields=["student", "assignment", "quarter"], name="uniq_grade"),
            models.CheckConstraint(check=Q(grade__isnull=True) | Q(grade__gte=1, grade__lte=10), name="grade_1_10"),
        ]

    def clean(self) -> None:
        if self.student_id and self.assignment_id:
            if self.student.school_class_id != self.assignment.school_class_id:
                raise ValidationError("Оценка должна относиться к учащемуся из этого класса")

    def __str__(self) -> str:
        return f"{self.student} {self.assignment} {self.quarter}={self.grade}"


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=16, choices=AuditAction.choices)
    model = models.CharField(max_length=128)
    object_id = models.CharField(max_length=64)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Лог действий"
        verbose_name_plural = "Логи действий"
        indexes = [models.Index(fields=["created_at"], name="auditlog_created_at_idx")]

    def __str__(self) -> str:
        return f"{self.created_at} {self.action} {self.model} {self.object_id}"
