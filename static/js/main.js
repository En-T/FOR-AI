/**
 * Главный скрипт приложения управления школой
 * Инициализация компонентов, AJAX запросы, обработка ошибок
 */

// Глобальные переменные
window.SchoolApp = {
  config: {
    baseUrl: '',
    csrfToken: '',
    apiUrl: '/api/',
    timeout: 30000,
    maxRetries: 3
  },
  components: {},
  utils: {}
};

// Базовые утилиты
document.addEventListener('DOMContentLoaded', function() {
  SchoolApp.init();
});

SchoolApp.init = function() {
  console.log('School App initializing...');
  
  // Установка CSRF токена
  this.setupCsrfToken();
  
  // Инициализация компонентов
  this.initComponents();
  
  // Установка обработчиков событий
  this.setupEventListeners();
  
  console.log('School App initialized');
};

SchoolApp.setupCsrfToken = function() {
  const metaTag = document.querySelector('meta[name="csrf-token"]');
  if (metaTag) {
    this.config.csrfToken = metaTag.getAttribute('content');
  } else {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    if (cookieValue) {
      this.config.csrfToken = cookieValue.split('=')[1];
    }
  }
};

SchoolApp.initComponents = function() {
  // Инициализация компонентов если они существуют
  if (typeof SchoolApp.components.Modals !== 'undefined') {
    SchoolApp.components.Modals.init();
  }
  
  if (typeof SchoolApp.components.Forms !== 'undefined') {
    SchoolApp.components.Forms.init();
  }
  
  if (typeof SchoolApp.components.Tables !== 'undefined') {
    SchoolApp.components.Tables.init();
  }
  
  if (typeof SchoolApp.components.TransferBox !== 'undefined') {
    SchoolApp.components.TransferBox.init();
  }
  
  // Автов инициализация компонентов по data-атрибутам
  this.autoInitComponents();
};

SchoolApp.autoInitComponents = function() {
  // Автов инициализация tooltips
  document.querySelectorAll('[data-tooltip]').forEach(element => {
    this.initTooltip(element);
  });
  
  // Автов инициализация dropdown
  document.querySelectorAll('[data-dropdown]').forEach(element => {
    this.initDropdown(element);
  });
  
  // Автов инициализация popovers
  document.querySelectorAll('[data-popover]').forEach(element => {
    this.initPopover(element);
  });
};

SchoolApp.setupEventListeners = function() {
  // Обработчик клика на мобильном меню
  const navbarToggle = document.querySelector('.navbar-toggle');
  if (navbarToggle) {
    navbarToggle.addEventListener('click', this.toggleMobileSidebar.bind(this));
  }
  
  // Обработчик для оверлея мобильного меню
  const overlay = document.querySelector('.sidebar-overlay');
  if (overlay) {
    overlay.addEventListener('click', this.closeMobileSidebar.bind(this));
  }
  
  // Обработчик для сворачивания sidebar
  const sidebarToggle = document.querySelector('.sidebar-toggle-btn');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', this.toggleSidebar.bind(this));
  }
  
  // Обработчики для активного состояния меню
  this.setupNavigationListeners();
  
  // Обработчики для закрытия при клике вне элементов
  document.addEventListener('click', this.handleDocumentClick.bind(this));
  
  // Обработчики для клавиатуры
  document.addEventListener('keydown', this.handleKeyboard.bind(this));
  
  // Обработчики для форм (предотвращение двойной отправки)
  this.setupFormSubmitHandlers();
  
  // Обработчики для анимаций загрузки
  this.setupLoadingHandlers();
  
  // Обработчики для выхода со страницы
  window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
  
  // Обработчики для изменения размера окна
  let resizeTimeout;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
      SchoolApp.handleResize();
    }, 250);
  });
};

SchoolApp.setupNavigationListeners = function() {
  // Обработка активных пунктов меню
  document.querySelectorAll('.sidebar-nav-link, .navbar-nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
      // Удаляем активный класс у всех ссылок
      document.querySelectorAll('.sidebar-nav-link.active, .navbar-nav-link.active').forEach(activeLink => {
        activeLink.classList.remove('active');
      });
      
      // Добавляем активный класс текущей ссылке
      this.classList.add('active');
    });
  });
  
  // Обработка хлебных крошек
  document.querySelectorAll('.breadcrumb-link').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const href = this.getAttribute('href');
      if (href && href !== '#') {
        SchoolApp.navigate(href);
      }
    });
  });
};

SchoolApp.setupFormSubmitHandlers = function() {
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', this.handleFormSubmit.bind(this));
  });
};

SchoolApp.setupLoadingHandlers = function() {
  // Показать индикатор загрузки при необходимости
  document.addEventListener('ajaxSend', function() {
    document.body.classList.add('loading');
  });
  
  document.addEventListener('ajaxComplete', function() {
    document.body.classList.remove('loading');
  });
};

SchoolApp.toggleMobileSidebar = function() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  const body = document.body;
  
  if (sidebar && overlay) {
    sidebar.classList.toggle('mobile-open');
    overlay.classList.toggle('active');
    body.classList.toggle('body-scroll-lock');
    
    // ARIA атрибуты
    const isOpen = sidebar.classList.contains('mobile-open');
    sidebar.setAttribute('aria-hidden', !isOpen);
    overlay.setAttribute('aria-hidden', !isOpen);
  }
};

SchoolApp.closeMobileSidebar = function() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  const body = document.body;
  
  if (sidebar && overlay) {
    sidebar.classList.remove('mobile-open');
    overlay.classList.remove('active');
    body.classList.remove('body-scroll-lock');
    
    // ARIA атрибуты
    sidebar.setAttribute('aria-hidden', 'true');
    overlay.setAttribute('aria-hidden', 'true');
  }
};

SchoolApp.toggleSidebar = function() {
  const appWrapper = document.querySelector('.app-wrapper');
  if (appWrapper) {
    appWrapper.classList.toggle('sidebar-collapsed');
    
    // Сохранение состояния в localStorage
    const isCollapsed = appWrapper.classList.contains('sidebar-collapsed');
    localStorage.setItem('sidebar-collapsed', isCollapsed);
  }
};

SchoolApp.handleDocumentClick = function(e) {
  // Закрыть dropdown при клике вне их
  const dropdowns = document.querySelectorAll('.dropdown.show');
  dropdowns.forEach(dropdown => {
    if (!dropdown.contains(e.target)) {
      dropdown.classList.remove('show');
    }
  });
  
  // Закрыть tooltip при клике
  const tooltips = document.querySelectorAll('.tooltip.show');
  tooltips.forEach(tooltip => {
    if (!tooltip.contains(e.target)) {
      tooltip.classList.remove('show');
    }
  });
};

SchoolApp.handleKeyboard = function(e) {
  // Esc закрывает модальные окна
  if (e.key === 'Escape') {
    const modals = document.querySelectorAll('.modal.show');
    modals.forEach(modal => {
      if (typeof SchoolApp.components.Modals !== 'undefined') {
        SchoolApp.components.Modals.close(modal);
      }
    });
    
    // Закрыть мобильное меню
    this.closeMobileSidebar();
  }
  
  // Ctrl+S для сохранения формы
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    const activeForm = document.querySelector('form');
    if (activeForm && activeForm.querySelector('[type="submit"]')) {
      activeForm.dispatchEvent(new Event('submit'));
    }
  }
};

SchoolApp.handleFormSubmit = function(e) {
  const form = e.target;
  const submitBtn = form.querySelector('[type="submit"]');
  
  // Предотвращение двойной отправки
  if (form.dataset.submitting === 'true') {
    e.preventDefault();
    return;
  }
  
  // Показать состояние загрузки
  if (submitBtn) {
    submitBtn.classList.add('btn-loading');
    submitBtn.disabled = true;
  }
  
  form.dataset.submitting = 'true';
  
  // Очистить состояние после отправки
  setTimeout(function() {
    form.dataset.submitting = 'false';
    if (submitBtn) {
      submitBtn.classList.remove('btn-loading');
      submitBtn.disabled = false;
    }
  }, 1000);
};

SchoolApp.handleBeforeUnload = function(e) {
  const unsavedForms = document.querySelectorAll('form[data-unsaved="true"]');
  if (unsavedForms.length > 0) {
    e.preventDefault();
    e.returnValue = 'Вы имеете несохраненные изменения. Вы уверены, что хотите покинуть страницу?';
    return e.returnValue;
  }
};

SchoolApp.handleResize = function() {
  const width = window.innerWidth;
  
  // Скрыть/показать меню при изменении размера
  if (width > 767) {
    this.closeMobileSidebar();
  }
  
  // Восстановить sidebar на десктопах
  if (width > 1199) {
    const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    const appWrapper = document.querySelector('.app-wrapper');
    if (appWrapper) {
      if (isCollapsed) {
        appWrapper.classList.add('sidebar-collapsed');
      } else {
        appWrapper.classList.remove('sidebar-collapsed');
      }
    }
  }
};

SchoolApp.navigate = function(url, options = {}) {
  if (options.ajax === false) {
    window.location.href = url;
    return;
  }
  
  const defaultOptions = {
    ajax: true,
    showLoading: true,
    pushState: true,
    target: '.main-content',
  };
  
  const config = Object.assign({}, defaultOptions, options);
  
  if (config.showLoading) {
    document.dispatchEvent(new Event('ajaxSend'));
  }
  
  return this.ajax({
    url: url,
    method: 'GET',
    success: function(response) {
      const targetElement = document.querySelector(config.target);
      if (targetElement) {
        targetElement.innerHTML = response;
      }
      
      if (config.pushState && history.pushState) {
        history.pushState({url: url}, '', url);
      }
      
      // Реинициализация компонентов
      SchoolApp.initComponents();
    },
    error: function(error) {
      console.error('Navigation error:', error);
      if (error.status === 404) {
        window.location.href = '/404/';
      } else {
        window.location.href = '/500/';
      }
    },
    complete: function() {
      if (config.showLoading) {
        document.dispatchEvent(new Event('ajaxComplete'));
      }
    }
  });
};

SchoolApp.ajax = function(options) {
  const defaultOptions = {
    method: 'GET',
    headers: {},
    credentials: 'same-origin'
  };
  
  const config = Object.assign({}, defaultOptions, options);
  
  // Добавление CSRF токена для POST/PUT/DELETE запросов
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method.toUpperCase())) {
    config.headers['X-CSRFToken'] = this.config.csrfToken;
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
  }
  
  return fetch(config.url, config)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json();
      }
      return response.text();
    })
    .then(data => {
      if (config.success && typeof config.success === 'function') {
        config.success(data);
      }
      return data;
    })
    .catch(error => {
      console.error('AJAX Error:', error);
      if (config.error && typeof config.error === 'function') {
        config.error(error);
      }
      throw error;
    })
    .finally(() => {
      if (config.complete && typeof config.complete === 'function') {
        config.complete();
      }
    });
};

SchoolApp.showNotification = function(message, type = 'info', duration = 5000) {
  const alertId = 'alert-' + Date.now();
  const alertHtml = `
    <div id="${alertId}" class="alert alert-${type} alert-dismissible" role="alert">
      <div class="alert-content">
        <span class="alert-icon">${this.getAlertIcon(type)}</span>
        <div class="alert-text">${message}</div>
      </div>
      <button type="button" class="close-btn" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  `;
  
  const container = document.body.querySelector('.alert-container') || (function() {
    const container = document.createElement('div');
    container.className = 'alert-container';
    document.body.appendChild(container);
    return container;
  })();
  
  container.insertAdjacentHTML('beforeend', alertHtml);
  
  const alert = document.getElementById(alertId);
  setTimeout(() => alert.classList.add('show'), 10);
  
  // Автоматическое скрытие
  if (duration > 0) {
    setTimeout(() => {
      this.hideNotification(alertId);
    }, duration);
  }
  
  // Обработчик закрытия
  const closeBtn = alert.querySelector('[data-dismiss="alert"]');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => this.hideNotification(alertId));
  }
  
  return alertId;
};

SchoolApp.hideNotification = function(alertId) {
  const alert = document.getElementById(alertId);
  if (alert) {
    alert.classList.remove('show');
    setTimeout(() => alert.remove(), 300);
  }
};

SchoolApp.getAlertIcon = function(type) {
  const icons = {
    success: '✓',
    error: '✗',
    warning: '⚠',
    info: 'ℹ'
  };
  return icons[type] || icons.info;
};

SchoolApp.showConfirm = function(message, callback, options = {}) {
  const defaultOptions = {
    title: 'Подтвердите действие',
    confirmText: 'Подтвердить',
    cancelText: 'Отмена',
    confirmType: 'danger'
  };
  
  const config = Object.assign({}, defaultOptions, options);
  
  const modalHtml = `
    <div class="modal show" id="confirm-modal" tabindex="-1" role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">${config.title}</h5>
            <button type="button" class="close-btn" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <p>${message}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">${config.cancelText}</button>
            <button type="button" class="btn btn-${config.confirmType}" id="confirm-ok">${config.confirmText}</button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop show"></div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  
  const modal = document.getElementById('confirm-modal');
  const backdrop = document.querySelector('.modal-backdrop');
  
  const closeModal = () => {
    modal.remove();
    backdrop.remove();
    document.body.classList.remove('modal-open');
  };
  
  const confirmBtn = document.getElementById('confirm-ok');
  confirmBtn.addEventListener('click', () => {
    if (callback && typeof callback === 'function') {
      callback(true);
    }
    closeModal();
  });
  
  // Обработчики закрытия
  modal.querySelectorAll('[data-dismiss="modal"]').forEach(btn => {
    btn.addEventListener('click', closeModal);
  });
  
  backdrop.addEventListener('click', closeModal);
  
  document.addEventListener('keydown', function handler(e) {
    if (e.key === 'Escape') {
      closeModal();
      document.removeEventListener('keydown', handler);
    }
  });
  
  document.body.classList.add('modal-open');
};

SchoolApp.utils.debounce = function(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

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

SchoolApp.utils.formatDate = function(date, format = 'DD.MM.YYYY') {
  const d = new Date(date);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  
  switch (format) {
    case 'DD.MM.YYYY':
      return `${day}.${month}.${year}`;
    case 'YYYY-MM-DD':
      return `${year}-${month}-${day}`;
    case 'DD Month YYYY':
      const months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                      'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
      return `${day} ${months[d.getMonth()]} ${year}`;
    default:
      return `${day}.${month}.${year}`;
  }
};

SchoolApp.utils.formatNumber = function(number, decimals = 0, decimalPoint = ',', thousandsSep = ' ') {
  number = parseFloat(number);
  if (isNaN(number)) return '';
  
  const fixed = number.toFixed(decimals);
  const parts = fixed.split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousandsSep);
  return parts.join(decimalPoint || '.');
};

SchoolApp.utils.truncate = function(text, maxLength = 50, suffix = '...') {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + suffix;
};

SchoolApp.utils.escapeHtml = function(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
};

// Обработка истории браузера
window.addEventListener('popstate', function(e) {
  if (e.state && e.state.url) {
    SchoolApp.navigate(e.state.url, { pushState: false });
  }
});

// Установить начальное состояние
if (history.state === null) {
  history.replaceState({ url: window.location.href }, '');
}