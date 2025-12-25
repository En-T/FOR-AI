from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class UserRole:
    ADMIN_SCHOOL = 'admin_school'
    DEPT_EDUCATION = 'dept_education'
    CHOICES = [
        (ADMIN_SCHOOL, 'Администратор школы'),
        (DEPT_EDUCATION, 'Департамент образования'),
    ]


class Quarter:
    Q1 = 'q1'
    Q2 = 'q2'
    Q3 = 'q3'
    Q4 = 'q4'
    EXAM = 'exam'
    ANNUAL = 'annual'
    FINAL = 'final'
    CHOICES = [
        (Q1, 'Первая четверть'),
        (Q2, 'Вторая четверть'),
        (Q3, 'Третья четверть'),
        (Q4, 'Четвертая четверть'),
        (EXAM, 'Экзаменационная'),
        (ANNUAL, 'Годовая'),
        (FINAL, 'Итоговая'),
    ]


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=UserRole.CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    class Meta:
        db_table = 'users'


class School(models.Model):
    name = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    graduating_class = models.IntegerField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': UserRole.DEPT_EDUCATION}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'schools'
        unique_together = ('name', 'location')


class Teacher(models.Model):
    full_name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'teachers'
        unique_together = ('full_name', 'school')


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'subjects'


def validate_class_name(value):
    import re
    pattern = r'^\d{1,2}[А-Яа-я]?$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Имя класса должно быть в формате "5" или "5А/Б/В/Г/Д/Е/Ж/З/И"'
        )


class Class(models.Model):
    name = models.CharField(max_length=50, validators=[validate_class_name])
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'classes'
        unique_together = ('name', 'school')


class Subgroup(models.Model):
    name = models.CharField(max_length=50)
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='subgroups'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subgroups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name} - {self.name}"

    class Meta:
        db_table = 'subgroups'
        unique_together = ('name', 'class_obj', 'subject')


class Student(models.Model):
    full_name = models.CharField(max_length=255)
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='students'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'students'


class StudentSubgroupAssignment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='subgroup_assignments'
    )
    subgroup = models.ForeignKey(
        Subgroup,
        on_delete=models.CASCADE,
        related_name='student_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.subgroup}"

    class Meta:
        db_table = 'student_subgroup_assignments'
        unique_together = ('student', 'subgroup')


def validate_teacher_school(teacher, subgroup):
    if teacher.school_id != subgroup.class_obj.school_id:
        raise ValidationError('Учитель и подгруппа должны быть из одной школы')


class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        validate_teacher_school(self.teacher, self.subgroup)

    def __str__(self):
        return f"{self.teacher} - {self.subgroup}"

    class Meta:
        db_table = 'teacher_assignments'
        unique_together = ('teacher', 'subgroup')


def validate_grade(value):
    if value is not None and (value < 1 or value > 10):
        raise ValidationError('Оценка должна быть от 1 до 10 или пустой')


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    quarter = models.CharField(max_length=20, choices=Quarter.CHOICES)
    grade = models.IntegerField(null=True, blank=True, validators=[validate_grade])
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': UserRole.ADMIN_SCHOOL}
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.grade}"

    class Meta:
        db_table = 'grades'
        unique_together = ('student', 'subject', 'quarter')
