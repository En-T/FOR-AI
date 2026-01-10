/**
 * Модальные окна и диалоги
 * Открытие/закрытие, подтверждения, AJAX модальные окна
 */

SchoolApp.components = SchoolApp.components || {};
SchoolApp.components.Modals = {
  activeModals: new Set(),
  modalStack: []
};

/**
 * Инициализация модальных окон
 */
SchoolApp.components.Modals.init = function() {
  this.setupModalHandlers();
  this.setupConfirmHandlers();
  this.setupAjaxModals();
  this.setupModalHelpers();
};

/**
 * Настройка обработчиков модальных окон
 */
SchoolApp.components.Modals.setupModalHandlers = function() {
  // Обработчики открытия модальных окон
  document.querySelectorAll('[data-toggle="modal"]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = trigger.getAttribute('data-target') || trigger.getAttribute('href');
      const modal = document.querySelector(targetId);
      
      if (modal) {
        const options = {
          backdrop: trigger.getAttribute('data-backdrop') !== 'false',
          keyboard: trigger.getAttribute('data-keyboard') !== 'false',
          focus: trigger.getAttribute('data-focus') !== 'false'
        };
        
        this.show(modal, options);
      }
    });
  });
  
  // Обработчики закрытия по клику на крестик
  document.querySelectorAll('.modal [data-dismiss="modal"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const modal = btn.closest('.modal');
      this.hide(modal);
    });
  });
  
  // Обработчики закрытия модального окна
  this.setupModalCloseHandlers();
};

/**
 * Настройка обработчиков закрытия модальных окон
 */
SchoolApp.components.Modals.setupModalCloseHandlers = function() {
  // Клик на фон
  document.addEventListener('click', (e) => {
    const modal = e.target.closest('.modal');
    if (modal && e.target === modal && modal.classList.contains('show')) {
      const backdrop = modal.getAttribute('data-backdrop');
      if (backdrop !== 'static') {
        this.hide(modal);
      }
    }
  });
  
  // Нажатие клавиши Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const topModal = this.getTopModal();
      if (topModal) {
        const keyboard = topModal.getAttribute('data-keyboard');
        if (keyboard !== 'false') {
          this.hide(topModal);
        }
      }
    }
  });
};

/**
 * Показать модальное окно
 */
SchoolApp.components.Modals.show = function(modal, options = {}) {
  const defaultOptions = {
    backdrop: true,
    keyboard: true,
    focus: true,
    show: true,
    centered: false
  };
  
  const config = Object.assign({}, defaultOptions, options);
  
  // Создать фон если нужно
  if (config.backdrop) {
    this.createBackdrop();
  }
  
  // Добавить класс для центрирования
  if (config.centered) {
    modal.classList.add('modal-centered');
  }
  
  // Показать модальное окно
  modal.classList.add('show');
  document.body.classList.add('modal-open');
  
  // Установить ARIA атрибуты
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('role', 'dialog');
  modal.removeAttribute('aria-hidden');
  
  // Сохранить в стек
  this.modalStack.push(modal);
  this.activeModals.add(modal);
  
  // Сфокусироваться на первом поле ввода
  if (config.focus) {
    const firstInput = modal.querySelector('input:not([type="hidden"]), select, textarea, button:not([data-dismiss="modal"])');
    if (firstInput) {
      setTimeout(() => firstInput.focus(), 100);
    }
  }
  
  // Вызвать событие
  modal.dispatchEvent(new Event('modal-show'));
  
  return modal;
};

/**
 * Создать фон для модального окна
 */
SchoolApp.components.Modals.createBackdrop = function() {
  // Удалить существующий фон
  this.removeBackdrop();
  
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop show';
  backdrop.setAttribute('aria-hidden', 'true');
  
  document.body.appendChild(backdrop);
  return backdrop;
};

/**
 * Удалить фон
 */
SchoolApp.components.Modals.removeBackdrop = function() {
  const existingBackdrop = document.querySelector('.modal-backdrop');
  if (existingBackdrop) {
    existingBackdrop.remove();
  }
};

/**
 * Скрыть модальное окно
 */
SchoolApp.components.Modals.hide = function(modal) {
  if (!modal || !modal.classList.contains('show')) {
    return;
  }
  
  // Скрыть модальное окно
  modal.classList.remove('show');
  modal.setAttribute('aria-hidden', 'true');
  modal.removeAttribute('aria-modal');
  
  // Удалить из стека
  const index = this.modalStack.indexOf(modal);
  if (index > -1) {
    this.modalStack.splice(index, 1);
  }
  
  this.activeModals.delete(modal);
  
  // Показать предыдущее модальное окно если есть
  const previousModal = this.getTopModal();
  if (!previousModal) {
    document.body.classList.remove('modal-open');
    this.removeBackdrop();
  } else if (previousModal.getAttribute('data-backdrop') !== 'false') {
    this.createBackdrop();
  }
  
  // Очистить содержимое AJAX модального окна (если нужно)
  if (modal.dataset.clearOnHide === 'true') {
    const modalBody = modal.querySelector('.modal-body');
    if (modalBody) {
      modalBody.innerHTML = '<div class="spinner"></div>';
    }
  }
  
  modal.dispatchEvent(new Event('modal-hide'));
};

/**
 * Получить верхнее модальное окно
 */
SchoolApp.components.Modals.getTopModal = function() {
  return this.modalStack[this.modalStack.length - 1];
};

/**
 * Настройка обработчиков подтверждения
 */
SchoolApp.components.Modals.setupConfirmHandlers = function() {
  document.querySelectorAll('[data-confirm]').forEach(element => {
    element.addEventListener('click', (e) => {
      e.preventDefault();
      
      const message = element.getAttribute('data-confirm') || 'Вы уверены, что хотите выполнить это действие?';
      const confirmTitle = element.getAttribute('data-confirm-title') || 'Подтвердите действие';
      const confirmText = element.getAttribute('data-confirm-text') || 'Подтвердить';
      const cancelText = element.getAttribute('data-cancel-text') || 'Отмена';
      const confirmType = element.getAttribute('data-confirm-type') || 'danger';
      
      this.showConfirm({
        message,
        title: confirmTitle,
        confirmText,
        cancelText,
        confirmType,
        onConfirm: () => {
          // Выполнить действие
          const href = element.getAttribute('href');
          const onclick = element.getAttribute('onclick');
          
          if (href && href !== '#') {
            if (element.target === '_blank') {
              window.open(href, '_blank');
            } else {
              window.location.href = href;
            }
          } else if (onclick) {
            eval(onclick);
          }
        }
      });
    });
  });
};

/**
 * Показать диалог подтверждения
 */
SchoolApp.components.Modals.showConfirm = function(options) {
  const defaults = {
    title: 'Подтвердите действие',
    message: 'Вы уверены, что хотите выполнить это действие?',
    confirmText: 'Подтвердить',
    cancelText: 'Отмена',
    confirmType: 'primary',
    cancelType: 'secondary',
    onConfirm: null,
    onCancel: null,
    centered: true,
    backdrop: true
  };
  
  const config = Object.assign({}, defaults, options);
  
  const modalId = 'confirm-modal-' + Date.now();
  const modalHtml = `
    <div class="modal" id="${modalId}" tabindex="-1" role="dialog">
      <div class="modal-dialog ${config.centered ? 'modal-dialog-centered' : ''}" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">${config.title}</h5>
            <button type="button" class="close-btn" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <p>${config.message}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-${config.cancelType}" data-dismiss="modal">${config.cancelText}</button>
            <button type="button" class="btn btn-${config.confirmType}" id="${modalId}-confirm">${config.confirmText}</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  
  const modal = document.getElementById(modalId);
  const confirmBtn = document.getElementById(modalId + '-confirm');
  
  // Обработчики
  confirmBtn.addEventListener('click', () => {
    if (config.onConfirm && typeof config.onConfirm === 'function') {
      config.onConfirm();
    }
    this.hide(modal);
    modal.remove();
  });
  
  modal.addEventListener('modal-hide', () => {
    if (config.onCancel && typeof config.onCancel === 'function') {
      config.onCancel();
    }
    setTimeout(() => modal.remove(), 100);
  });
  
  // Показать модальное окно
  this.show(modal, {
    backdrop: config.backdrop,
    centered: config.centered
  });
  
  return modal;
};

/**
 * Настройка AJAX модальных окон
 */
SchoolApp.components.Modals.setupAjaxModals = function() {
  document.querySelectorAll('[data-modal-ajax]').forEach(element => {
    element.addEventListener('click', (e) => {
      e.preventDefault();
      
      const url = element.getAttribute('data-modal-ajax') || element.getAttribute('href');
      const targetModal = element.getAttribute('data-modal-target') || '#ajax-modal';
      const modal = document.querySelector(targetModal);
      
      if (modal && url) {
        this.loadModalContent(modal, url);
      }
    });
  });
};

/**
 * Загрузить содержимое модального окна через AJAX
 */
SchoolApp.components.Modals.loadModalContent = function(modal, url) {
  const modalBody = modal.querySelector('.modal-body');
  
  // Показать индикатор загрузки
  if (modalBody) {
    modalBody.innerHTML = '<div class="spinner"></div>';
  }
  
  // Показать модальное окно
  this.show(modal);
  
  // Загрузить содержимое
  SchoolApp.ajax({
    url: url,
    method: 'GET',
    success: function(response) {
      if (modalBody) {
        modalBody.innerHTML = response;
      }
      
      // Вызвать обработчики для нового содержимого
      if (typeof SchoolApp.components.Forms !== 'undefined') {
        SchoolApp.components.Forms.init();
      }
    },
    error: function(error) {
      if (modalBody) {
        modalBody.innerHTML = `
          <div class="alert alert-error">
            <strong>Ошибка!</strong> Не удалось загрузить содержимое. Пожалуйста, попробуйте позже.
          </div>
        `;
      }
    }
  });
};

/**
 * Настройка вспомогательных функций
 */
SchoolApp.components.Modals.setupModalHelpers = function() {
  // Фокусировка на элементе при изменении содержимого
  this.setupModalFocusHandlers();
  
  // Обработка размеров модальных окон
  this.setupModalSizeHandlers();
};

/**
 * Настройка обработчиков фокуса
 */
SchoolApp.components.Modals.setupModalFocusHandlers = function() {
  // Сохранять фокус внутри модального окна
  document.addEventListener('focusin', (e) => {
    const modal = this.getTopModal();
    
    if (modal && modal.hasAttribute('data-trap-focus')) {
      const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      if (!modal.contains(e.target)) {
        const firstElement = focusableElements[0];
        if (firstElement) {
          firstElement.focus();
        }
      }
    }
  });
};

/**
 * Настройка обработчиков размеров
 */
SchoolApp.components.Modals.setupModalSizeHandlers = function() {
  // Обработка модальных окон большого размера
  document.querySelectorAll('.modal-large').forEach(modal => {
    const modalContent = modal.querySelector('.modal-content');
    
    if (modalContent) {
      const maxHeight = window.innerHeight - 100;
      modalContent.style.maxHeight = `${maxHeight}px`;
      modalContent.style.overflowY = 'auto';
    }
  });
  
  // Изменение размера при изменении окна
  window.addEventListener('resize', () => {
    document.querySelectorAll('.modal-large.show').forEach(modal => {
      const modalContent = modal.querySelector('.modal-content');
      
      if (modalContent) {
        const maxHeight = window.innerHeight - 100;
        modalContent.style.maxHeight = `${maxHeight}px`;
      }
    });
  });
};

/**
 * Показать информационное модальное окно
 */
SchoolApp.components.Modals.showInfo = function(title, message, options = {}) {
  const modalId = 'info-modal-' + Date.now();
  
  const modalHtml = `
    <div class="modal modal-info" id="${modalId}" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header modal-header-info">
            <h5 class="modal-title">${title}</h5>
            <button type="button" class="close-btn" data-dismiss="modal">
              <span>&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <p>${message}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  
  const modal = document.getElementById(modalId);
  this.show(modal, options);
  
  return modal;
};

/**
 * Показать ошибку в модальном окне
 */
SchoolApp.components.Modals.showError = function(title, message, options = {}) {
  const modalId = 'error-modal-' + Date.now();
  
  const modalHtml = `
    <div class="modal modal-error" id="${modalId}" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header modal-header-error">
            <h5 class="modal-title">${title || 'Ошибка'}</h5>
            <button type="button" class="close-btn" data-dismiss="modal">
              <span>&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <div class="alert alert-error">${message}</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Закрыть</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  
  const modal = document.getElementById(modalId);
  this.show(modal, options);
  
  return modal;
};

/**
 * Показать успех в модальном окне
 */
SchoolApp.components.Modals.showSuccess = function(title, message, options = {}) {
  options.onConfirm = options.onConfirm || (() => window.location.reload());
  
  const modalId = 'success-modal-' + Date.now();
  
  const modalHtml = `
    <div class="modal modal-success" id="${modalId}" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header modal-header-success">
            <h5 class="modal-title">${title || 'Успех'}</h5>
            <button type="button" class="close-btn" data-dismiss="modal">
              <span>&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <div class="alert alert-success">${message}</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  
  const modal = document.getElementById(modalId);
  this.show(modal, options);
  
  return modal;
};

/**
 * Закрыть все модальные окна
 */
SchoolApp.components.Modals.hideAll = function() {
  this.modalStack.slice().reverse().forEach(modal => {
    this.hide(modal);
  });
};

// Экспорт для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SchoolApp.components.Modals;
}