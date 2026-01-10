# Инструкции по загрузке проекта на GitHub

## Шаг 1: Создание репозитория на GitHub

1. Перейти на https://github.com/new
2. Ввести название репозитория: school_management
3. Добавить описание: "Web application for school management with Django"
4. Выбрать Public или Private (на ваш выбор)
5. Нажать "Create repository"
6. Скопировать URL репозитория

## Шаг 2: Инициализация Git локально

```bash
# Перейти в папку проекта
cd school_management

# Инициализировать Git репозиторий (если еще не инициализирован)
git init

# Добавить все файлы
git add .

# Сделать первый коммит
git commit -m "Initial commit: School management application with Django"
```

## Шаг 3: Добавление удаленного репозитория

```bash
# Заменить YOUR_USERNAME на ваше имя пользователя GitHub
# Заменить REPO_NAME на название репозитория

git remote add origin https://github.com/YOUR_USERNAME/school_management.git

# Или, если вы используете SSH:
# git remote add origin git@github.com:YOUR_USERNAME/school_management.git
```

## Шаг 4: Загрузка на GitHub

```bash
# Переименовать ветку на main (если необходимо)
git branch -M main

# Загрузить проект на GitHub
git push -u origin main
```

## Шаг 5: Проверка

После выполнения команд откройте в браузере:
https://github.com/YOUR_USERNAME/school_management
