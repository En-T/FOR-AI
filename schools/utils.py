import logging
from django.db.models import Avg, Count, Q
from django.utils.translation import gettext_lazy as _
from .models import Grade, ClassGroup, School, Student, AuditLog, User, Subject, Teacher

logger = logging.getLogger('schools')

def log_action(user, action, model_name, object_id=None, details=None, ip_address=None):
    """Универсальная функция логирования действий"""
    try:
        AuditLog.objects.create(
            actor=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else '',
            details=details or '',
            ip_address=ip_address
        )
        logger.info(f"Action logged: {user} {action} {model_name} {object_id}")
    except Exception as e:
        logger.error(f"Failed to log action: {e}")

def get_user_school(user):
    """Получить школу пользователя (для school_admin)"""
    try:
        if user.role == 'school_admin':
            return user.school
        return None
    except AttributeError:
        return None

def get_student_average_by_quarter(student, quarter):
    """Получить средний балл учащегося за четверть"""
    if quarter not in ['q1', 'q2', 'q3', 'q4', 'exam', 'year', 'final']:
        raise ValueError("Invalid quarter")
    
    average = Grade.objects.filter(
        student=student,
        quarter=quarter,
        grade__isnull=False
    ).aggregate(avg=Avg('grade'))['avg']
    
    return round(average, 2) if average else None

def get_class_average(class_obj):
    """Получить средний балл класса (по четвертям)"""
    students = class_obj.students.all()
    if not students:
        return 0
    
    average = Grade.objects.filter(
        student__in=students,
        quarter__in=['q1', 'q2', 'q3', 'q4'],
        grade__isnull=False
    ).aggregate(avg=Avg('grade'))['avg']
    
    return round(average, 2) if average else 0

def get_school_average(school):
    """Получить средний балл школы"""
    students = Student.objects.filter(class_group__school=school)
    if not students:
        return 0
    
    average = Grade.objects.filter(
        student__in=students,
        quarter__in=['q1', 'q2', 'q3', 'q4'],
        grade__isnull=False
    ).aggregate(avg=Avg('grade'))['avg']
    
    return round(average, 2) if average else 0

def calculate_statistics(school):
    """Расчет всей статистики по школе"""
    classes = school.classes.all()
    students = Student.objects.filter(class_group__school=school)
    teachers = school.teachers.all()
    
    class_count = classes.count()
    student_count = students.count()
    teacher_count = teachers.count()
    
    average_grade = Grade.objects.filter(
        student__in=students,
        quarter__in=['q1', 'q2', 'q3', 'q4'],
        grade__isnull=False
    ).aggregate(avg=Avg('grade'))['avg']
    
    class_stats = []
    for class_obj in classes:
        class_students = class_obj.students.count()
        if class_students > 0:
            class_avg = get_class_average(class_obj)
            class_stats.append({
                'class': class_obj,
                'student_count': class_students,
                'average_grade': class_avg
            })
    
    return {
        'class_count': class_count,
        'student_count': student_count,
        'teacher_count': teacher_count,
        'average_grade': round(average_grade, 2) if average_grade else 0,
        'class_statistics': class_stats
    }

def get_class_subject_groups(class_obj):
    """Получить все назначения предметов для класса с информацией о подгруппах"""
    from .models import ClassSubjectGroup
    
    subject_assignments = {}
    assignments = ClassSubjectGroup.objects.filter(class_group=class_obj).select_related('subject', 'teacher')
    
    for assignment in assignments:
        subject_id = assignment.subject_id
        if subject_id not in subject_assignments:
            subject_assignments[subject_id] = {
                'subject': assignment.subject,
                'groups': []
            }
        
        subject_assignments[subject_id]['groups'].append({
            'teacher': assignment.teacher,
            'group_number': assignment.group_number,
            'level': assignment.level,
            'assignment_id': assignment.id
        })
    
    return subject_assignments

def get_teacher_assignments(teacher):
    """Получить все назначения учителя с детализацией по классам"""
    from .models import ClassSubjectGroup
    
    assignments = ClassSubjectGroup.objects.filter(teacher=teacher).select_related('class_group', 'subject')
    
    result = {}
    for assignment in assignments:
        class_id = assignment.class_group_id
        if class_id not in result:
            result[class_id] = {
                'class': assignment.class_group,
                'subjects': []
            }
        
        result[class_id]['subjects'].append({
            'subject': assignment.subject,
            'level': assignment.level,
            'group_number': assignment.group_number,
            'assignment_id': assignment.id
        })
    
    return result

def calculate_student_averages(student):
    """Пересчитать все средние баллы учащегося"""
    quarters = ['q1', 'q2', 'q3', 'q4', 'exam', 'year', 'final']
    
    results = {}
    for quarter in quarters:
        results[quarter] = get_student_average_by_quarter(student, quarter)
    
    return results

def get_system_statistics():
    """Получить глобальную статистику системы (для суперпользователя)"""
    from .models import School
    
    school_count = School.objects.count()
    user_count = User.objects.filter(is_superuser=False).count()
    
    students = Student.objects.all()
    student_count = students.count()
    
    teachers_count = Teacher.objects.count()
    subjects_count = Subject.objects.count()
    
    average_grade = Grade.objects.filter(
        quarter__in=['q1', 'q2', 'q3', 'q4'],
        grade__isnull=False
    ).aggregate(avg=Avg('grade'))['avg']
    
    return {
        'school_count': school_count,
        'user_count': user_count,
        'student_count': student_count,
        'teacher_count': teachers_count,
        'subject_count': subjects_count,
        'average_grade': round(average_grade, 2) if average_grade else 0
    }

def parse_log_file(limit=100, search_term=None):
    """Парсинг лог-файла для отображения в веб-интерфейсе"""
    import os
    from datetime import datetime
    
    log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')
    
    if not os.path.exists(log_file_path):
        return []
    
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        logs = []
        for line in lines[-limit:]:
            if search_term and search_term.lower() not in line.lower():
                continue
            
            try:
                parts = line.strip().split(' ', 3)
                if len(parts) >= 4:
                    logs.append({
                        'level': parts[0],
                        'timestamp': parts[1] + ' ' + parts[2],
                        'message': parts[3]
                    })
            except (IndexError, ValueError):
                continue
        
        return list(reversed(logs))
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        return []