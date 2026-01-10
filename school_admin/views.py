from __future__ import annotations

import json

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Q
from django.http import HttpRequest
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView

from .forms import (
    AssignmentStudentsForm,
    ClassForm,
    ClassTeacherAssignmentForm,
    ProfileUpdateForm,
    SchoolAdminPasswordChangeForm,
    StudentForm,
    TeacherAssignmentForm,
    TeacherForm,
)
from .mixins import SchoolAdminRequiredMixin, SchoolObjectAccessMixin, SuccessMessageMixin
from .models import (
    AuditAction,
    AssignmentStudent,
    ClassTeacherAssignment,
    Grade,
    Quarter,
    SchoolClass,
    Student,
    Subject,
    Teacher,
)
from .utils import get_class_average_grade, get_school_classes, get_student_average_grade, log_action


class SchoolAdminDashboardView(SchoolAdminRequiredMixin, TemplateView):
    template_name = "admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.school
        context.update(
            {
                "school": school,
                "classes_count": SchoolClass.objects.filter(school=school).count(),
                "students_count": Student.objects.filter(school_class__school=school).count(),
                "teachers_count": Teacher.objects.filter(school=school).count(),
                "subjects_count": Subject.objects.filter(school=school).count(),
            }
        )
        return context


class ClassListView(SchoolAdminRequiredMixin, ListView):
    model = SchoolClass
    template_name = "admin/classes/list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = SchoolClass.objects.filter(school=self.school).annotate(students_count=Count("students"))
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["school"] = self.school
        return context


class ClassCreateView(SchoolAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = SchoolClass
    form_class = ClassForm
    template_name = "admin/classes/create.html"
    success_message = "Класс создан"

    def form_valid(self, form):
        form.instance.school = self.school
        response = super().form_valid(form)
        log_action(actor=self.request.user, action=AuditAction.CREATE, instance=self.object)
        return response

    def get_success_url(self):
        return reverse("school_admin:class_detail", kwargs={"pk": self.object.pk})


class ClassDetailView(SchoolObjectAccessMixin, DetailView):
    model = SchoolClass
    template_name = "admin/classes/detail.html"
    school_lookup_path = "school"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school_class: SchoolClass = self.object

        students = list(school_class.students.all().order_by("last_name", "first_name", "middle_name"))
        avg_by_student_id = {
            row["student_id"]: row["avg"]
            for row in Grade.objects.filter(student__in=students, grade__isnull=False)
            .values("student_id")
            .annotate(avg=Avg("grade"))
        }
        student_rows = [{"obj": s, "avg": avg_by_student_id.get(s.id)} for s in students]

        assignments = (
            school_class.assignments.select_related("subject", "teacher")
            .annotate(student_count=Count("student_links"))
            .order_by("subject__name", "study_level", "teacher__last_name")
        )

        context.update(
            {
                "school": school_class.school,
                "students": student_rows,
                "students_count": len(students),
                "class_avg": get_class_average_grade(school_class=school_class),
                "assignments": assignments,
            }
        )
        return context


class ClassUpdateView(SchoolObjectAccessMixin, SuccessMessageMixin, UpdateView):
    model = SchoolClass
    form_class = ClassForm
    template_name = "admin/classes/update.html"
    school_lookup_path = "school"
    success_message = "Класс обновлен"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(actor=self.request.user, action=AuditAction.UPDATE, instance=self.object)
        return response

    def get_success_url(self):
        return reverse("school_admin:class_detail", kwargs={"pk": self.object.pk})


class ClassDeleteView(SchoolObjectAccessMixin, DeleteView):
    model = SchoolClass
    template_name = "admin/classes/delete.html"
    school_lookup_path = "school"
    success_url = reverse_lazy("school_admin:class_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(actor=request.user, action=AuditAction.DELETE, instance=self.object)
        messages.success(request, "Класс удален")
        return super().delete(request, *args, **kwargs)


class TeacherListView(SchoolAdminRequiredMixin, ListView):
    model = Teacher
    template_name = "admin/teachers/list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = Teacher.objects.filter(school=self.school).annotate(assignments_count=Count("assignments"))
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(middle_name__icontains=q)
            )
        return qs.order_by("last_name", "first_name", "middle_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["school"] = self.school
        return context


class TeacherCreateView(SchoolAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "admin/teachers/create.html"
    success_message = "Учитель создан"

    def form_valid(self, form):
        form.instance.school = self.school
        response = super().form_valid(form)
        log_action(actor=self.request.user, action=AuditAction.CREATE, instance=self.object)
        return response

    def get_success_url(self):
        return reverse("school_admin:teacher_detail", kwargs={"pk": self.object.pk})


class TeacherDetailView(SchoolObjectAccessMixin, DetailView):
    model = Teacher
    template_name = "admin/teachers/detail.html"
    school_lookup_path = "school"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher: Teacher = self.object
        assignments = teacher.assignments.select_related("school_class", "subject").order_by(
            "school_class__name", "subject__name"
        )
        context.update({"assignments": assignments, "school": self.school})
        return context


class TeacherUpdateView(SchoolObjectAccessMixin, SuccessMessageMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "admin/teachers/update.html"
    school_lookup_path = "school"
    success_message = "Учитель обновлен"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(actor=self.request.user, action=AuditAction.UPDATE, instance=self.object)
        return response

    def get_success_url(self):
        return reverse("school_admin:teacher_detail", kwargs={"pk": self.object.pk})


class TeacherDeleteView(SchoolObjectAccessMixin, DeleteView):
    model = Teacher
    template_name = "admin/teachers/delete.html"
    school_lookup_path = "school"
    success_url = reverse_lazy("school_admin:teacher_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(actor=request.user, action=AuditAction.DELETE, instance=self.object)
        messages.success(request, "Учитель удален")
        return super().delete(request, *args, **kwargs)


class TeacherAssignmentCreateView(SchoolAdminRequiredMixin, FormView):
    template_name = "admin/teachers/assignment_create.html"
    form_class = TeacherAssignmentForm

    def dispatch(self, request, *args, **kwargs):
        self.teacher = get_object_or_404(Teacher, pk=kwargs["pk"], school=self.school)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "subject_qs": Subject.objects.filter(school=self.school).order_by("name"),
                "class_qs": SchoolClass.objects.filter(school=self.school).order_by("name"),
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"teacher": self.teacher})
        return context

    def form_valid(self, form):
        teacher: Teacher = self.teacher
        subject: Subject = form.cleaned_data["subject"]
        classes = form.cleaned_data["classes"]
        study_level = form.cleaned_data["study_level"]

        created = 0
        with transaction.atomic():
            for school_class in classes:
                assignment, was_created = ClassTeacherAssignment.objects.get_or_create(
                    school_class=school_class,
                    subject=subject,
                    teacher=teacher,
                    study_level=study_level,
                )
                if not was_created:
                    continue

                created += 1
                log_action(actor=self.request.user, action=AuditAction.CREATE, instance=assignment)

                peers = ClassTeacherAssignment.objects.filter(
                    school_class=school_class,
                    subject=subject,
                    study_level=study_level,
                ).exclude(pk=assignment.pk)
                if not peers.exists():
                    students = list(school_class.students.all())
                    AssignmentStudent.objects.bulk_create(
                        [
                            AssignmentStudent(
                                assignment=assignment,
                                student=s,
                                school_class=assignment.school_class,
                                subject=assignment.subject,
                                study_level=assignment.study_level,
                            )
                            for s in students
                        ]
                    )

        messages.success(self.request, f"Назначения созданы: {created}")
        return redirect("school_admin:teacher_detail", pk=teacher.pk)


class StudentListView(SchoolAdminRequiredMixin, ListView):
    model = Student
    template_name = "admin/students/list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Student.objects.filter(school_class__school=self.school)
            .select_related("school_class")
            .annotate(avg_grade=Avg("grades__grade"))
        )

        q = self.request.GET.get("q")
        class_id = self.request.GET.get("class")
        if class_id:
            qs = qs.filter(school_class_id=class_id)
        if q:
            qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(middle_name__icontains=q))
        return qs.order_by("school_class__name", "last_name", "first_name", "middle_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "q": self.request.GET.get("q", ""),
                "class_filter": self.request.GET.get("class", ""),
                "classes": get_school_classes(school=self.school),
                "school": self.school,
            }
        )
        return context


class StudentCreateView(SchoolAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = "admin/students/create.html"
    success_message = "Учащийся добавлен"

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(SchoolClass, pk=kwargs["pk"], school=self.school)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"school_class": self.school_class, "school": self.school})
        return context

    def form_valid(self, form):
        form.instance.school_class = self.school_class
        response = super().form_valid(form)
        log_action(actor=self.request.user, action=AuditAction.CREATE, instance=self.object)

        student = self.object
        assignments = ClassTeacherAssignment.objects.filter(school_class=self.school_class)
        for subject_id, study_level in assignments.values_list("subject_id", "study_level").distinct():
            subject_assignments = assignments.filter(subject_id=subject_id, study_level=study_level)
            if subject_assignments.count() == 1:
                assignment = subject_assignments.first()
                AssignmentStudent.objects.get_or_create(
                    assignment=assignment,
                    student=student,
                    defaults={
                        "school_class": assignment.school_class,
                        "subject": assignment.subject,
                        "study_level": assignment.study_level,
                    },
                )

        return response

    def get_success_url(self):
        return reverse("school_admin:class_detail", kwargs={"pk": self.school_class.pk})


class StudentDetailView(SchoolAdminRequiredMixin, DetailView):
    model = Student
    template_name = "admin/students/detail.html"

    def get_object(self, queryset=None):
        obj: Student = super().get_object(queryset=queryset)
        if obj.school_class.school_id != self.school.id:
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student: Student = self.object
        school_class = student.school_class

        assignments = (
            ClassTeacherAssignment.objects.filter(school_class=school_class)
            .select_related("subject", "teacher")
            .order_by("subject__name", "study_level", "teacher__last_name")
        )

        quarter_keys = list(Quarter.values)
        grade_map = {(g.assignment_id, g.quarter): g.grade for g in Grade.objects.filter(student=student)}

        rows = []
        for assignment in assignments:
            grades = [grade_map.get((assignment.id, q)) for q in quarter_keys]
            rows.append({"assignment": assignment, "grades": grades})

        context.update(
            {
                "school": self.school,
                "school_class": school_class,
                "avg": get_student_average_grade(student=student),
                "rows": rows,
                "quarters": [Quarter(q) for q in quarter_keys],
            }
        )
        return context


class StudentUpdateView(SchoolAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "admin/students/update.html"
    success_message = "Учащийся обновлен"

    def get_object(self, queryset=None):
        obj: Student = super().get_object(queryset=queryset)
        if obj.school_class.school_id != self.school.id:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(actor=self.request.user, action=AuditAction.UPDATE, instance=self.object)
        return response

    def get_success_url(self):
        return reverse("school_admin:student_detail", kwargs={"pk": self.object.pk})


class StudentDeleteView(SchoolAdminRequiredMixin, DeleteView):
    model = Student
    template_name = "admin/students/delete.html"
    success_url = reverse_lazy("school_admin:student_list")

    def get_object(self, queryset=None):
        obj: Student = super().get_object(queryset=queryset)
        if obj.school_class.school_id != self.school.id:
            raise PermissionDenied
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(actor=request.user, action=AuditAction.DELETE, instance=self.object)
        messages.success(request, "Учащийся удален")
        return super().delete(request, *args, **kwargs)


class ClassTeacherAssignmentCreateView(SchoolAdminRequiredMixin, CreateView):
    model = ClassTeacherAssignment
    form_class = ClassTeacherAssignmentForm
    template_name = "admin/assignments/create.html"

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(SchoolClass, pk=kwargs["pk"], school=self.school)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["subject"].queryset = Subject.objects.filter(school=self.school).order_by("name")
        form.fields["teacher"].queryset = Teacher.objects.filter(school=self.school).order_by(
            "last_name", "first_name", "middle_name"
        )
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"school_class": self.school_class, "school": self.school})
        return context

    def form_valid(self, form):
        form.instance.school_class = self.school_class
        response = super().form_valid(form)

        assignment: ClassTeacherAssignment = self.object
        log_action(actor=self.request.user, action=AuditAction.CREATE, instance=assignment)

        peers = ClassTeacherAssignment.objects.filter(
            school_class=self.school_class,
            subject=assignment.subject,
            study_level=assignment.study_level,
        ).exclude(pk=assignment.pk)

        if not peers.exists():
            students = list(self.school_class.students.all())
            AssignmentStudent.objects.bulk_create(
                [
                    AssignmentStudent(
                        assignment=assignment,
                        student=s,
                        school_class=assignment.school_class,
                        subject=assignment.subject,
                        study_level=assignment.study_level,
                    )
                    for s in students
                ]
            )
            messages.success(self.request, "Назначение создано для всего класса")
            return redirect("school_admin:class_detail", pk=self.school_class.pk)

        messages.info(self.request, "Создано назначение с подгруппами — распределите учащихся")
        return redirect("school_admin:assignment_update", pk=self.school_class.pk, assignment_id=assignment.pk)


class ClassTeacherAssignmentUpdateView(SchoolAdminRequiredMixin, TemplateView):
    template_name = "admin/assignments/update.html"

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(SchoolClass, pk=kwargs["pk"], school=self.school)
        self.assignment = get_object_or_404(
            ClassTeacherAssignment,
            pk=kwargs["assignment_id"],
            school_class=self.school_class,
        )
        return super().dispatch(request, *args, **kwargs)

    def _needs_subgroups(self) -> bool:
        return (
            ClassTeacherAssignment.objects.filter(
                school_class=self.school_class,
                subject=self.assignment.subject,
                study_level=self.assignment.study_level,
            ).count()
            > 1
        )

    def _build_forms(self, *, data=None):
        assignment_form = ClassTeacherAssignmentForm(data=data, instance=self.assignment)
        assignment_form.fields["subject"].queryset = Subject.objects.filter(school=self.school).order_by("name")
        assignment_form.fields["teacher"].queryset = Teacher.objects.filter(school=self.school).order_by(
            "last_name", "first_name", "middle_name"
        )
        assignment_form.fields["subject"].disabled = True
        assignment_form.fields["teacher"].disabled = True

        students_form = AssignmentStudentsForm(
            student_qs=self.school_class.students.all().order_by("last_name", "first_name", "middle_name"),
            data=data,
            initial={
                "students": Student.objects.filter(assignment_links__assignment=self.assignment),
            }
            if data is None
            else None,
        )

        return assignment_form, students_form

    def get(self, request: HttpRequest, *args, **kwargs):
        assignment_form, students_form = self._build_forms()
        return self.render_to_response(
            self.get_context_data(
                school=self.school,
                school_class=self.school_class,
                assignment=self.assignment,
                assignment_form=assignment_form,
                students_form=students_form,
                needs_subgroups=self._needs_subgroups(),
            )
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        assignment_form, students_form = self._build_forms(data=request.POST)
        needs_subgroups = self._needs_subgroups()

        if not assignment_form.is_valid() or not students_form.is_valid():
            return self.render_to_response(
                self.get_context_data(
                    school=self.school,
                    school_class=self.school_class,
                    assignment=self.assignment,
                    assignment_form=assignment_form,
                    students_form=students_form,
                    needs_subgroups=needs_subgroups,
                )
            )

        with transaction.atomic():
            prev_study_level = self.assignment.study_level

            self.assignment = assignment_form.save()
            log_action(actor=request.user, action=AuditAction.UPDATE, instance=self.assignment)

            if prev_study_level != self.assignment.study_level:
                Grade.objects.filter(assignment=self.assignment).delete()
                AssignmentStudent.objects.filter(assignment=self.assignment).delete()

            peer_count = (
                ClassTeacherAssignment.objects.filter(
                    school_class=self.school_class,
                    subject=self.assignment.subject,
                    study_level=self.assignment.study_level,
                )
                .exclude(pk=self.assignment.pk)
                .count()
            )

            if peer_count == 0:
                desired_students = set(self.school_class.students.all())
            else:
                if "students" not in request.POST:
                    messages.info(request, "Для назначения с подгруппами нужно распределить учащихся")
                    return redirect(
                        "school_admin:assignment_update",
                        pk=self.school_class.pk,
                        assignment_id=self.assignment.pk,
                    )
                desired_students = set(students_form.cleaned_data["students"])

            current_students = set(Student.objects.filter(assignment_links__assignment=self.assignment))

            removed = current_students - desired_students
            added = desired_students - current_students

            if removed:
                Grade.objects.filter(student__in=removed, assignment=self.assignment).delete()
                AssignmentStudent.objects.filter(assignment=self.assignment, student__in=removed).delete()

            if added:
                other_assignments = ClassTeacherAssignment.objects.filter(
                    school_class=self.school_class,
                    subject=self.assignment.subject,
                    study_level=self.assignment.study_level,
                ).exclude(pk=self.assignment.pk)

                Grade.objects.filter(student__in=added, assignment__in=other_assignments).delete()
                AssignmentStudent.objects.filter(student__in=added, assignment__in=other_assignments).delete()

                try:
                    AssignmentStudent.objects.bulk_create(
                        [
                            AssignmentStudent(
                                assignment=self.assignment,
                                student=s,
                                school_class=self.assignment.school_class,
                                subject=self.assignment.subject,
                                study_level=self.assignment.study_level,
                            )
                            for s in added
                        ]
                    )
                except IntegrityError as exc:
                    raise ValidationError(
                        "Нельзя назначить учащегося в две подгруппы по одному предмету"
                    ) from exc

        messages.success(request, "Назначение обновлено")
        return redirect("school_admin:class_detail", pk=self.school_class.pk)


class ClassTeacherAssignmentDeleteView(SchoolAdminRequiredMixin, TemplateView):
    template_name = "admin/assignments/delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(SchoolClass, pk=kwargs["pk"], school=self.school)
        self.assignment = get_object_or_404(
            ClassTeacherAssignment,
            pk=kwargs["assignment_id"],
            school_class=self.school_class,
        )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        assignment = self.assignment
        log_action(actor=request.user, action=AuditAction.DELETE, instance=assignment)
        assignment.delete()
        messages.success(request, "Назначение удалено")
        return redirect("school_admin:class_detail", pk=self.school_class.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"school": self.school, "school_class": self.school_class, "assignment": self.assignment})
        return context


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GradeBookView(SchoolAdminRequiredMixin, TemplateView):
    template_name = "admin/gradebook/index.html"

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(SchoolClass, pk=kwargs["pk"], school=self.school)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        students = list(self.school_class.students.all().order_by("last_name", "first_name", "middle_name"))
        assignments = list(
            self.school_class.assignments.select_related("subject", "teacher").order_by(
                "subject__name", "study_level", "teacher__last_name"
            )
        )
        quarter_keys = list(Quarter.values)

        assigned_pairs = set(
            AssignmentStudent.objects.filter(student__in=students, assignment__in=assignments).values_list(
                "student_id", "assignment_id"
            )
        )

        grades = Grade.objects.filter(student__in=students, assignment__in=assignments)
        grade_map = {(g.student_id, g.assignment_id, g.quarter): g.grade for g in grades}

        quarters = [Quarter(q) for q in quarter_keys]

        rows = []
        for student in students:
            assignment_cells = []
            for assignment in assignments:
                enabled = (student.id, assignment.id) in assigned_pairs
                values = [
                    {
                        "quarter": quarter,
                        "grade": grade_map.get((student.id, assignment.id, quarter.value)) if enabled else None,
                        "enabled": enabled,
                    }
                    for quarter in quarters
                ]
                assignment_cells.append({"assignment": assignment, "values": values})
            rows.append({"student": student, "cells": assignment_cells})

        context.update(
            {
                "school": self.school,
                "school_class": self.school_class,
                "assignments": assignments,
                "quarters": quarters,
                "rows": rows,
            }
        )
        return context


@method_decorator(csrf_protect, name="dispatch")
class GradeBookSaveView(SchoolAdminRequiredMixin, View):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Некорректный JSON"}, status=400)

        student_id = payload.get("student_id")
        assignment_id = payload.get("assignment_id")
        quarter = payload.get("quarter")
        grade_value = payload.get("grade")

        if quarter not in Quarter.values:
            return JsonResponse({"status": "error", "message": "Некорректная четверть"}, status=400)

        student = get_object_or_404(Student.objects.select_related("school_class__school"), pk=student_id)
        if student.school_class.school_id != self.school.id:
            raise PermissionDenied

        assignment = get_object_or_404(ClassTeacherAssignment.objects.select_related("school_class"), pk=assignment_id)
        if assignment.school_class.school_id != self.school.id:
            raise PermissionDenied

        if assignment.school_class_id != student.school_class_id:
            return JsonResponse({"status": "error", "message": "Учащийся не из этого класса"}, status=400)

        if not AssignmentStudent.objects.filter(assignment=assignment, student=student).exists():
            return JsonResponse({"status": "error", "message": "Учащийся не входит в подгруппу"}, status=403)

        if grade_value in (None, ""):
            grade_int = None
        else:
            try:
                grade_int = int(grade_value)
            except (TypeError, ValueError):
                return JsonResponse({"status": "error", "message": "Оценка должна быть числом"}, status=400)
            if not (1 <= grade_int <= 10):
                return JsonResponse({"status": "error", "message": "Оценка должна быть 1..10"}, status=400)

        with transaction.atomic():
            grade_obj, created = Grade.objects.get_or_create(
                student=student,
                assignment=assignment,
                quarter=quarter,
                defaults={"grade": grade_int},
            )
            if not created:
                grade_obj.grade = grade_int
                grade_obj.full_clean()
                grade_obj.save(update_fields=["grade", "updated_at"])

            log_action(
                actor=request.user,
                action=AuditAction.UPDATE,
                instance=grade_obj,
                message=f"grade={grade_int}",
            )

        return JsonResponse({"status": "success", "message": "Сохранено", "grade": grade_int})


class SchoolAdminProfileView(SchoolAdminRequiredMixin, TemplateView):
    template_name = "admin/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school"] = self.school
        return context


class SchoolAdminProfileUpdateView(SchoolAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "admin/profile_update.html"
    form_class = ProfileUpdateForm
    success_message = "Профиль обновлен"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(actor=self.request.user, action=AuditAction.UPDATE, instance=self.request.user)
        return response

    def get_success_url(self):
        return reverse("school_admin:profile")


class SchoolAdminPasswordChangeView(SchoolAdminRequiredMixin, FormView):
    template_name = "admin/password_change.html"
    form_class = SchoolAdminPasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, "Пароль изменен")
        log_action(actor=self.request.user, action=AuditAction.UPDATE, instance=self.request.user, message="password")
        return redirect("school_admin:profile")


class SchoolAdminReportView(SchoolAdminRequiredMixin, TemplateView):
    template_name = "admin/report.html"
