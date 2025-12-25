import os
import sys
import json
import django

sys.path.insert(0, '/home/engine/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core import serializers
from core.models import (
    User, School, Teacher, Subject, Class, Subgroup,
    Student, StudentSubgroupAssignment, TeacherAssignment
)


def create_json_fixture():
    fixture_data = []
    
    # Export in order: User, School, Subject, Class, Teacher, Subgroup, Student, TeacherAssignment, StudentSubgroupAssignment
    for model in [User, School, Subject, Class, Teacher, Subgroup, Student, TeacherAssignment, StudentSubgroupAssignment]:
        for obj in model.objects.all():
            fixture_data.append(obj)
    
    with open('/home/engine/project/fixtures/test_data.json', 'w', encoding='utf-8') as f:
        f.write(serializers.serialize('json', fixture_data, ensure_ascii=False))
    
    print("JSON fixture created successfully at /home/engine/project/fixtures/test_data.json")


if __name__ == '__main__':
    create_json_fixture()
