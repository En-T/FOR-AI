from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password, check_password
import re


class User(models.Model):
    ROLE_ADMIN_SCHOOL = 'admin_school'
    ROLE_DEPT_EDUCATION = 'dept_education'

    ROLE_CHOICES = [
        (ROLE_ADMIN_SCHOOL, 'Admin School'),
        (ROLE_DEPT_EDUCATION, 'Dept Education'),
    ]

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'core_user'


class School(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    graduating_class = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='schools'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_school'
        unique_together = ('name', 'location')
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'core_subject'


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='teachers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_teacher'
        unique_together = ('full_name', 'school')
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Class(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='classes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_class'
        unique_together = ('name', 'school')
        ordering = ['name']

    def clean(self):
        super().clean()
        pattern = r'^[1-9]\d*([А-И])?$'
        if not re.match(pattern, self.name):
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'name': 'Name must be in format: "5" or "5А/Б/В/Г/Д/Е/Ж/З/И"'
            })

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Subgroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    school_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name='subgroups'
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='subgroups'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_subgroup'
        unique_together = ('name', 'school_class', 'subject')
        ordering = ['name']

    def __str__(self):
        return f"{self.school_class.name} - {self.subject.name} - {self.name}"


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    school_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name='students'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_student'
        unique_together = ('full_name', 'school_class')
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class StudentSubgroupAssignment(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='subgroup_assignments'
    )
    subgroup = models.ForeignKey(
        Subgroup, on_delete=models.CASCADE, related_name='student_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_studentsubgroupassignment'
        unique_together = ('student', 'subgroup')

    def __str__(self):
        return f"{self.student.full_name} - {self.subgroup}"


class TeacherAssignment(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='assignments'
    )
    subgroup = models.ForeignKey(
        Subgroup, on_delete=models.CASCADE, related_name='teacher_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_teacherassignment'
        unique_together = ('teacher', 'subgroup')

    def clean(self):
        super().clean()
        if self.teacher.school_id != self.subgroup.school_class.school_id:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'teacher': 'Teacher school must match subgroup class school'
            })

    def __str__(self):
        return f"{self.teacher.full_name} - {self.subgroup}"


class Grade(models.Model):
    QUARTER_CHOICES = [
        ('q1', 'Первая четверть'),
        ('q2', 'Вторая четверть'),
        ('q3', 'Третья четверть'),
        ('q4', 'Четвертая четверть'),
        ('exam', 'Экзаменационная'),
        ('annual', 'Годовая'),
        ('final', 'Итоговая'),
    ]

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='grades'
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='grades'
    )
    quarter = models.CharField(max_length=10, choices=QUARTER_CHOICES)
    grade = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='grades'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_grade'
        unique_together = ('student', 'subject', 'quarter')

    def clean(self):
        super().clean()
        if self.grade is not None and not (1 <= self.grade <= 10):
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'grade': 'Grade must be between 1 and 10 if provided'
            })

    def __str__(self):
        return f"{self.student.full_name} - {self.subject} ({self.quarter}): {self.grade}"
