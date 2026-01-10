from django.db import models
from django.core.exceptions import ValidationError


class School(models.Model):
    class FinalGrade(models.IntegerChoices):
        GRADE_4 = 4, '4 класс'
        GRADE_9 = 9, '9 класс'
        GRADE_11 = 11, '11 класс'

    name = models.CharField(
        max_length=255,
        verbose_name='Название школы'
    )
    director = models.CharField(
        max_length=255,
        verbose_name='Директор (ФИО)'
    )
    final_grade = models.IntegerField(
        choices=FinalGrade.choices,
        verbose_name='Выпускной класс'
    )
    location = models.CharField(
        max_length=255,
        verbose_name='Расположение'
    )
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_schools',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Школа'
        verbose_name_plural = 'Школы'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.location})'


class Subject(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название предмета'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(
        max_length=10,
        verbose_name='Название класса'
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name='Школа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'
        ordering = ['school', 'name']
        unique_together = ['school', 'name']

    def __str__(self):
        return f'{self.name} ({self.school.name})'


class Student(models.Model):
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Отчество'
    )
    class_ref = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name='Класс'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        middle = f' {self.middle_name}' if self.middle_name else ''
        return f'{self.last_name} {self.first_name}{middle}'

    @property
    def full_name(self):
        middle = f' {self.middle_name}' if self.middle_name else ''
        return f'{self.last_name} {self.first_name}{middle}'


class Teacher(models.Model):
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Отчество'
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='teachers',
        verbose_name='Школа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        middle = f' {self.middle_name}' if self.middle_name else ''
        return f'{self.last_name} {self.first_name}{middle}'

    @property
    def full_name(self):
        middle = f' {self.middle_name}' if self.middle_name else ''
        return f'{self.last_name} {self.first_name}{middle}'


class ClassTeacherAssignment(models.Model):
    class StudyLevel(models.TextChoices):
        BASE = 'BASE', 'Базовый'
        ADVANCED = 'ADVANCED', 'Повышенный'

    class_ref = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
        verbose_name='Класс'
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='class_assignments',
        verbose_name='Учитель'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='class_assignments',
        verbose_name='Предмет'
    )
    study_level = models.CharField(
        max_length=20,
        choices=StudyLevel.choices,
        default=StudyLevel.BASE,
        verbose_name='Уровень изучения'
    )
    has_subgroups = models.BooleanField(
        default=False,
        verbose_name='Есть подгруппы'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Назначение учителя'
        verbose_name_plural = 'Назначения учителей'
        ordering = ['class_ref', 'subject']
        unique_together = ['class_ref', 'teacher', 'subject']

    def __str__(self):
        return f'{self.class_ref.name} - {self.subject.name} - {self.teacher.full_name}'


class Subgroup(models.Model):
    assignment = models.ForeignKey(
        ClassTeacherAssignment,
        on_delete=models.CASCADE,
        related_name='subgroups',
        verbose_name='Назначение'
    )
    order = models.PositiveIntegerField(
        verbose_name='Порядковый номер'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Подгруппа'
        verbose_name_plural = 'Подгруппы'
        ordering = ['assignment', 'order']
        unique_together = ['assignment', 'order']

    def __str__(self):
        return f'{self.assignment.subject.name} - {self.assignment.teacher.full_name} - Подгруппа {self.order}'


class SubgroupStudent(models.Model):
    subgroup = models.ForeignKey(
        Subgroup,
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name='Подгруппа'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='subgroups',
        verbose_name='Ученик'
    )

    class Meta:
        verbose_name = 'Ученик в подгруппе'
        verbose_name_plural = 'Ученики в подгруппах'
        ordering = ['subgroup', 'student']
        unique_together = ['subgroup', 'student']

    def __str__(self):
        return f'{self.subgroup} - {self.student.full_name}'


class Grade(models.Model):
    class Quarter(models.TextChoices):
        Q1 = 'Q1', 'Первая'
        Q2 = 'Q2', 'Вторая'
        Q3 = 'Q3', 'Третья'
        Q4 = 'Q4', 'Четвертая'
        EXAM = 'EXAM', 'Экзаменационная'
        YEAR = 'YEAR', 'Годовая'
        FINAL = 'FINAL', 'Итоговая'

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Ученик'
    )
    assignment = models.ForeignKey(
        ClassTeacherAssignment,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Назначение учителя'
    )
    quarter = models.CharField(
        max_length=10,
        choices=Quarter.choices,
        verbose_name='Четверть'
    )
    grade = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Оценка'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        ordering = ['student', 'assignment', 'quarter']
        unique_together = ['student', 'assignment', 'quarter']

    def clean(self):
        if self.grade is not None and (self.grade < 1 or self.grade > 10):
            raise ValidationError({'grade': 'Оценка должна быть от 1 до 10'})

    def __str__(self):
        grade_str = self.grade if self.grade is not None else 'Н/А'
        return f'{self.student.full_name} - {self.assignment.subject.name} - {self.get_quarter_display()}: {grade_str}'
