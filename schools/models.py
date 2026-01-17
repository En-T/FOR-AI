import os
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import Q, Avg
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger('schools')

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Email должен быть указан'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superuser')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))
        
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'Администратор системы'),
        ('education_dept', 'Отдел образования'),
        ('school_admin', 'Администратор школы'),
    ]
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(_('роль'), max_length=20, choices=ROLE_CHOICES)
    first_name = models.CharField(_('имя'), max_length=150, blank=True)
    last_name = models.CharField(_('фамилия'), max_length=150, blank=True)
    patronymic = models.CharField(_('отчество'), max_length=150, blank=True)
    school = models.ForeignKey(
        'School', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_('школа'),
        related_name='admins'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(filter(None, parts)).strip() or self.email
    
    def get_initials(self):
        initials = ''
        if self.first_name:
            initials += self.first_name[0] + '.'
        if self.patronymic:
            initials += self.patronymic[0] + '.'
        return f"{self.last_name} {initials}".strip()

class School(models.Model):
    GRADUATION_CLASS_CHOICES = [
        (4, '4 класс'),
        (9, '9 класс'),
        (11, '11 класс'),
    ]
    
    name = models.CharField(_('название школы'), max_length=255)
    director_name = models.CharField(_('ФИО директора'), max_length=255, blank=True)
    graduation_class = models.IntegerField(_('выпускной класс'), choices=GRADUATION_CLASS_CHOICES)
    location = models.CharField(_('расположение'), max_length=255, blank=True)
    education_dept = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('отдел образования'),
        limit_choices_to={'role': 'education_dept'},
        related_name='schools'
    )
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('школа')
        verbose_name_plural = _('школы')
        
    def __str__(self):
        return self.name
    
    def get_statistics(self):
        classes = self.classes.all()
        students = Student.objects.filter(class_group__school=self)
        teachers = Teacher.objects.filter(school=self)
        
        class_count = classes.count()
        student_count = students.count()
        teacher_count = teachers.count()
        
        average_grade = Grade.objects.filter(
            student__in=students,
            quarter__in=['q1', 'q2', 'q3', 'q4']
        ).aggregate(avg=Avg('grade'))['avg'] or 0
        
        return {
            'class_count': class_count,
            'student_count': student_count,
            'teacher_count': teacher_count,
            'average_grade': round(average_grade, 2) if average_grade else 0
        }

class Teacher(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name=_('школа'), related_name='teachers')
    first_name = models.CharField(_('имя'), max_length=150)
    last_name = models.CharField(_('фамилия'), max_length=150)
    patronymic = models.CharField(_('отчество'), max_length=150, blank=True)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('учитель')
        verbose_name_plural = _('учителя')
        
    def __str__(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(filter(None, parts))
    
    def get_initials(self):
        initials = ''
        if self.first_name:
            initials += self.first_name[0] + '.'
        if self.patronymic:
            initials += self.patronymic[0] + '.'
        return f"{self.last_name} {initials}".strip()

class Subject(models.Model):
    name = models.CharField(_('название предмета'), max_length=255, unique=True)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('предмет')
        verbose_name_plural = _('предметы')
        
    def __str__(self):
        return self.name

class ClassGroup(models.Model):
    name = models.CharField(_('название класса'), max_length=50)
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name=_('школа'), related_name='classes')
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('класс')
        verbose_name_plural = _('классы')
        unique_together = ['name', 'school']
        
    def __str__(self):
        return f"{self.name} ({self.school.name})"
    
    def get_average_grade(self):
        students = self.students.all()
        if not students:
            return 0
        
        average = Grade.objects.filter(
            student__in=students,
            quarter__in=['q1', 'q2', 'q3', 'q4']
        ).aggregate(avg=Avg('grade'))['avg']
        
        return round(average, 2) if average else 0

class Student(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, verbose_name=_('класс'), related_name='students')
    first_name = models.CharField(_('имя'), max_length=150)
    last_name = models.CharField(_('фамилия'), max_length=150)
    patronymic = models.CharField(_('отчество'), max_length=150, blank=True)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('учащийся')
        verbose_name_plural = _('учащиеся')
        
    def __str__(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(filter(None, parts))
    
    def get_initials(self):
        initials = ''
        if self.first_name:
            initials += self.first_name[0] + '.'
        if self.patronymic:
            initials += self.patronymic[0] + '.'
        return f"{self.last_name} {initials}".strip()
    
    def get_average_by_quarter(self, quarter):
        grades = Grade.objects.filter(student=self, quarter=quarter).exclude(grade__isnull=True)
        avg = grades.aggregate(avg=Avg('grade'))['avg']
        return round(avg, 2) if avg else None
    
    def get_year_average(self):
        return self.get_average_by_quarter('year')
    
    def get_final_average(self):
        return self.get_average_by_quarter('final')

class ClassSubjectGroup(models.Model):
    LEVEL_CHOICES = [
        ('basic', 'Базовый'),
        ('advanced', 'Повышенный'),
    ]
    
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, verbose_name=_('класс'), related_name='subject_groups')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_('предмет'), related_name='class_groups')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name=_('учитель'), related_name='subject_groups')
    level = models.CharField(_('уровень изучения'), max_length=20, choices=LEVEL_CHOICES, default='basic')
    group_number = models.IntegerField(_('номер группы'), default=1)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('назначение предмета')
        verbose_name_plural = _('назначения предметов')
        unique_together = ['class_group', 'subject', 'teacher', 'group_number']
        
    def __str__(self):
        return f"{self.class_group} - {self.subject} - {self.teacher} (Группа {self.group_number})"

class StudentSubjectGroup(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('учащийся'), related_name='subject_groups')
    subject_group = models.ForeignKey(ClassSubjectGroup, on_delete=models.CASCADE, verbose_name=_('группа предмета'), related_name='student_members')
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('распределение учащегося по группе')
        verbose_name_plural = _('распределения учащихся по группам')
        unique_together = ['student', 'subject_group']
        
    def __str__(self):
        return f"{self.student} - {self.subject_group}"

class Grade(models.Model):
    QUARTER_CHOICES = [
        ('q1', 'Первая четверть'),
        ('q2', 'Вторая четверть'),
        ('q3', 'Третья четверть'),
        ('q4', 'Четвертая четверть'),
        ('exam', 'Экзаменационная'),
        ('year', 'Годовая'),
        ('final', 'Итоговая'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('учащийся'), related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_('предмет'), related_name='grades')
    quarter = models.CharField(_('четверть'), max_length=20, choices=QUARTER_CHOICES)
    grade = models.IntegerField(_('оценка'), null=True, blank=True, validators=[
        MinValueValidator(1),
        MaxValueValidator(10)
    ])
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('оценка')
        verbose_name_plural = _('оценки')
        unique_together = ['student', 'subject', 'quarter']
        
    def __str__(self):
        quarter_display = dict(self.QUARTER_CHOICES).get(self.quarter, self.quarter)
        return f"{self.student} - {self.subject} - {quarter_display}: {self.grade}"
    
    def clean(self):
        if self.grade is not None and (self.grade < 1 or self.grade > 10):
            raise ValidationError(_('Оценка должна быть от 1 до 10'))

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Создание'),
        ('update', 'Обновление'),
        ('delete', 'Удаление'),
        ('login', 'Вход'),
        ('logout', 'Выход'),
        ('password_change', 'Смена пароля'),
    ]
    
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('пользователь'), related_name='audit_logs')
    action = models.CharField(_('действие'), max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(_('модель'), max_length=100)
    object_id = models.CharField(_('ID объекта'), max_length=255, blank=True)
    details = models.TextField(_('детали'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP адрес'), null=True, blank=True)
    created_at = models.DateTimeField(_('дата и время'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('лог действия')
        verbose_name_plural = _('логи действий')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.actor} - {self.get_action_display()} - {self.model_name} ({self.created_at})"