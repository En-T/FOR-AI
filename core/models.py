from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin_school', 'Администратор школы'),
        ('dept_education', 'Отдел образования'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username


class School(models.Model):
    name = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    graduating_class = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('name', 'location')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Teacher(models.Model):
    full_name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('full_name', 'school')
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name


class Class(models.Model):
    name = models.CharField(max_length=50)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('name', 'school')
        ordering = ['name']
    
    def clean(self):
        super().clean()
        if not re.match(r'^[1-9]\d*([А-И])?$', self.name):
            raise ValidationError('Название класса должно быть в формате: "5" или "5А/Б/В/Г/Д/Е/Ж/З/И"')
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Subgroup(models.Model):
    name = models.CharField(max_length=50)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subgroups')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subgroups')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('name', 'class_obj', 'subject')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name} - {self.name}"


class Student(models.Model):
    full_name = models.CharField(max_length=255)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('full_name', 'class_obj')
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name


class StudentSubgroupAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subgroup_assignments')
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE, related_name='student_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'subgroup')
    
    def __str__(self):
        return f"{self.student.full_name} - {self.subgroup}"


class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE, related_name='teacher_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('teacher', 'subgroup')
    
    def clean(self):
        super().clean()
        if self.teacher.school != self.subgroup.class_obj.school:
            raise ValidationError('Учитель должен принадлежать той же школе, что и подгруппа')
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.subgroup}"


class Grade(models.Model):
    QUARTER_CHOICES = (
        ('q1', 'Первая четверть'),
        ('q2', 'Вторая четверть'),
        ('q3', 'Третья четверть'),
        ('q4', 'Четвертая четверть'),
        ('exam', 'Экзаменационная'),
        ('annual', 'Годовая'),
        ('final', 'Итоговая'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    quarter = models.CharField(max_length=10, choices=QUARTER_CHOICES)
    grade = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'quarter')
    
    def clean(self):
        super().clean()
        if self.grade is not None:
            if not (1 <= self.grade <= 10):
                raise ValidationError('Оценка должна быть от 1 до 10')
    
    def __str__(self):
        grade_str = str(self.grade) if self.grade is not None else 'Не оценен'
        return f"{self.student.full_name} - {self.subject} ({self.quarter}): {grade_str}"
