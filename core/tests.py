from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import (
    User, UserRole, School, Teacher, Subject, Class, Subgroup,
    Student, StudentSubgroupAssignment, TeacherAssignment, Grade, Quarter
)


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role=UserRole.ADMIN_SCHOOL
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.role, UserRole.ADMIN_SCHOOL)
    
    def test_password_hashing(self):
        user = User(username='testuser', role=UserRole.DEPT_EDUCATION)
        user.set_password('mypassword')
        self.assertNotEqual(user.password, 'mypassword')
        self.assertTrue(user.check_password('mypassword'))


class SchoolModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dept_admin',
            password='admin123',
            role=UserRole.DEPT_EDUCATION
        )
    
    def test_create_school(self):
        school = School.objects.create(
            name='Тестовая школа',
            director='Директор',
            graduating_class=11,
            location='ул. Тестовая',
            created_by=self.user
        )
        self.assertEqual(school.name, 'Тестовая школа')
        self.assertEqual(school.graduating_class, 11)


class SubjectModelTest(TestCase):
    def test_create_subject(self):
        subject = Subject.objects.create(name='Тестовый предмет')
        self.assertEqual(subject.name, 'Тестовый предмет')
    
    def test_subject_unique(self):
        Subject.objects.create(name='Уникальный предмет')
        with self.assertRaises(ValidationError):
            subject = Subject(name='Уникальный предмет')
            subject.full_clean()


class ClassModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dept_admin',
            password='admin123',
            role=UserRole.DEPT_EDUCATION
        )
        self.school = School.objects.create(
            name='Тестовая школа',
            director='Директор',
            graduating_class=11,
            location='ул. Тестовая',
            created_by=self.user
        )
    
    def test_create_class(self):
        cls = Class.objects.create(name='5А', school=self.school)
        self.assertEqual(cls.name, '5А')
        self.assertEqual(cls.school, self.school)
    
    def test_class_name_validation(self):
        valid_names = ['5', '5А', '10Б', '11В']
        for name in valid_names:
            cls = Class(name=name, school=self.school)
            cls.full_clean()
        
        invalid_names = ['5АБ', 'ABC', '123']
        for name in invalid_names:
            cls = Class(name=name, school=self.school)
            with self.assertRaises(ValidationError):
                cls.full_clean()


class SubgroupModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dept_admin',
            password='admin123',
            role=UserRole.DEPT_EDUCATION
        )
        self.school = School.objects.create(
            name='Тестовая школа',
            director='Директор',
            graduating_class=11,
            location='ул. Тестовая',
            created_by=self.user
        )
        self.subject = Subject.objects.create(name='Математика')
        self.cls = Class.objects.create(name='5А', school=self.school)
    
    def test_create_subgroup(self):
        subgroup = Subgroup.objects.create(
            name='Подгруппа 1',
            class_obj=self.cls,
            subject=self.subject
        )
        self.assertEqual(subgroup.name, 'Подгруппа 1')
        self.assertEqual(subgroup.class_obj, self.cls)
        self.assertEqual(subgroup.subject, self.subject)


class StudentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dept_admin',
            password='admin123',
            role=UserRole.DEPT_EDUCATION
        )
        self.school = School.objects.create(
            name='Тестовая школа',
            director='Директор',
            graduating_class=11,
            location='ул. Тестовая',
            created_by=self.user
        )
        self.cls = Class.objects.create(name='5А', school=self.school)
    
    def test_create_student(self):
        student = Student.objects.create(full_name='Иванов Иван', class_obj=self.cls)
        self.assertEqual(student.full_name, 'Иванов Иван')
        self.assertEqual(student.class_obj, self.cls)


class StudentSubgroupAssignmentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dept_admin',
            password='admin123',
            role=UserRole.DEPT_EDUCATION
        )
        self.school = School.objects.create(
            name='Тестовая школа',
            director='Директор',
            graduating_class=11,
            location='ул. Тестовая',
            created_by=self.user
        )
        self.subject = Subject.objects.create(name='Математика')
        self.cls = Class.objects.create(name='5А', school=self.school)
        self.subgroup = Subgroup.objects.create(
            name='Подгруппа 1',
            class_obj=self.cls,
            subject=self.subject
        )
        self.student = Student.objects.create(full_name='Иванов Иван', class_obj=self.cls)
    
    def test_create_assignment(self):
        assignment = StudentSubgroupAssignment.objects.create(
            student=self.student,
            subgroup=self.subgroup
        )
        self.assertEqual(assignment.student, self.student)
        self.assertEqual(assignment.subgroup, self.subgroup)
    
    def test_student_in_multiple_subgroups(self):
        # Создаем вторую подгруппу по другому предмету
        english = Subject.objects.create(name='Английский язык')
        subgroup2 = Subgroup.objects.create(
            name='Подгруппа 1',
            class_obj=self.cls,
            subject=english
        )
        
        # Назначаем студента в обе подгруппы
        StudentSubgroupAssignment.objects.create(student=self.student, subgroup=self.subgroup)
        StudentSubgroupAssignment.objects.create(student=self.student, subgroup=subgroup2)
        
        # Проверяем, что студент состоит в двух подгруппах
        self.assertEqual(
            self.student.subgroup_assignments.count(),
            2
        )


class GradeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='school_admin',
            password='admin123',
            role=UserRole.ADMIN_SCHOOL
        )
        self.school = School.objects.create(
            name='Тестовая школа',
            director='Директор',
            graduating_class=11,
            location='ул. Тестовая',
            created_by=User.objects.create_user(
                username='dept_admin',
                password='admin123',
                role=UserRole.DEPT_EDUCATION
            )
        )
        self.subject = Subject.objects.create(name='Математика')
        self.cls = Class.objects.create(name='5А', school=self.school)
        self.student = Student.objects.create(full_name='Иванов Иван', class_obj=self.cls)
    
    def test_create_grade(self):
        grade = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            quarter=Quarter.Q1,
            grade=5,
            assigned_by=self.user
        )
        self.assertEqual(grade.grade, 5)
        self.assertEqual(grade.quarter, Quarter.Q1)
    
    def test_grade_validation(self):
        valid_grades = [1, 5, 10, None]
        for grade_value in valid_grades:
            grade = Grade(
                student=self.student,
                subject=self.subject,
                quarter=Quarter.Q1,
                grade=grade_value,
                assigned_by=self.user
            )
            grade.full_clean()
        
        invalid_grades = [0, 11, -1, 100]
        for grade_value in invalid_grades:
            grade = Grade(
                student=self.student,
                subject=self.subject,
                quarter=Quarter.Q1,
                grade=grade_value,
                assigned_by=self.user
            )
            with self.assertRaises(ValidationError):
                grade.full_clean()
