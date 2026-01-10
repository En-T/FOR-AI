/**
 * Вспомогательные функции и утилиты
 * Общие функции, используемые в разных частях приложения
 */

SchoolApp.utils = SchoolApp.utils || {};

/**
 * Форматирование дат
 */
SchoolApp.utils.formatDate = function(date, format = 'DD.MM.YYYY') {
  const d = new Date(date);
  
  if (isNaN(d.getTime())) {
    return '';
  }
  
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  
  switch (format) {
    case 'DD.MM.YYYY':
      return `${day}.${month}.${year}`;
    case 'YYYY-MM-DD':
      return `${year}-${month}-${day}`;
    case 'DD Month YYYY':
      const months = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
      ];
      return `${day} ${months[d.getMonth()]} ${year}`;
    case 'DD.MM.YYYY HH:mm':
      return `${day}.${month}.${year} ${hours}:${minutes}`;
    case 'datetime':
      return d.toLocaleString('ru-RU');
    default:
      return `${day}.${month}.${year}`;
  }
};

/**
 * Форматирование чисел
 */
SchoolApp.utils.formatNumber = function(number, decimals = 0, decimalPoint = ',', thousandsSep = ' ') {
  number = parseFloat(number);
  
  if (isNaN(number)) {
    return '';
  }
  
  const fixed = number.toFixed(decimals);
  const parts = fixed.split('.');
  
  // Разделитель тысяч
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousandsSep);
  
  return parts.join(decimalPoint || '.');
};

/**
 * Форматирование валюты
 */
SchoolApp.utils.formatCurrency = function(amount, currency = '₽', decimals = 2) {
  return `${SchoolApp.utils.formatNumber(amount, decimals)} ${currency}`;
};

/**
 * Форматирование процентов
 */
SchoolApp.utils.formatPercent = function(value, decimals = 1) {
  return `${SchoolApp.utils.formatNumber(value, decimals)}%`;
};

/**
 * Усечение текста
 */
SchoolApp.utils.truncate = function(text, maxLength = 50, suffix = '...') {
  if (!text || typeof text !== 'string') {
    return '';
  }
  
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.substring(0, maxLength) + suffix;
};

/**
 * Экранирование HTML
 */
SchoolApp.utils.escapeHtml = function(text) {
  if (!text) return '';
  
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  
  return text.toString().replace(/[&<>"']/g, m => map[m]);
};

/**
 * Генерация уникального ID
 */
SchoolApp.utils.generateId = function(prefix = 'id') {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Получить cookie
 */
SchoolApp.utils.getCookie = function(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='));
  
  return cookieValue ? cookieValue.split('=')[1] : null;
};

/**
 * Установить cookie
 */
SchoolApp.utils.setCookie = function(name, value, days = 7) {
  const expires = new Date();
  expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
  
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
};

/**
 * Удалить cookie
 */
SchoolApp.utils.deleteCookie = function(name) {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/`;
};

/**
 * Сохранить данные в localStorage
 */
SchoolApp.utils.saveLocal = function(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data));
    return true;
  } catch (e) {
    console.error('Failed to save to localStorage:', e);
    return false;
  }
};

/**
 * Получить данные из localStorage
 */
SchoolApp.utils.getLocal = function(key, defaultValue = null) {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (e) {
    console.error('Failed to get from localStorage:', e);
    return defaultValue;
  }
};

/**
 * Удалить данные из localStorage
 */
SchoolApp.utils.removeLocal = function(key) {
  localStorage.removeItem(key);
};

/**
 * Очистить localStorage (с префиксом)
 */
SchoolApp.utils.clearLocal = function(prefix = '') {
  const keys = Object.keys(localStorage);
  keys.forEach(key => {
    if (!prefix || key.startsWith(prefix)) {
      localStorage.removeItem(key);
    }
  });
};

/**
 * Копировать в буфер обмена
 */
SchoolApp.utils.copyToClipboard = function(text) {
  return new Promise((resolve, reject) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text)
        .then(() => resolve(true))
        .catch(err => reject(err));
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (success) {
          resolve(true);
        } else {
          reject(new Error('Copy failed'));
        }
      } catch (err) {
        document.body.removeChild(textArea);
        reject(err);
      }
    }
  });
};

/**
 * Скачать файл
 */
SchoolApp.utils.downloadFile = function(data, filename, contentType = 'text/plain') {
  const blob = new Blob([data], { type: contentType });
  const url = window.URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.style.display = 'none';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  window.URL.revokeObjectURL(url);
};

/**
 * Получить параметры URL
 */
SchoolApp.utils.getUrlParams = function() {
  const params = new URLSearchParams(window.location.search);
  const result = {};
  
  for (const [key, value] of params.entries()) {
    if (key in result) {
      if (Array.isArray(result[key])) {
        result[key].push(value);
      } else {
        result[key] = [result[key], value];
      }
    } else {
      result[key] = value;
    }
  }
  
  return result;
};

/**
 * Обновить параметры URL без перезагрузки
 */
SchoolApp.utils.updateUrlParams = function(params) {
  const url = new URL(window.location.href);
  
  Object.keys(params).forEach(key => {
    if (params[key] === null || params[key] === undefined || params[key] === '') {
      url.searchParams.delete(key);
    } else {
      url.searchParams.set(key, params[key]);
    }
  });
  
  window.history.replaceState({}, '', url);
};

/**
 * Проверить, является ли устройство мобильным
 */
SchoolApp.utils.isMobile = function() {
  return window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

/**
 * Проверить, является ли устройство планшетом
 */
SchoolApp.utils.isTablet = function() {
  return window.innerWidth > 768 && window.innerWidth <= 1024;
};

/**
 * Проверить, является ли устройство десктопом
 */
SchoolApp.utils.isDesktop = function() {
  return window.innerWidth > 1024;
};

/**
 * Получить размер экрана
 */
SchoolApp.utils.getScreenSize = function() {
  const width = window.innerWidth;
  
  if (width >= 1200) return 'xl';
  if (width >= 1024) return 'lg';
  if (width >= 768) return 'md';
  if (width >= 480) return 'sm';
  return 'xs';
};

/**
 * Утилита debounce
 */
SchoolApp.utils.debounce = function(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func.apply(this, args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Утилита throttle
 */
SchoolApp.utils.throttle = function(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * Генератор случайных чисел в диапазоне
 */
SchoolApp.utils.random = function(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

/**
 * Генерация UUID
 */
SchoolApp.utils.uuid = function() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

/**
 * Глубокое клонирование объекта
 */
SchoolApp.utils.deepClone = function(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => SchoolApp.utils.deepClone(item));
  if (typeof obj === 'object') {
    const clonedObj = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = SchoolApp.utils.deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
};

/**
 * Объединение объектов (deep merge)
 */
SchoolApp.utils.merge = function(target, ...sources) {
  if (!sources.length) return target;
  const source = sources.shift();
  
  if (SchoolApp.utils.isObject(target) && SchoolApp.utils.isObject(source)) {
    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        if (SchoolApp.utils.isObject(source[key])) {
          if (!target[key]) Object.assign(target, { [key]: {} });
          SchoolApp.utils.merge(target[key], source[key]);
        } else {
          Object.assign(target, { [key]: source[key] });
        }
      }
    }
  }
  
  return SchoolApp.utils.merge(target, ...sources);
};

/**
 * Проверка является ли значение объектом
 */
SchoolApp.utils.isObject = function(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
};

/**
 * Проверка является ли значение пустым
 */
SchoolApp.utils.isEmpty = function(value) {
  if (value == null) return true;
  if (typeof value === 'boolean') return false;
  if (typeof value === 'number') return false;
  if (typeof value === 'string') return value.length === 0;
  if (Array.isArray(value)) return value.length === 0;
  if (SchoolApp.utils.isObject(value)) return Object.keys(value).length === 0;
  return false;
};

/**
 * Поиск элемента в массиве объектов
 */
SchoolApp.utils.find = function(array, predicate) {
  return array.find(predicate);
};

/**
 * Фильтрация массива
 */
SchoolApp.utils.filter = function(array, predicate) {
  return array.filter(predicate);
};

/**
 * Карта массива
 */
SchoolApp.utils.map = function(array, callback) {
  return array.map(callback);
};

/**
 * Индекс элемента в массиве
 */
SchoolApp.utils.findIndex = function(array, predicate) {
  return array.findIndex(predicate);
};

/**
 * Удалить элемент из массива по индексу
 */
SchoolApp.utils.removeAt = function(array, index) {
  return [...array.slice(0, index), ...array.slice(index + 1)];
};

/**
 * Переместить элемент в массиве
 */
SchoolApp.utils.move = function(array, fromIndex, toIndex) {
  const newArray = [...array];
  const element = newArray.splice(fromIndex, 1)[0];
  newArray.splice(toIndex, 0, element);
  return newArray;
};

/**
 * Уникальные значения в массиве
 */
SchoolApp.utils.unique = function(array) {
  return [...new Set(array)];
};

/**
 * Группировка массива
 */
SchoolApp.utils.groupBy = function(array, key) {
  return array.reduce((result, item) => {
    const group = item[key];
    result[group] = result[group] || [];
    result[group].push(item);
    return result;
  }, {});
};

/**
 * Сортировка массива
 */
SchoolApp.utils.sortBy = function(array, key, order = 'asc') {
  const sorted = [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal < bVal) return order === 'asc' ? -1 : 1;
    if (aVal > bVal) return order === 'asc' ? 1 : -1;
    return 0;
  });
  
  return sorted;
};

/**
 * Генерация строки случайных символов
 */
SchoolApp.utils.randomString = function(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

/**
 * Преобразование в kebab-case
 */
SchoolApp.utils.kebabCase = function(str) {
  return str.replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase();
};

/**
 * Преобразование в camelCase
 */
SchoolApp.utils.camelCase = function(str) {
  return str.replace(/[-_\s]+(.)?/g, (_, char) => char ? char.toUpperCase() : '');
};

/**
 * Преобразование в PascalCase
 */
SchoolApp.utils.pascalCase = function(str) {
  const camel = SchoolApp.utils.camelCase(str);
  return camel.charAt(0).toUpperCase() + camel.slice(1);
};

/**
 * Валидация email
 */
SchoolApp.utils.isEmail = function(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

/**
 * Валидация URL
 */
SchoolApp.utils.isUrl = function(url) {
  try {
    new URL(url);
    return true;
  } catch (e) {
    return false;
  }
};

/**
 * Валидация телефона
 */
SchoolApp.utils.isPhone = function(phone) {
  const regex = /^[\+]?[1-9][\d]{0,15}$/;
  return regex.test(phone.replace(/\s/g, ''));
};

/**
 * Валидация UUID
 */
SchoolApp.utils.isUuid = function(uuid) {
  const regex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return regex.test(uuid);
};

/**
 * Валидация JSON строки
 */
SchoolApp.utils.isJson = function(str) {
  try {
    JSON.parse(str);
    return true;
  } catch (e) {
    return false;
  }
};

/**
 * Аналог jQuery.ready()
 */
SchoolApp.utils.ready = function(callback) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', callback);
  } else {
    callback();
  }
};

// Экспорт для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SchoolApp.utils;
}