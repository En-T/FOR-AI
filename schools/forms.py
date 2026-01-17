from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import User, School, ClassGroup, Student, Teacher, Subject, ClassSubjectGroup, Grade

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'director_name', 'graduation_class', 'location']
        labels = {
            'name': _('Название школы'),
            'director_name': _('ФИО директора'),
            'graduation_class': _('Выпускной класс'),
            'location': _('Расположение'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name'),
            Field('director_name'),
            Field('graduation_class'),
            Field('location'),
            Submit('submit', _('Сохранить'), css_class='btn-primary')
        )

class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput,
        required=False,
        help_text=_('Оставьте пустым, чтобы сгенерировать автоматически')
    )
    password2 = forms.CharField(
        label=_('Подтверждение пароля'),
        widget=forms.PasswordInput,
        required=False
    )
    school = forms.ModelChoiceField(
        queryset=School.objects.none(),
        label=_('Школа'),
        required=False,
        help_text=_('Выберите школу для администратора школы')
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'patronymic', 'role', 'school']
        labels = {
            'email': _('Email'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'patronymic': _('Отчество'),
            'role': _('Роль'),
            'school': _('Школа'),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        if self.user and self.user.role == 'education_dept':
            self.fields['role'].choices = [
                ('education_dept', _('Отдел образования')),
                ('school_admin', _('Администратор школы'))
            ]
            # Ограничиваем школы только школами текущего пользователя
            self.fields['school'].queryset = School.objects.filter(education_dept=self.user)
        elif self.user and self.user.role == 'superuser':
            self.fields['school'].queryset = School.objects.all()
        
        layout_fields = [
            Field('email'),
            Row(
                Column(Field('last_name'), css_class='col-md-4'),
                Column(Field('first_name'), css_class='col-md-4'),
                Column(Field('patronymic'), css_class='col-md-4'),
            ),
            Field('role'),
        ]
        
        # Показываем поле школы только для school_admin
        if self.instance.pk and self.instance.role == 'school_admin':
            layout_fields.append(Field('school'))
        elif not self.instance.pk:
            layout_fields.append(Field('school'))
        
        if not self.instance.pk:
            layout_fields.extend([
                Field('password1'),
                Field('password2'),
            ])
        
        layout_fields.append(Submit('submit', _('Сохранить'), css_class='btn-primary'))
        self.helper.layout = Layout(*layout_fields)
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        role = cleaned_data.get('role')
        school = cleaned_data.get('school')
        
        if password1 or password2:
            if password1 != password2:
                raise ValidationError(_('Пароли не совпадают'))
        
        if role == 'school_admin' and not school:
            raise ValidationError(_('Для администратора школы необходимо выбрать школу'))
        
        return cleaned_data

class UserChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        self.by_admin = kwargs.pop('by_admin', False)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        if self.by_admin:
            # Администратор может менять пароль без старого
            self.fields.pop('old_password')
            self.helper.layout = Layout(
                Field('new_password1'),
                Field('new_password2'),
                Submit('submit', _('Изменить пароль'), css_class='btn-primary')
            )
        else:
            self.helper.layout = Layout(
                Field('old_password'),
                Field('new_password1'),
                Field('new_password2'),
                Submit('submit', _('Изменить пароль'), css_class='btn-primary')
            )

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        labels = {
            'name': _('Название предмета'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name'),
            Submit('submit', _('Сохранить'), css_class='btn-primary')
        )

class ClassForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = ['name']
        labels = {
            'name': _('Название класса'),
        }
        help_texts = {
            'name': _('Например: "5А" или "5"'),
        }
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name'),
            Submit('submit', _('Сохранить'), css_class='btn-primary')
        )

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['class_group', 'first_name', 'last_name', 'patronymic']
        labels = {
            'class_group': _('Класс'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'patronymic': _('Отчество'),
        }
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        if self.school:
            self.fields['class_group'].queryset = ClassGroup.objects.filter(school=self.school)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('class_group'),
            Row(
                Column(Field('last_name'), css_class='col-md-4'),
                Column(Field('first_name'), css_class='col-md-4'),
                Column(Field('patronymic'), css_class='col-md-4'),
            ),
            Submit('submit', _('Сохранить'), css_class='btn-primary')
        )

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'patronymic']
        labels = {
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'patronymic': _('Отчество'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column(Field('last_name'), css_class='col-md-4'),
                Column(Field('first_name'), css_class='col-md-4'),
                Column(Field('patronymic'), css_class='col-md-4'),
            ),
            Submit('submit', _('Сохранить'), css_class='btn-primary')
        )

class AssignTeacherToSubjectForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        label=_('Предмет')
    )
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.none(),
        label=_('Учитель')
    )
    level = forms.ChoiceField(
        choices=ClassSubjectGroup.LEVEL_CHOICES,
        label=_('Уровень изучения'),
        initial='basic'
    )
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        self.class_group = kwargs.pop('class_group', None)
        super().__init__(*args, **kwargs)
        
        if self.school:
            self.fields['teacher'].queryset = Teacher.objects.filter(school=self.school)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('subject'),
            Field('teacher'),
            Field('level'),
            Submit('submit', _('Назначить'), css_class='btn-primary')
        )

class GradeJournalForm(forms.Form):
    """Динамическая форма для журнала оценок"""
    
    def __init__(self, *args, **kwargs):
        self.class_group = kwargs.pop('class_group', None)
        students = kwargs.pop('students', [])
        subjects = kwargs.pop('subjects', [])
        grades_data = kwargs.pop('grades_data', {})
        
        super().__init__(*args, **kwargs)
        
        quarters = ['q1', 'q2', 'q3', 'q4', 'exam', 'year', 'final']
        
        for student in students:
            for subject in subjects:
                for quarter in quarters:
                    field_name = f'grade_{student.id}_{subject.id}_{quarter}'
                    current_grade = grades_data.get((student.id, subject.id, quarter))
                    self.fields[field_name] = forms.IntegerField(
                        required=False,
                        min_value=1,
                        max_value=10,
                        initial=current_grade,
                        widget=forms.NumberInput(attrs={
                            'class': 'grade-input',
                            'data-student': student.id,
                            'data-subject': subject.id,
                            'data-quarter': quarter
                        })
                    )

class DistributeStudentsToSubgroupsForm(forms.Form):
    """Форма для распределения учащихся по подгруппам (transfer-box)"""
    
    def __init__(self, *args, **kwargs):
        self.students = kwargs.pop('students', [])
        self.teachers = kwargs.pop('teachers', [])
        self.current_distribution = kwargs.pop('current_distribution', {})
        
        super().__init__(*args, **kwargs)
        
        # Создаем поля для каждой подгруппы
        for i, teacher in enumerate(self.teachers):
            field_name = f'group_{i+1}_students'
            self.fields[field_name] = forms.ModelMultipleChoiceField(
                queryset=self.students,
                required=False,
                label=f'Группа {i+1} ({teacher.get_initials()})',
                initial=self.current_distribution.get(i+1, [])
            )

class AssignTeacherToGroupForm(forms.Form):
    """Форма назначения учителя на предметы в несколько классов"""
    
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        label=_('Предмет')
    )
    class_groups = forms.ModelMultipleChoiceField(
        queryset=ClassGroup.objects.none(),
        label=_('Классы'),
        widget=forms.CheckboxSelectMultiple
    )
    level = forms.ChoiceField(
        choices=ClassSubjectGroup.LEVEL_CHOICES,
        label=_('Уровень изучения'),
        initial='basic'
    )
    
    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        if self.school:
            self.fields['class_groups'].queryset = ClassGroup.objects.filter(school=self.school)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('subject'),
            Field('class_groups'),
            Field('level'),
            Submit('submit', _('Назначить'), css_class='btn-primary')
        )