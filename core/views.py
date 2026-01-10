from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction

from .models import (
    User, School, Subject, Teacher, Class, Subgroup,
    Student, StudentSubgroupAssignment, TeacherAssignment, Grade
)


def check_role(request, allowed_roles):
    """Check if user has required role"""
    user = request.user
    if not user.is_authenticated:
        return None, None
    return user, user.role in allowed_roles


# Dashboard View
@login_required
def dashboard_view(request):
    user = request.user
    if user.role == User.ROLE_SUPERUSER:
        return redirect('superuser-dashboard')
    elif user.role == User.ROLE_DEPT_EDUCATION:
        return redirect('director-dashboard')
    
    context = {'role': user.role}

    if user.role == User.ROLE_ADMIN_SCHOOL:
        # Get user's school (assuming user has a school assigned)
        # For demo, we'll get the first school or None
        try:
            school = School.objects.filter(classes__isnull=False).distinct().first()
            if not school:
                school = School.objects.first()
            context['school'] = school

            if school:
                context['stats'] = {
                    'students': Student.objects.filter(school_class__school=school).count(),
                    'classes': Class.objects.filter(school=school).count(),
                    'teachers': Teacher.objects.filter(school=school).count(),
                }
            else:
                context['stats'] = {'students': 0, 'classes': 0, 'teachers': 0}
        except Exception:
            context['stats'] = {'students': 0, 'classes': 0, 'teachers': 0}
            context['school'] = None

    elif user.role == User.ROLE_DEPT_EDUCATION:
        context['schools'] = School.objects.all()

    return render(request, 'dashboard.html', context)


# School Views (DEPT_EDUCATION)
@login_required
def school_list(request):
    user = request.user
    if user.role != User.ROLE_DEPT_EDUCATION:
        return HttpResponseForbidden('Access denied')

    schools = School.objects.all()
    return render(request, 'schools/list.html', {'schools': schools})


@login_required
def school_create(request):
    user = request.user
    if user.role != User.ROLE_DEPT_EDUCATION:
        return HttpResponseForbidden('Access denied')

    if request.method == 'POST':
        name = request.POST.get('name')
        director = request.POST.get('director')
        graduating_class = request.POST.get('graduating_class')
        location = request.POST.get('location')

        if name and director and graduating_class and location:
            school = School.objects.create(
                name=name,
                director=director,
                graduating_class=int(graduating_class),
                location=location,
                created_by=user
            )
            messages.success(request, 'School created successfully')
            return redirect('school_list')

    return render(request, 'schools/form.html', {})


@login_required
def school_update(request, pk):
    user = request.user
    if user.role != User.ROLE_DEPT_EDUCATION:
        return HttpResponseForbidden('Access denied')

    school = get_object_or_404(School, pk=pk)

    if request.method == 'POST':
        school.name = request.POST.get('name', school.name)
        school.director = request.POST.get('director', school.director)
        school.graduating_class = int(request.POST.get('graduating_class', school.graduating_class))
        school.location = request.POST.get('location', school.location)
        school.save()
        messages.success(request, 'School updated successfully')
        return redirect('school_list')

    return render(request, 'schools/form.html', {'school': school, 'form': {
        'name': {'value': school.name},
        'director': {'value': school.director},
        'graduating_class': {'value': school.graduating_class},
        'location': {'value': school.location},
    }})


@login_required
def school_delete(request, pk):
    user = request.user
    if user.role != User.ROLE_DEPT_EDUCATION:
        return HttpResponseForbidden('Access denied')

    school = get_object_or_404(School, pk=pk)

    if request.method == 'POST':
        school.delete()
        messages.success(request, 'School deleted successfully')
        return redirect('school_list')

    return render(request, 'schools/confirm_delete.html', {'school': school})


# Class Views (ADMIN_SCHOOL)
@login_required
def class_list(request):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()  # Get first school for demo
    if school:
        classes = Class.objects.filter(school=school)
    else:
        classes = []

    return render(request, 'classes/list.html', {'classes': classes})


@login_required
def class_create(request):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()

    if request.method == 'POST':
        name = request.POST.get('name')

        if name and school:
            try:
                class_obj = Class.objects.create(name=name, school=school)
                messages.success(request, 'Class created successfully')
                return redirect('class_list')
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Please provide class name and ensure school exists')

    return render(request, 'classes/form.html', {'form': {}})


@login_required
def class_update(request, pk):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    class_obj = get_object_or_404(Class, pk=pk)

    if request.method == 'POST':
        class_obj.name = request.POST.get('name', class_obj.name)
        try:
            class_obj.save()
            messages.success(request, 'Class updated successfully')
            return redirect('class_list')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'classes/form.html', {'class': class_obj, 'form': {
        'name': {'value': class_obj.name},
    }})


@login_required
def class_delete(request, pk):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    class_obj = get_object_or_404(Class, pk=pk)

    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, 'Class deleted successfully')
        return redirect('class_list')

    return render(request, 'classes/confirm_delete.html', {'class': class_obj})


# Student Views (ADMIN_SCHOOL)
@login_required
def student_list(request):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    class_id = request.GET.get('class_id')

    if school:
        classes = Class.objects.filter(school=school)
        if class_id:
            students = Student.objects.filter(school_class_id=class_id, school_class__school=school)
        else:
            students = Student.objects.filter(school_class__school=school)
    else:
        classes = []
        students = []

    return render(request, 'students/list.html', {
        'students': students,
        'classes': classes,
        'selected_class_id': class_id
    })


@login_required
def student_create(request):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    classes = Class.objects.filter(school=school) if school else []

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        school_class_id = request.POST.get('school_class')

        if full_name and school_class_id:
            try:
                Student.objects.create(
                    full_name=full_name,
                    school_class_id=int(school_class_id)
                )
                messages.success(request, 'Student created successfully')
                return redirect('student_list')
            except Exception as e:
                messages.error(request, str(e))

    return render(request, 'students/form.html', {'classes': classes, 'form': {
        'full_name': {'value': request.POST.get('full_name', '')},
        'school_class': {'value': request.POST.get('school_class', '')},
    }})


@login_required
def student_update(request, pk):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    classes = Class.objects.filter(school=school) if school else []
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.full_name = request.POST.get('full_name', student.full_name)
        student.school_class_id = int(request.POST.get('school_class', student.school_class_id))
        try:
            student.save()
            messages.success(request, 'Student updated successfully')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'students/form.html', {
        'student': student,
        'classes': classes,
        'form': {
            'full_name': {'value': student.full_name},
            'school_class': {'value': student.school_class_id},
        }
    })


@login_required
def student_delete(request, pk):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully')
        return redirect('student_list')

    return render(request, 'students/confirm_delete.html', {'student': student})


@login_required
def student_bulk_upload(request):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    classes = Class.objects.filter(school=school) if school else []

    if request.method == 'POST':
        school_class_id = request.POST.get('school_class')
        students_text = request.POST.get('students')

        if school_class_id and students_text:
            student_names = [line.strip() for line in students_text.split('\n') if line.strip()]
            created_count = 0

            with transaction.atomic():
                for name in student_names:
                    try:
                        Student.objects.create(
                            full_name=name,
                            school_class_id=int(school_class_id)
                        )
                        created_count += 1
                    except Exception:
                        pass

            messages.success(request, f'{created_count} student(s) added successfully')
            return redirect('student_list')

    return render(request, 'students/bulk_upload.html', {'classes': classes})


# Teacher Views (ADMIN_SCHOOL)
@login_required
def teacher_list(request):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    teachers = Teacher.objects.filter(school=school) if school else []

    return render(request, 'teachers/list.html', {'teachers': teachers})


@login_required
def teacher_create(request):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()

    if request.method == 'POST':
        full_name = request.POST.get('full_name')

        if full_name and school:
            try:
                Teacher.objects.create(full_name=full_name, school=school)
                messages.success(request, 'Teacher created successfully')
                return redirect('teacher_list')
            except Exception as e:
                messages.error(request, str(e))

    return render(request, 'teachers/form.html', {'form': {}})


@login_required
def teacher_update(request, pk):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        teacher.full_name = request.POST.get('full_name', teacher.full_name)
        try:
            teacher.save()
            messages.success(request, 'Teacher updated successfully')
            return redirect('teacher_list')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'teachers/form.html', {'teacher': teacher, 'form': {
        'full_name': {'value': teacher.full_name},
    }})


@login_required
def teacher_delete(request, pk):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully')
        return redirect('teacher_list')

    return render(request, 'teachers/confirm_delete.html', {'teacher': teacher})


# Subgroup Assignment Views (ADMIN_SCHOOL)
@login_required
def subgroup_assignments(request, class_id):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    classes = Class.objects.filter(school=school) if school else []

    selected_class = None
    subgroups = []
    teachers = []

    if class_id:
        selected_class = get_object_or_404(Class, pk=class_id)
        subgroups = Subgroup.objects.filter(school_class=selected_class)
        teachers = Teacher.objects.filter(school=school)

    return render(request, 'subgroups/assignments.html', {
        'classes': classes,
        'selected_class': selected_class,
        'subgroups': subgroups,
        'teachers': teachers,
    })


@login_required
def assign_teacher(request, subgroup_id):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    subgroup = get_object_or_404(Subgroup, pk=subgroup_id)

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        if teacher_id:
            teacher = get_object_or_404(Teacher, pk=teacher_id)

            # Validate teacher belongs to same school
            if teacher.school != subgroup.school_class.school:
                messages.error(request, 'Teacher must belong to the same school')
                return redirect('subgroup_assignments', class_id=subgroup.school_class.id)

            # Remove existing assignment if any
            TeacherAssignment.objects.filter(subgroup=subgroup).delete()

            # Create new assignment
            TeacherAssignment.objects.create(teacher=teacher, subgroup=subgroup)
            messages.success(request, 'Teacher assigned successfully')

    return redirect('subgroup_assignments', class_id=subgroup.school_class.id)


@login_required
def assign_students_to_subgroups(request, class_id):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    classes = Class.objects.filter(school=school) if school else []

    selected_class = None
    students = []
    subgroups = []

    if class_id:
        selected_class = get_object_or_404(Class, pk=class_id)
        students = Student.objects.filter(school_class=selected_class)
        subgroups = Subgroup.objects.filter(school_class=selected_class)

        # Add student_ids to subgroups for template display
        for subgroup in subgroups:
            assignments = StudentSubgroupAssignment.objects.filter(subgroup=subgroup)
            subgroup.student_ids = [a.student_id for a in assignments]

    if request.method == 'POST':
        subgroup_students = request.POST.getlist('subgroups')

        with transaction.atomic():
            # Clear all existing assignments for this class
            StudentSubgroupAssignment.objects.filter(
                subgroup__school_class_id=class_id
            ).delete()

            # Create new assignments
            for item in subgroup_students:
                parts = item.split('_')
                if len(parts) == 2:
                    subgroup_id = int(parts[0])
                    student_id = int(parts[1])

                    subgroup = get_object_or_404(Subgroup, pk=subgroup_id)
                    student = get_object_or_404(Student, pk=student_id)

                    # Check if assignment already exists
                    if not StudentSubgroupAssignment.objects.filter(
                        student=student, subgroup=subgroup
                    ).exists():
                        StudentSubgroupAssignment.objects.create(
                            student=student, subgroup=subgroup
                        )

        messages.success(request, 'Student distribution saved')
        return redirect('assign_students_to_subgroups', class_id=class_id)

    return render(request, 'subgroups/students.html', {
        'classes': classes,
        'selected_class': selected_class,
        'students': students,
        'subgroups': subgroups,
    })


# Grade Views (ADMIN_SCHOOL)
@login_required
def grade_input(request, class_id):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    classes = Class.objects.filter(school=school) if school else []

    quarter = request.GET.get('quarter', 'q1')
    selected_class = None
    students = []
    subjects = []
    grades = {}

    if class_id:
        selected_class = get_object_or_404(Class, pk=class_id)
        students = Student.objects.filter(school_class=selected_class)
        subjects = Subject.objects.all()

        # Load existing grades
        existing_grades = Grade.objects.filter(
            student__school_class=selected_class,
            quarter=quarter
        )

        for grade in existing_grades:
            key = f"{grade.student_id}_{grade.subject_id}"
            grades[key] = grade.grade

    if request.method == 'POST':
        quarter = request.POST.get('quarter', quarter)

        with transaction.atomic():
            for student in students:
                for subject in subjects:
                    grade_value = request.POST.get(f'grade_{student.id}_{subject.id}')
                    if grade_value:
                        grade, created = Grade.objects.update_or_create(
                            student=student,
                            subject=subject,
                            quarter=quarter,
                            defaults={
                                'grade': int(grade_value),
                                'assigned_by': user
                            }
                        )

        messages.success(request, 'Grades saved successfully')
        return redirect('grade_input', class_id=class_id)

    return render(request, 'grades/form.html', {
        'classes': classes,
        'selected_class': selected_class,
        'students': students,
        'subjects': subjects,
        'grades': grades,
        'quarter': quarter,
    })


# Report Views (ADMIN_SCHOOL)
@login_required
def student_grades(request, student_id):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return HttpResponseForbidden('Access denied')

    school = School.objects.first()
    students = Student.objects.filter(school_class__school=school) if school else []
    selected_student = get_object_or_404(Student, pk=student_id)

    grades_data = []
    existing_grades = Grade.objects.filter(student=selected_student).select_related('subject')

    for grade in existing_grades:
        # Find or create row for this subject
        row = next((r for r in grades_data if r['subject'].id == grade.subject_id), None)
        if not row:
            row = {
                'subject': grade.subject,
                'q1': None, 'q2': None, 'q3': None, 'q4': None,
                'exam': None, 'annual': None, 'final': None
            }
            grades_data.append(row)

        setattr(row, grade.quarter, grade.grade)

    return render(request, 'reports/student_grades.html', {
        'students': students,
        'selected_student': selected_student,
        'grades_data': grades_data,
    })


# API Views
@login_required
@require_POST
def grade_save(request):
    user = request.user
    if user.role != User.ROLE_ADMIN_SCHOOL:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    data = request.POST
    student_id = data.get('student_id')
    subject_id = data.get('subject_id')
    quarter = data.get('quarter')
    grade_value = data.get('grade')

    try:
        student = Student.objects.get(pk=student_id)
        subject = Subject.objects.get(pk=subject_id)

        if grade_value:
            grade, created = Grade.objects.update_or_create(
                student=student,
                subject=subject,
                quarter=quarter,
                defaults={
                    'grade': int(grade_value),
                    'assigned_by': user
                }
            )
            return JsonResponse({'success': True, 'grade': grade.grade})
        else:
            Grade.objects.filter(
                student=student,
                subject=subject,
                quarter=quarter
            ).delete()
            return JsonResponse({'success': True, 'grade': None})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
