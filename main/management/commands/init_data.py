from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.utils import log_create
from main.models import School, Subject, Class, Student, Teacher, ClassTeacherAssignment, Grade

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize the database with initial data including a superuser and sample data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@school.local',
                password='admin123',
                first_name='Super',
                last_name='Admin',
                role=User.Role.SUPERUSER
            )
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {admin.username}'))
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write(self.style.WARNING('Superuser already exists'))

        # Create sample subjects
        subjects_data = [
            'Математика',
            'Русский язык',
            'Литература',
            'История',
            'География',
            'Физика',
            'Химия',
            'Биология',
            'Английский язык',
            'Информатика',
            'Физическая культура',
        ]
        subjects = []
        for subject_name in subjects_data:
            subject, created = Subject.objects.get_or_create(name=subject_name)
            if created:
                subjects.append(subject)
                self.stdout.write(f'Created subject: {subject.name}')

        # Create a sample school
        school, created = School.objects.get_or_create(
            name='Средняя школа №1',
            defaults={
                'director': 'Иванов Иван Иванович',
                'final_grade': School.FinalGrade.GRADE_11,
                'location': 'Москва',
                'created_by': admin,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created school: {school.name}'))
        else:
            self.stdout.write(self.style.WARNING('Sample school already exists'))

        # Create sample classes
        class_names = ['1А', '1Б', '5А', '5Б', '9А', '9Б', '11А', '11Б']
        classes = {}
        for class_name in class_names:
            cls, created = Class.objects.get_or_create(
                name=class_name,
                school=school
            )
            if created:
                classes[class_name] = cls
                self.stdout.write(f'Created class: {cls.name}')
            elif class_name not in classes:
                classes[class_name] = cls

        # Create sample teachers
        teachers_data = [
            {'first_name': 'Петр', 'last_name': 'Петров', 'middle_name': 'Петрович'},
            {'first_name': 'Мария', 'last_name': 'Сидорова', 'middle_name': 'Ивановна'},
            {'first_name': 'Алексей', 'last_name': 'Козлов', 'middle_name': 'Сергеевич'},
            {'first_name': 'Елена', 'last_name': 'Новикова', 'middle_name': 'Александровна'},
            {'first_name': 'Дмитрий', 'last_name': 'Морозов', 'middle_name': 'Владимирович'},
        ]
        teachers = []
        for teacher_data in teachers_data:
            teacher, created = Teacher.objects.get_or_create(
                school=school,
                **teacher_data
            )
            if created:
                teachers.append(teacher)
                self.stdout.write(f'Created teacher: {teacher.full_name}')

        # Create sample students
        students_data = [
            {'first_name': 'Анна', 'last_name': 'Смирнова', 'middle_name': 'Андреевна', 'class_name': '5А'},
            {'first_name': 'Михаил', 'last_name': 'Волков', 'middle_name': 'Сергеевич', 'class_name': '5А'},
            {'first_name': 'Екатерина', 'last_name': 'Кузнецова', 'middle_name': 'Дмитриевна', 'class_name': '5А'},
            {'first_name': 'Артем', 'last_name': 'Попов', 'middle_name': 'Николаевич', 'class_name': '5Б'},
            {'first_name': 'София', 'last_name': 'Васильева', 'middle_name': 'Михайловна', 'class_name': '5Б'},
        ]
        for student_data in students_data:
            class_name = student_data.pop('class_name')
            class_obj = classes.get(class_name)
            if class_obj:
                student, created = Student.objects.get_or_create(
                    class_ref=class_obj,
                    **student_data
                )
                if created:
                    self.stdout.write(f'Created student: {student.full_name}')

        # Create sample teacher assignments
        if teachers:
            math_subject = Subject.objects.get(name='Математика')
            class_5a = classes.get('5А')
            teacher = teachers[0]

            assignment, created = ClassTeacherAssignment.objects.get_or_create(
                class_ref=class_5a,
                teacher=teacher,
                subject=math_subject,
                defaults={
                    'study_level': ClassTeacherAssignment.StudyLevel.BASE,
                    'has_subgroups': False,
                }
            )
            if created:
                self.stdout.write(f'Created assignment: {assignment}')

        self.stdout.write(self.style.SUCCESS('Database initialization completed!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write(f'Username: admin')
        self.stdout.write(f'Password: admin123')
        self.stdout.write('\nRun the server with: python manage.py runserver')
