from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

from .models import ClassTeacherAssignment, SchoolClass, Student, StudyLevel, Subject, Teacher

User = get_user_model()


class ClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name"]


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["first_name", "last_name", "middle_name"]


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["first_name", "last_name", "middle_name"]


class ClassTeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = ClassTeacherAssignment
        fields = ["subject", "teacher", "study_level"]


class AssignmentStudentsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.none(), required=False)

    def __init__(self, *, student_qs, **kwargs):
        super().__init__(**kwargs)
        self.fields["students"].queryset = student_qs


class TeacherAssignmentForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.none())
    classes = forms.ModelMultipleChoiceField(queryset=SchoolClass.objects.none())
    study_level = forms.ChoiceField(choices=StudyLevel.choices, initial=StudyLevel.BASIC)

    def __init__(self, *, subject_qs, class_qs, **kwargs):
        super().__init__(**kwargs)
        self.fields["subject"].queryset = subject_qs
        self.fields["classes"].queryset = class_qs


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class SchoolAdminPasswordChangeForm(PasswordChangeForm):
    pass
