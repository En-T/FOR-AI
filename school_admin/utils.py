from __future__ import annotations

from typing import Iterable

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import Avg

from .models import (
    AuditAction,
    AuditLog,
    ClassTeacherAssignment,
    Grade,
    Quarter,
    School,
    SchoolAdminProfile,
    SchoolClass,
    Student,
    Subject,
    Teacher,
)


def get_school_admin_school(*, user) -> School:
    if not user or isinstance(user, AnonymousUser):
        raise SchoolAdminProfile.DoesNotExist
    profile = SchoolAdminProfile.objects.select_related("school").get(user=user)
    return profile.school


def get_school_classes(*, school: School):
    return SchoolClass.objects.filter(school=school).order_by("name")


def get_school_teachers(*, school: School):
    return Teacher.objects.filter(school=school).order_by("last_name", "first_name", "middle_name")


def get_school_students(*, school: School):
    return Student.objects.filter(school_class__school=school).select_related("school_class").order_by(
        "school_class__name",
        "last_name",
        "first_name",
        "middle_name",
    )


def get_student_average_grade(*, student: Student) -> float | None:
    return (
        Grade.objects.filter(student=student, grade__isnull=False)
        .aggregate(avg=Avg("grade"))
        .get("avg")
    )


def get_class_average_grade(*, school_class: SchoolClass) -> float | None:
    return (
        Grade.objects.filter(student__school_class=school_class, grade__isnull=False)
        .aggregate(avg=Avg("grade"))
        .get("avg")
    )


def calculate_average_for_quarter(*, quarter: Quarter, assignment: ClassTeacherAssignment, students: Iterable[Student]):
    student_ids = [s.id for s in students]
    return (
        Grade.objects.filter(
            assignment=assignment,
            student_id__in=student_ids,
            quarter=quarter,
            grade__isnull=False,
        )
        .aggregate(avg=Avg("grade"))
        .get("avg")
    )


@transaction.atomic
def create_subgroups(*, assignment: ClassTeacherAssignment, students: Iterable[Student]):
    from .models import AssignmentStudent

    AssignmentStudent.objects.filter(assignment=assignment).delete()
    links = [
        AssignmentStudent(
            assignment=assignment,
            student=s,
            school_class=assignment.school_class,
            subject=assignment.subject,
            study_level=assignment.study_level,
        )
        for s in students
    ]
    AssignmentStudent.objects.bulk_create(links)


def log_action(*, actor, action: AuditAction, instance, message: str = "") -> None:
    AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        model=instance.__class__.__name__,
        object_id=str(getattr(instance, "pk", "")),
        message=message,
    )
