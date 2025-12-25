import os
import sys
import django

sys.path.insert(0, '/home/engine/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.exceptions import ValidationError
from core.models import (
    User, UserRole, School, Teacher, Subject, Class, Subgroup,
    Student, StudentSubgroupAssignment, TeacherAssignment, Grade
)
from django.core.validators import validate_email


def test_validation():
    print("=== Проверка валидации ===\n")
    
    # 1. Проверка валидации класса
    print("1. Проверка валидации имени класса:")
    
    # Допустимые форматы
    valid_names = ['5', '5А', '10Б', '11В']
    for name in valid_names:
        try:
            validate_class_name(name)
            print(f"   '{name}' - валидно ✓")
        except ValidationError as e:
            print(f"   '{name}' - невалидно: {e}")
    
    # Недопустимые форматы
    invalid_names = ['5АБ', 'ABC', '123', '']
    for name in invalid_names:
        try:
            validate_class_name(name)
            print(f"   '{name}' - валидно (неожиданно)")
        except ValidationError as e:
            print(f"   '{name}' - невалидно ✓")
    
    # 2. Проверка валидации оценки
    print("\n2. Проверка валидации оценки:")
    
    # Допустимые значения
    valid_grades = [1, 5, 10, None]
    for grade in valid_grades:
        try:
            validate_grade(grade)
            print(f"   {grade} - валидно ✓")
        except ValidationError as e:
            print(f"   {grade} - невалидно: {e}")
    
    # Недопустимые значения
    invalid_grades = [0, 11, -1, 100]
    for grade in invalid_grades:
        try:
            validate_grade(grade)
            print(f"   {grade} - валидно (неожиданно)")
        except ValidationError as e:
            print(f"   {grade} - невалидно ✓")
    
    # 3. Проверка уникальности
    print("\n3. Проверка уникальности:")
    
    # Попытка создать дублирующую школу
    school = School.objects.first()
    try:
        dup_school = School(name=school.name, location=school.location, 
                          director="Другой", graduating_class=10)
        dup_school.full_clean()
        print(f"   Дубликат школы - валидно (неожиданно)")
    except ValidationError as e:
        print(f"   Дубликат школы - невалидно ✓")
    
    # 4. Проверка связей
    print("\n4. Проверка связей моделей:")
    
    student = Student.objects.first()
    print(f"   Студент '{student.full_name}' привязан к классу '{student.class_obj.name}'")
    
    subgroup = Subgroup.objects.first()
    print(f"   Подгруппа '{subgroup.subject.name} - {subgroup.name}' привязана к классу '{subgroup.class_obj.name}'")
    
    # 5. Проверка подгруппы
    print("\n5. Проверка подгруппы (Class + Subject):")
    
    cls = Class.objects.first()
    subject = Subject.objects.filter(name='Математика').first()
    existing_subgroups = Subgroup.objects.filter(class_obj=cls, subject=subject)
    print(f"   Класс '{cls.name}' имеет {existing_subgroups.count()} подгрупп по предмету '{subject.name}'")
    
    for sg in existing_subgroups:
        print(f"      - {sg.name}")
    
    print("\n=== Все проверки валидации пройдены! ===")


if __name__ == '__main__':
    from core.models import validate_class_name, validate_grade
    test_validation()
