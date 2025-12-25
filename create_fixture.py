import os
import sys
import django

sys.path.insert(0, '/home/engine/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    User, UserRole, School, Teacher, Subject, Class, Subgroup,
    Student, StudentSubgroupAssignment, TeacherAssignment
)


def create_fixture_data():
    # Create users
    dept_user = User.objects.create_user(
        username='dept_admin',
        password='admin123',
        role=UserRole.DEPT_EDUCATION
    )
    
    school_admin = User.objects.create_user(
        username='school_admin',
        password='admin123',
        role=UserRole.ADMIN_SCHOOL
    )
    
    # Create school
    school = School.objects.create(
        name='Школа №1',
        director='Петров И.И.',
        graduating_class=11,
        location='ул. Ленина',
        created_by=dept_user
    )
    
    # Create subjects
    math_subject = Subject.objects.create(name='Математика')
    russian_subject = Subject.objects.create(name='Русский язык')
    english_subject = Subject.objects.create(name='Английский язык')
    
    # Create class
    class_5a = Class.objects.create(name='5А', school=school)
    
    # Create teachers
    teacher_petrov = Teacher.objects.create(full_name='Петров', school=school)
    teacher_ivanov = Teacher.objects.create(full_name='Иванов', school=school)
    teacher_sidorov = Teacher.objects.create(full_name='Сидоров', school=school)
    teacher_kuznetsov = Teacher.objects.create(full_name='Кузнецов', school=school)
    
    # Create subgroups
    math_subgroup_1 = Subgroup.objects.create(
        name='Подгруппа 1',
        class_obj=class_5a,
        subject=math_subject
    )
    math_subgroup_2 = Subgroup.objects.create(
        name='Подгруппа 2',
        class_obj=class_5a,
        subject=math_subject
    )
    english_subgroup_1 = Subgroup.objects.create(
        name='Подгруппа 1',
        class_obj=class_5a,
        subject=english_subject
    )
    english_subgroup_2 = Subgroup.objects.create(
        name='Подгруппа 2',
        class_obj=class_5a,
        subject=english_subject
    )
    
    # Create students
    student_ivan = Student.objects.create(full_name='Иван', class_obj=class_5a)
    student_maria = Student.objects.create(full_name='Мария', class_obj=class_5a)
    student_petr = Student.objects.create(full_name='Петр', class_obj=class_5a)
    student_anna = Student.objects.create(full_name='Анна', class_obj=class_5a)
    student_boris = Student.objects.create(full_name='Борис', class_obj=class_5a)
    student_anya = Student.objects.create(full_name='Аня', class_obj=class_5a)
    student_dasha = Student.objects.create(full_name='Даша', class_obj=class_5a)
    student_roma = Student.objects.create(full_name='Рома', class_obj=class_5a)
    student_sasha = Student.objects.create(full_name='Саша', class_obj=class_5a)
    student_vova = Student.objects.create(full_name='Вова', class_obj=class_5a)
    
    # Create teacher assignments
    TeacherAssignment.objects.create(teacher=teacher_petrov, subgroup=math_subgroup_1)
    TeacherAssignment.objects.create(teacher=teacher_ivanov, subgroup=math_subgroup_2)
    TeacherAssignment.objects.create(teacher=teacher_sidorov, subgroup=english_subgroup_1)
    TeacherAssignment.objects.create(teacher=teacher_kuznetsov, subgroup=english_subgroup_2)
    
    # Create student subgroup assignments - Math Subgroup 1
    StudentSubgroupAssignment.objects.create(student=student_ivan, subgroup=math_subgroup_1)
    StudentSubgroupAssignment.objects.create(student=student_maria, subgroup=math_subgroup_1)
    StudentSubgroupAssignment.objects.create(student=student_petr, subgroup=math_subgroup_1)
    
    # Create student subgroup assignments - Math Subgroup 2
    StudentSubgroupAssignment.objects.create(student=student_anna, subgroup=math_subgroup_2)
    StudentSubgroupAssignment.objects.create(student=student_boris, subgroup=math_subgroup_2)
    
    # Create student subgroup assignments - English Subgroup 1
    StudentSubgroupAssignment.objects.create(student=student_anya, subgroup=english_subgroup_1)
    StudentSubgroupAssignment.objects.create(student=student_dasha, subgroup=english_subgroup_1)
    StudentSubgroupAssignment.objects.create(student=student_roma, subgroup=english_subgroup_1)
    
    # Create student subgroup assignments - English Subgroup 2
    StudentSubgroupAssignment.objects.create(student=student_sasha, subgroup=english_subgroup_2)
    StudentSubgroupAssignment.objects.create(student=student_vova, subgroup=english_subgroup_2)
    
    print("Test data created successfully!")
    print(f"Users: {User.objects.count()}")
    print(f"Schools: {School.objects.count()}")
    print(f"Subjects: {Subject.objects.count()}")
    print(f"Classes: {Class.objects.count()}")
    print(f"Teachers: {Teacher.objects.count()}")
    print(f"Subgroups: {Subgroup.objects.count()}")
    print(f"Students: {Student.objects.count()}")
    print(f"Teacher Assignments: {TeacherAssignment.objects.count()}")
    print(f"Student Subgroup Assignments: {StudentSubgroupAssignment.objects.count()}")


if __name__ == '__main__':
    create_fixture_data()
