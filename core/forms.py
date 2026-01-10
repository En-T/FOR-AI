from django import forms
from .models import User, School, Subject, AuditLog


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class SchoolForm(forms.ModelForm):
    """Form for creating and updating schools"""
    GRADUATING_CLASS_CHOICES = [
        (4, '4 класс'),
        (9, '9 класс'),
        (11, '11 класс'),
    ]

    graduating_class = forms.ChoiceField(
        choices=GRADUATING_CLASS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Выпускной класс'
    )

    class Meta:
        model = School
        fields = ['name', 'director', 'graduating_class', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название школы'}),
            'director': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО директора'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес/Расположение'}),
        }
        labels = {
            'name': 'Название школы',
            'director': 'Директор',
            'location': 'Расположение',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        location = self.cleaned_data.get('location')
        if name and location:
            if School.objects.filter(name=name, location=location).exists():
                raise forms.ValidationError('Школа с таким названием и расположением уже существует.')
        return name


class DirectorUserCreateForm(forms.ModelForm):
    """Form for creating users by Director of Education (School Administrator only)"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Пароль'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'school']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'school': 'Школа',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'] = forms.ChoiceField(
            choices=[(User.ROLE_ADMIN_SCHOOL, 'School Administrator')],
            widget=forms.HiddenInput(),
            initial=User.ROLE_ADMIN_SCHOOL
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.ROLE_ADMIN_SCHOOL
        if commit:
            user.save()
        return user


class DirectorUserUpdateForm(forms.ModelForm):
    """Form for updating users by Director of Education"""
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'school']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'school': 'Школа',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'] = forms.ChoiceField(
            choices=[(User.ROLE_ADMIN_SCHOOL, 'School Administrator')],
            widget=forms.HiddenInput(),
            initial=User.ROLE_ADMIN_SCHOOL
        )


class SubjectForm(forms.ModelForm):
    """Form for creating and updating subjects"""
    class Meta:
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название предмета'}),
        }
        labels = {
            'name': 'Название предмета',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and Subject.objects.filter(name=name).exists():
            raise forms.ValidationError('Предмет с таким названием уже существует.')
        return name


class UserPasswordSetForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Новый пароль'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Подтвердите пароль'
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        if password != confirm:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data


class LogFilterForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Пользователь'
    )
    action_type = forms.ChoiceField(
        choices=[('', 'Все действия')] + AuditLog.ACTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Тип действия'
    )
    model_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название модели'}),
        label='Модель'
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='От даты'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='До даты'
    )


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'school']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            (User.ROLE_DEPT_EDUCATION, 'Director of Education'),
            (User.ROLE_ADMIN_SCHOOL, 'School Administrator'),
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'school']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            (User.ROLE_DEPT_EDUCATION, 'Director of Education'),
            (User.ROLE_ADMIN_SCHOOL, 'School Administrator'),
        ]
