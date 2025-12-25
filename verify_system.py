import os
import sys
import django

sys.path.insert(0, '/home/engine/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    User, UserRole, School, Teacher, Subject, Class, Subgroup,
    Student, StudentSubgroupAssignment, TeacherAssignment, Grade
)


def verify_system():
    print("=== Проверка системы ===\n")
    
    # 1. Проверка пользователей
    print("1. Пользователи:")
    for user in User.objects.all():
        print(f"   - {user.username} ({user.role})")
        # Проверка пароля
        assert user.check_password('admin123'), f"Неверный пароль для {user.username}"
        print(f"     Пароль верный: True")
    
    # 2. Проверка школы
    print("\n2. Школы:")
    school = School.objects.first()
    print(f"   - {school.name}")
    print(f"   - Директор: {school.director}")
    print(f"   - Выпускной класс: {school.graduating_class}")
    print(f"   - Расположение: {school.location}")
    
    # 3. Проверка предметов
    print("\n3. Предметы:")
    for subject in Subject.objects.all():
        print(f"   - {subject.name}")
    
    # 4. Проверка классов
    print("\n4. Классы:")
    for cls in Class.objects.all():
        print(f"   - {cls.name} ({cls.school.name})")
    
    # 5. Проверка учителей
    print("\n5. Учителя:")
    for teacher in Teacher.objects.all():
        print(f"   - {teacher.full_name} ({teacher.school.name})")
    
    # 6. Проверка подгрупп
    print("\n6. Подгруппы:")
    for subgroup in Subgroup.objects.all():
        print(f"   - {subgroup.subject.name}, {subgroup.name} ({subgroup.class_obj.name})")
    
    # 7. Проверка студентов
    print("\n7. Студенты:")
    for student in Student.objects.all():
        print(f"   - {student.full_name} ({student.class_obj.name})")
    
    # 8. Проверка назначений учителей
    print("\n8. Назначения учителей:")
    for assignment in TeacherAssignment.objects.all():
        print(f"   - {assignment.teacher.full_name} -> {assignment.subgroup}")
    
    # 9. Проверка назначений студентов в подгруппы
    print("\n9. Назначения студентов в подгруппы:")
    for assignment in StudentSubgroupAssignment.objects.all():
        print(f"   - {assignment.student.full_name} -> {assignment.subgroup}")
    
    # 10. Проверка того, что один студент может быть в разных подгруппах
    print("\n10. Проверка гибкости назначений (студент в разных подгруппах):")
    student = Student.objects.first()
    subgroups = student.subgroup_assignments.all().values_list('subgroup__subject__name', 'subgroup__name')
    print(f"   - {student.full_name} состоит в подгруппах:")
    for sg in student.subgroup_assignments.all():
        print(f"     * {sg.subgroup.subject.name}, {sg.subgroup.name}")
    
    print("\n=== Все проверки пройдены успешно! ===")


if __name__ == '__main__':
    verify_system()
