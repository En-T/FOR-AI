/**
 * Валидация форм на клиенте
 * Проверка обязательных полей, email, паролей и др.
 */

SchoolApp.components = SchoolApp.components || {};
SchoolApp.components.Forms = {
  validators: {},
  methods: {}
};

/**
 * Инициализация форм
 */
SchoolApp.components.Forms.init = function() {
  this.setupFormValidation();
  this.setupPasswordToggle();
  this.setupRealTimeValidation();
  this.setupConfirmSubmit();
  this.setupUnsavedChanges();
};

/**
 * Настройка валидации форм
 */
SchoolApp.components.Forms.setupFormValidation = function() {
  document.querySelectorAll('form').forEach(form => {
    // Проверка на наличие атрибута novalidate
    if (form.hasAttribute('data-validate')) {
      this.validateFormOnSubmit(form);
    }
  });
};

/**
 * Валидация формы при отправке
 */
SchoolApp.components.Forms.validateFormOnSubmit = function(form) {
  form.addEventListener('submit', (e) => {
    if (form.hasAttribute('data-validate')) {
      const isValid = this.validateForm(form);
      
      if (!isValid) {
        e.preventDefault();
        e.stopPropagation();
        
        // Прокрутка к первой ошибке
        const firstError = form.querySelector('.error-message');
        if (firstError) {
          firstError.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
        }
        
        SchoolApp.showNotification('Пожалуйста, исправьте ошибки в форме', 'error');
        return false;
      }
    }
    
    return true;
  });
};

/**
 * Основная функция валидации формы
 */
SchoolApp.components.Forms.validateForm = function(form) {
  let isValid = true;
  const fields = form.querySelectorAll('input, select, textarea');
  
  // Снимаем предыдущие ошибки
  this.clearErrors(form);
  
  fields.forEach(field => {
    if (!this.validateField(field)) {
      isValid = false;
    }
  });
  
  // Валидация совпадения паролей
  const passwordField = form.querySelector('[type="password"][name="password"]');
  const confirmPasswordField = form.querySelector('[type="password"][name="confirm_password"]');
  
  if (passwordField && confirmPasswordField) {
    if (passwordField.value !== confirmPasswordField.value) {
      this.showFieldError(confirmPasswordField, 'Пароли не совпадают');
      isValid = false;
    }
  }
  
  return isValid;
};

/**
 * Валидация отдельного поля
 */
SchoolApp.components.Forms.validateField = function(field) {
  const formGroup = this.getFormGroup(field);
  let isValid = true;
  
  // Обязательное поле
  if (field.hasAttribute('required') && !field.disabled) {
    if (!this.isRequired(field.value)) {
      this.showFieldError(field, 'Это поле обязательно для заполнения');
      return false;
    }
  }
  
  // Минимальная длина
  const minLength = field.getAttribute('minlength');
  if (minLength && field.value.length < parseInt(minLength)) {
    this.showFieldError(field, `Минимальная длина: ${minLength} символов`);
    return false;
  }
  
  // Максимальная длина
  const maxLength = field.getAttribute('maxlength');
  if (maxLength && field.value.length > parseInt(maxLength)) {
    this.showFieldError(field, `Максимальная длина: ${maxLength} символов`);
    return false;
  }
  
  // Проверка по атрибуту pattern
  if (field.hasAttribute('pattern')) {
    const pattern = new RegExp(field.getAttribute('pattern'));
    if (field.value && !pattern.test(field.value)) {
      const title = field.getAttribute('title') || 'Неверный формат';
      this.showFieldError(field, title);
      return false;
    }
  }
  
  // Валидация по типу поля
  switch (field.type) {
    case 'email':
      if (field.value && !this.methods.email(field.value)) {
        this.showFieldError(field, 'Введите корректный email адрес');
        isValid = false;
      }
      break;
      
    case 'url':
      if (field.value && !this.methods.url(field.value)) {
        this.showFieldError(field, 'Введите корректный URL');
        isValid = false;
      }
      break;
      
    case 'tel':
      if (field.value && !this.methods.phone(field.value)) {
        this.showFieldError(field, 'Введите корректный номер телефона');
        isValid = false;
      }
      break;
      
    case 'password':
      if (field.value && (!this.methods.password(field.value) || field.value.length < 8)) {
        this.showFieldError(field, 'Пароль должен содержать минимум 8 символов');
        isValid = false;
      }
      break;
      
    case 'number':
      if (field.value) {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        const num = parseFloat(field.value);
        
        if (min !== null && num < parseFloat(min)) {
          this.showFieldError(field, `Минимальное значение: ${min}`);
          isValid = false;
        } else if (max !== null && num > parseFloat(max)) {
          this.showFieldError(field, `Максимальное значение: ${max}`);
          isValid = false;
        }
      }
      break;
      
    case 'date':
      if (field.value && !this.methods.date(field.value)) {
        this.showFieldError(field, 'Введите корректную дату');
        isValid = false;
      }
      break;
  }
  
  // Пользовательская валидация по тегу data-validate
  if (field.hasAttribute('data-validate')) {
    const validatorName = field.getAttribute('data-validate');
    if (this.validators[validatorName]) {
      const result = this.validators[validatorName](field.value, field);
      if (result !== true) {
        this.showFieldError(field, result || 'Ошибка валидации');
        isValid = false;
      }
    }
  }
  
  // Скрыть статус ошибки если поле валидно
  if (isValid) {
    this.hideFieldError(field);
  }
  
  return isValid;
};

/**
 * Показать ошибку поля
 */
SchoolApp.components.Forms.showFieldError = function(field, message) {
  const formGroup = this.getFormGroup(field);
  
  // Добавить класс ошибки
  formGroup.classList.add('error');
  field.classList.add('error');
  
  // Удалить предыдущее сообщение об ошибке
  const existingError = formGroup.querySelector('.error-message');
  if (existingError) {
    existingError.remove();
  }
  
  // Создать новое сообщение об ошибке
  const errorEl = document.createElement('div');
  errorEl.className = 'error-message';
  errorEl.textContent = message;
  errorEl.setAttribute('role', 'alert');
  
  // Вставить после поля или группы
  if (field.type === 'checkbox' || field.type === 'radio') {
    const label = formGroup.querySelector('.form-check-label');
    if (label) {
      label.parentNode.insertBefore(errorEl, label.nextSibling);
    } else {
      field.parentNode.insertBefore(errorEl, field.nextSibling);
    }
  } else {
    field.parentNode.insertBefore(errorEl, field.nextSibling);
  }
  
  // Добавить ARIA атрибуты
  field.setAttribute('aria-invalid', 'true');
  const errorId = `error-${field.name || 'field'}-${Date.now()}`;
  errorEl.id = errorId;
  field.setAttribute('aria-describedby', errorId);
};

/**
 * Скрыть ошибку поля
 */
SchoolApp.components.Forms.hideFieldError = function(field) {
  const formGroup = this.getFormGroup(field);
  const errorMessage = formGroup.querySelector('.error-message');
  
  // Удалить классы ошибки
  formGroup.classList.remove('error');
  field.classList.remove('error');
  
  // Удалить сообщение об ошибке
  if (errorMessage) {
    errorMessage.remove();
  }
  
  // Удалить ARIA атрибуты
  field.removeAttribute('aria-invalid');
  field.removeAttribute('aria-describedby');
};

/**
 * Очистить все ошибки в форме
 */
SchoolApp.components.Forms.clearErrors = function(form) {
  form.querySelectorAll('.error-message').forEach(error => error.remove());
  form.querySelectorAll('.error').forEach(field => {
    field.classList.remove('error');
    field.removeAttribute('aria-invalid');
    field.removeAttribute('aria-describedby');
  });
};

/**
 * Получить группу формы для поля
 */
SchoolApp.components.Forms.getFormGroup = function(field) {
  return field.closest('.form-group, .form-check');
};

/**
 * Установка переключателей показа пароля
 */
SchoolApp.components.Forms.setupPasswordToggle = function() {
  document.querySelectorAll('.password-toggle').forEach(toggle => {
    const targetId = toggle.getAttribute('data-target');
    const targetField = document.getElementById(targetId);
    
    if (targetField) {
      toggle.addEventListener('click', () => {
        const type = targetField.getAttribute('type') === 'password' ? 'text' : 'password';
        targetField.setAttribute('type', type);
        
        // Изменить иконку
        toggle.innerHTML = type === 'password' ? '👁️' : '🙈';
      });
    }
  });
};

/**
 * Реальная валидация при вводе
 */
SchoolApp.components.Forms.setupRealTimeValidation = function() {
  document.querySelectorAll('form[data-validate] input, form[data-validate] select, form[data-validate] textarea').forEach(field => {
    // Проверка при уходе с поля
    field.addEventListener('blur', () => {
      this.validateField(field);
    });
    
    // Проверка при изменении
    field.addEventListener('input', SchoolApp.utils.debounce(() => {
      if (field.classList.contains('error')) {
        this.validateField(field);
      }
    }, 300));
    
    // Проверка при изменении (для select)
    field.addEventListener('change', () => {
      if (field.classList.contains('error')) {
        this.validateField(field);
      }
    });
  });
};

/**
 * Подтверждение при отправке формы
 */
SchoolApp.components.Forms.setupConfirmSubmit = function() {
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', (e) => {
      const message = form.dataset.confirm || 'Вы уверены, что хотите выполнить это действие?';
      
      e.preventDefault();
      
      SchoolApp.showConfirm(message, (confirmed) => {
        if (confirmed) {
          form.removeAttribute('data-confirm');
          form.submit();
        }
      });
    });
  });
};

/**
 * Отслеживание несохраненных изменений
 */
SchoolApp.components.Forms.setupUnsavedChanges = function() {
  document.querySelectorAll('form[data-watch-unsaved]').forEach(form => {
    let hasUnsavedChanges = false;
    
    form.addEventListener('input', () => {
      hasUnsavedChanges = true;
      form.dataset.unsaved = 'true';
      window.dispatchEvent(new Event('beforeunload'));
    });
    
    form.addEventListener('submit', () => {
      hasUnsavedChanges = false;
      form.dataset.unsaved = 'false';
    });
    
    // Сброс при возврате назад
    window.addEventListener('beforeunload', (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    });
  });
};

/**
 * Валидация обязательных полей
 */
SchoolApp.components.Forms.isRequired = function(value) {
  return value !== null && value !== undefined && value.toString().trim() !== '';
};

/**
 * Методы валидации
 */
SchoolApp.components.Forms.methods = {
  /**
   * Валидация email
   */
  email: function(value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  },
  
  /**
   * Валидация URL
   */
  url: function(value) {
    try {
      new URL(value);
      return true;
    } catch (e) {
      return false;
    }
  },
  
  /**
   * Валидация телефона
   */
  phone: function(value) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(value.replace(/\s/g, ''));
  },
  
  /**
   * Валидация пароля
   */
  password: function(value) {
    // Минимум 8 символов, хотя бы одна буква и одна цифра
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/;
    return passwordRegex.test(value);
  },
  
  /**
   * Валидация даты
   */
  date: function(value) {
    const date = new Date(value);
    return date instanceof Date && !isNaN(date);
  },
  
  /**
   * Валидация целого числа
   */
  integer: function(value) {
    return /^-?\d+$/.test(value);
  },
  
  /**
   * Валидация числа с плавающей точкой
   */
  numeric: function(value) {
    return !isNaN(parseFloat(value)) && isFinite(value);
  }
};

/**
 * Кастомные валидаторы (можно расширять)
 */
SchoolApp.components.Forms.validators = {
  /**
   * Валидация имени (только буквы и пробелы)
   */
  name: function(value) {
    if (!/^[A-Za-zА-Яа-я\s]+$/.test(value)) {
      return 'Поле должно содержать только буквы';
    }
    return true;
  },
  
  /**
   * Валидация возраста
   */
  age: function(value) {
    const age = parseInt(value);
    if (isNaN(age) || age < 1 || age > 120) {
      return 'Возраст должен быть от 1 до 120';
    }
    return true;
  },
  
  /**
   * Валидация студенческого ID
   */
  studentId: function(value) {
    if (!/^\d{4,8}$/.test(value)) {
      return 'ID студента должен содержать от 4 до 8 цифр';
    }
    return true;
  }
};

/**
 * Добавить кастомный валидатор
 */
SchoolApp.components.Forms.addValidator = function(name, validator) {
  this.validators[name] = validator;
};

/**
 * Показать успех поля
 */
SchoolApp.components.Forms.showFieldSuccess = function(field) {
  field.classList.add('success');
  this.hideFieldError(field);
  
  // Очистить через 2 секунды
  setTimeout(() => {
    field.classList.remove('success');
  }, 2000);
};

// Экспорт для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SchoolApp.components.Forms;
}