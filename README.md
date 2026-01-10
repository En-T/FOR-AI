# School Management System

Система управления школой на базе Django 4.x

## Описание проекта

Данное приложение представляет собой систему управления образовательным учреждением, которая позволяет:

- Управлять школами, классами, учениками и учителями
- Назначать учителей на предметы и классы
- Создавать подгруппы для обучения
- Вести учет оценок по четвертям
- Логировать все действия пользователей
- Управлять правами доступа на основе ролей

## Технологический стек

- Django 4.2.16
- Python 3.9+
- SQLite (База данных по умолчанию)

## Структура проекта

```
school_management/
├── core/                   # Приложение для аутентификации и базовых моделей
│   ├── models.py          # Модели User и AuditLog
│   ├── admin.py          # Админ-панель
│   ├── mixins.py         # Миксины для проверки прав доступа
│   └── utils.py          # Функции для логирования
├── main/                  # Основное приложение для управления школой
│   ├── models.py         # Модели: School, Subject, Class, Student, Teacher и др.
│   ├── admin.py          # Админ-панель
│   └── management/       # Management команды
│       └── commands/
│           └── init_data.py  # Команда для инициализации данных
├── school_management/     # Настройки проекта
│   ├── settings.py       # Основные настройки
│   ├── urls.py           # URL маршруты
│   └── wsgi.py           # WSGI конфигурация
├── static/               # Статические файлы
│   ├── css/
│   └── js/
├── templates/            # HTML шаблоны
├── logs/                 # Логи приложения
├── manage.py             # Скрипт управления Django
└── requirements.txt      # Зависимости проекта
```

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd school_management
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # Для Linux/Mac
# или
venv\Scripts\activate     # Для Windows
```

### 3. Установка зависимостей

```bash
pip install Django==4.2.16
```

### 4. Применение миграций

```bash
python manage.py migrate
```

### 5. Инициализация данных (опционально)

```bash
python manage.py init_data
```

Эта команда создаст:
- Суперпользователя с логином `admin` и паролем `admin123`
- Образцы предметов
- Школу
- Классы
- Учителей и учеников
- Назначения учителей

### 6. Запуск сервера разработки

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000/

## Модели базы данных

### core.User
Расширение стандартной модели Django User с дополнительными полями:
- `role` - роль пользователя (Superuser, Director of Education, School Administrator)
- `school` - привязка к школе (опционально)

### core.AuditLog
Модель для логирования всех действий в системе:
- `user` - пользователь, выполнивший действие
- `action` - тип действия (CREATE, UPDATE, DELETE, LOGIN, VIEW)
- `model` - название модели
- `object_id` - ID объекта
- `timestamp` - время действия
- `details` - дополнительные детали (JSON)

### main.School
Модель школы:
- `name` - название школы
- `director` - ФИО директора
- `final_grade` - выпускной класс (4, 9, 11)
- `location` - расположение
- `created_by` - пользователь, создавший школу
- `created_at` / `updated_at` - временные метки

### main.Subject
Модель предмета:
- `name` - название предмета
- `created_at` - дата создания

### main.Class
Модель класса:
- `name` - название класса (например: "5А", "5")
- `school` - школа (ForeignKey)
- `created_at` - дата создания

Уникальность: (school, name)

### main.Student
Модель ученика:
- `first_name` - имя
- `last_name` - фамилия
- `middle_name` - отчество
- `class_ref` - класс (ForeignKey)
- `created_at` - дата создания

### main.Teacher
Модель учителя:
- `first_name` - имя
- `last_name` - фамилия
- `middle_name` - отчество
- `school` - школа (ForeignKey)
- `created_at` - дата создания

### main.ClassTeacherAssignment
Модель назначения учителя на класс и предмет:
- `class_ref` - класс (ForeignKey)
- `teacher` - учитель (ForeignKey)
- `subject` - предмет (ForeignKey)
- `study_level` - уровень изучения (Базовый, Повышенный)
- `has_subgroups` - есть ли подгруппы
- `created_at` - дата создания

Уникальность: (class_ref, teacher, subject)

### main.Subgroup
Модель подгруппы:
- `assignment` - назначение учителя (ForeignKey)
- `order` - порядковый номер подгруппы
- `created_at` - дата создания

Название подгруппы формируется автоматически: f"{subject.name} - {teacher.full_name} - Подгруппа {N}"

### main.SubgroupStudent
Модель связи ученика с подгруппой:
- `subgroup` - подгруппа (ForeignKey)
- `student` - ученик (ForeignKey)

Уникальность: (subgroup, student)

### main.Grade
Модель оценки:
- `student` - ученик (ForeignKey)
- `assignment` - назначение учителя (ForeignKey)
- `quarter` - четверть (Первая, Вторая, Третья, Четвертая, Экзаменационная, Годовая, Итоговая)
- `grade` - оценка (от 1 до 10, опционально)
- `created_at` / `updated_at` - временные метки

Уникальность: (student, assignment, quarter)

## Система прав доступа

### Роли пользователей

1. **Superuser** - полный доступ ко всем функциям
2. **Director of Education** - управление школами и глобальными настройками
3. **School Administrator** - управление своей школой

### Миксины для проверки прав доступа

- `SuperuserRequiredMixin` - только для суперпользователя
- `DirectorEducationRequiredMixin` - для отдела образования и выше
- `SchoolAdminRequiredMixin` - для администраторов школ и выше

Пример использования:

```python
from core.mixins import SuperuserRequiredMixin
from django.views.generic import ListView

class MyView(SuperuserRequiredMixin, ListView):
    model = MyModel
    template_name = 'my_template.html'
```

## Логирование

Логирование настроено для записи в файл `logs/app.log`. Также все действия записываются в модель `AuditLog`.

### Использование функций логирования

```python
from core.utils import log_create, log_update, log_delete, log_view, log_login

# Логирование создания объекта
log_create(user, 'Student', student.id, {'name': student.full_name})

# Логирование обновления
log_update(user, 'Student', student.id, {'changed_field': 'new_value'})

# Логирование удаления
log_delete(user, 'Student', student.id, {'name': student.full_name})

# Логирование просмотра
log_view(user, 'Student', student.id)

# Логирование входа
log_login(user)
```

## Админ-панель

Админ-панель доступна по адресу: http://localhost:8000/admin/

Для входа используйте учетные данные суперпользователя или созданного через команду `init_data`.

## Создание суперпользователя вручную

```bash
python manage.py createsuperuser
```

## Управление миграциями

### Создание новых миграций

```bash
python manage.py makemigrations
```

### Применение миграций

```bash
python manage.py migrate
```

### Отмена последней миграции

```bash
python manage.py migrate <app_name> <previous_migration>
```

## Дополнительные команды

### Запуск интерактивной оболочки

```bash
python manage.py shell
```

### Проверка на проблемы

```bash
python manage.py check
```

## Настройка

### Изменение базы данных

По умолчанию используется SQLite. Для использования PostgreSQL или другой БД измените настройки в `school_management/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'school_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Настройка логирования

Настройки логирования находятся в `school_management/settings.py`. Вы можете изменить уровень логирования, формат сообщений и другие параметры.

## Лицензия

MIT License
