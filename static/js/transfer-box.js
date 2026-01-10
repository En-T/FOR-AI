/**
 * Transfer Box Component
 * Компонент для перемещения элементов между списками
 * Используется для распределения учащихся по подгруппам
 */

SchoolApp.components = SchoolApp.components || {};
SchoolApp.components.TransferBox = {
  instances: new Map()
};

/**
 * Инициализация всех transfer-box компонентов
 */
SchoolApp.components.TransferBox.init = function() {
  document.querySelectorAll('.transfer-box').forEach((element, index) => {
    const instanceId = element.id || `transfer-box-${index}`;
    this.initInstance(instanceId, element);
  });
};

/**
 * Инициализация отдельного экземпляра
 */
SchoolApp.components.TransferBox.initInstance = function(instanceId, element) {
  if (this.instances.has(instanceId)) {
    return this.instances.get(instanceId);
  }

  const instance = {
    id: instanceId,
    element: element,
    sourceList: element.querySelector('.transfer-box-source'),
    targetList: element.querySelector('.transfer-box-target'),
    sourceSearch: element.querySelector('.transfer-box-source-search'),
    targetSearch: element.querySelector('.transfer-box-target-search'),
    sourceItems: new Map(),
    targetItems: new Map(),
    options: {
      allowDuplicates: element.dataset.allowDuplicates === 'true',
      allowReorder: element.dataset.allowReorder !== 'false',
      maxItems: parseInt(element.dataset.maxItems) || Infinity,
      minItems: parseInt(element.dataset.minItems) || 0
    }
  };

  // Инициализация элементов
  this.initItems(instance);
  this.setupEventListeners(instance);
  this.updateButtonStates(instance);
  this.updateCounts(instance);

  this.instances.set(instanceId, instance);
  return instance;
};

/**
 * Инициализация элементов списков
 */
SchoolApp.components.TransferBox.initItems = function(instance) {
  // Очистить карты
  instance.sourceItems.clear();
  instance.targetItems.clear();

  // Инициализировать исходные элементы
  if (instance.sourceList) {
    instance.sourceList.querySelectorAll('.transfer-box-item').forEach(item => {
      const itemId = item.dataset.id;
      instance.sourceItems.set(itemId, {
        element: item,
        id: itemId,
        text: item.textContent.trim(),
        data: JSON.parse(item.dataset.item || '{}')
      });
    });
  }

  // Инициализировать целевые элементы
  if (instance.targetList) {
    instance.targetList.querySelectorAll('.transfer-box-item').forEach(item => {
      const itemId = item.dataset.id;
      instance.targetItems.set(itemId, {
        element: item,
        id: itemId,
        text: item.textContent.trim(),
        data: JSON.parse(item.dataset.item || '{}')
      });
    });
  }
};

/**
 * Установка обработчиков событий
 */
SchoolApp.components.TransferBox.setupEventListeners = function(instance) {
  // Кнопки перемещения
  const moveRightBtn = instance.element.querySelector('.move-right');
  const moveLeftBtn = instance.element.querySelector('.move-left');
  const moveAllRightBtn = instance.element.querySelector('.move-all-right');
  const moveAllLeftBtn = instance.element.querySelector('.move-all-left');
  const sortUpBtn = instance.element.querySelector('.sort-up');
  const sortDownBtn = instance.element.querySelector('.sort-down');

  if (moveRightBtn) {
    moveRightBtn.addEventListener('click', () => this.moveRight(instance));
  }

  if (moveLeftBtn) {
    moveLeftBtn.addEventListener('click', () => this.moveLeft(instance));
  }

  if (moveAllRightBtn) {
    moveAllRightBtn.addEventListener('click', () => this.moveAllRight(instance));
  }

  if (moveAllLeftBtn) {
    moveAllLeftBtn.addEventListener('click', () => this.moveAllLeft(instance));
  }

  if (sortUpBtn) {
    sortUpBtn.addEventListener('click', () => this.moveUp(instance));
  }

  if (sortDownBtn) {
    sortDownBtn.addEventListener('click', () => this.moveDown(instance));
  }

  // Двойной клик на элементы
  if (instance.sourceList) {
    instance.sourceList.addEventListener('dblclick', (e) => {
      const item = e.target.closest('.transfer-box-item');
      if (item) {
        e.preventDefault();
        this.moveItem(instance, item.dataset.id, 'target');
      }
    });
  }

  if (instance.targetList) {
    instance.targetList.addEventListener('dblclick', (e) => {
      const item = e.target.closest('.transfer-box-item');
      if (item) {
        e.preventDefault();
        this.moveItem(instance, item.dataset.id, 'source');
      }
    });
  }

  // Поиск
  if (instance.sourceSearch) {
    instance.sourceSearch.addEventListener('input', 
      SchoolApp.utils.debounce((e) => {
        this.filterList(instance, 'source', e.target.value);
      }, 300)
    );
  }

  if (instance.targetSearch) {
    instance.targetSearch.addEventListener('input', 
      SchoolApp.utils.debounce((e) => {
        this.filterList(instance, 'target', e.target.value);
      }, 300)
    );
  }
};

/**
 * Переместить выбранные элементы вправо (из исходного в целевой)
 */
SchoolApp.components.TransferBox.moveRight = function(instance) {
  const selectedItems = instance.sourceList.querySelectorAll('.transfer-box-item.selected');
  
  selectedItems.forEach(item => {
    this.moveItem(instance, item.dataset.id, 'target');
  });
};

/**
 * Переместить выбранные элементы влево (из целевого в исходный)
 */
SchoolApp.components.TransferBox.moveLeft = function(instance) {
  const selectedItems = instance.targetList.querySelectorAll('.transfer-box-item.selected');
  
  selectedItems.forEach(item => {
    this.moveItem(instance, item.dataset.id, 'source');
  });
};

/**
 * Переместить все элементы вправо
 */
SchoolApp.components.TransferBox.moveAllRight = function(instance) {
  const items = instance.sourceList.querySelectorAll('.transfer-box-item');
  
  items.forEach(item => {
    if (!item.classList.contains('hidden')) {
      this.moveItem(instance, item.dataset.id, 'target');
    }
  });
};

/**
 * Переместить все элементы влево
 */
SchoolApp.components.TransferBox.moveAllLeft = function(instance) {
  const items = instance.targetList.querySelectorAll('.transfer-box-item');
  
  items.forEach(item => {
    if (!item.classList.contains('hidden')) {
      this.moveItem(instance, item.dataset.id, 'source');
    }
  });
};

/**
 * Переместить элемент вверх в целевом списке
 */
SchoolApp.components.TransferBox.moveUp = function(instance) {
  const selectedItem = instance.targetList.querySelector('.transfer-box-item.selected');
  
  if (selectedItem) {
    const previousItem = selectedItem.previousElementSibling;
    
    if (previousItem && !previousItem.classList.contains('hidden')) {
      instance.targetList.insertBefore(selectedItem, previousItem);
      this.updateOrder(instance);
    }
  }
};

/**
 * Переместить элемент вниз в целевом списке
 */
SchoolApp.components.TransferBox.moveDown = function(instance) {
  const selectedItem = instance.targetList.querySelector('.transfer-box-item.selected');
  
  if (selectedItem) {
    const nextItem = selectedItem.nextElementSibling;
    
    if (nextItem && !nextItem.classList.contains('hidden')) {
      instance.targetList.insertBefore(nextItem, selectedItem);
      this.updateOrder(instance);
    }
  }
};

/**
 * Переместить конкретный элемент
 */
SchoolApp.components.TransferBox.moveItem = function(instance, itemId, direction) {
  const item = instance[direction === 'target' ? 'sourceItems' : 'targetItems'].get(itemId);

  if (!item) return false;

  // Проверка ограничений
  if (direction === 'target') {
    if (instance.targetItems.size >= instance.options.maxItems) {
      SchoolApp.showNotification(
        `Максимальное количество элементов: ${instance.options.maxItems}`,
        'warning'
      );
      return false;
    }

    if (!instance.options.allowDuplicates && this.isDuplicate(instance, item.id, direction)) {
      SchoolApp.showNotification(
        'Этот элемент уже находится в целевом списке',
        'warning'
      );
      return false;
    }
  }

  // Удалить из текущего списка
  instance[direction === 'target' ? 'sourceItems' : 'targetItems'].delete(itemId);
  item.element.classList.add(direction === 'target' ? 'moving-right' : 'moving-left');

  // Добавить в новый список
  setTimeout(() => {
    instance[direction === 'target' ? 'targetItems' : 'sourceItems'].set(itemId, item);
    this.updateUI(instance);
    this.updateButtonStates(instance);
    this.updateCounts(instance);
    this.updateOrder(instance);
  }, 150);

  return true;
};

/**
 * Проверить является ли элемент дубликатом
 */
SchoolApp.components.TransferBox.isDuplicate = function(instance, itemId, direction) {
  if (direction === 'target') {
    // Проверка по ID в целевом списке
    if (instance.targetItems.has(itemId)) {
      return true;
    }

    // Проверка по другим идентификаторам (email, student_id, etc.)
    const sourceItem = instance.sourceItems.get(itemId);
    if (sourceItem && sourceItem.data) {
      const checkFields = ['email', 'student_id', 'personal_id', 'username'];
      
      for (let field of checkFields) {
        const value = sourceItem.data[field];
        if (value) {
          const duplicate = Array.from(instance.targetItems.values()).find(item => {
            return item.data && item.data[field] === value;
          });
          
          if (duplicate) return true;
        }
      }
    }
  }

  return false;
};

/**
 * Фильтрация списка
 */
SchoolApp.components.TransferBox.filterList = function(instance, direction, searchTerm) {
  const items = instance[direction === 'source' ? 'sourceItems' : 'targetItems'];
  const list = instance[direction === 'source' ? 'sourceList' : 'targetList'];
  const normalizedSearch = searchTerm.toLowerCase();

  list.querySelectorAll('.transfer-box-item').forEach(item => {
    const text = item.textContent.toLowerCase();
    const shouldShow = !searchTerm || text.includes(normalizedSearch);

    item.classList.toggle('hidden', !shouldShow);
  });

  this.updateButtonStates(instance);
};

/**
 * Обновить UI после изменений
 */
SchoolApp.components.TransferBox.updateUI = function(instance) {
  // Очистить списки
  if (instance.sourceList) {
    instance.sourceList.innerHTML = '';
  }
  if (instance.targetList) {
    instance.targetList.innerHTML = '';
  }

  // Заполнить исходный список
  instance.sourceItems.forEach(item => {
    if (instance.sourceList) {
      instance.sourceList.appendChild(item.element);
      item.element.classList.remove('selected', 'moving-left', 'moving-right');
    }
  });

  // Заполнить целевой список
  instance.targetItems.forEach(item => {
    if (instance.targetList) {
      instance.targetList.appendChild(item.element);
      item.element.classList.remove('selected', 'moving-left', 'moving-right');
    }
  });

  // Обновить обработчики кликов
  this.setupItemClickHandlers(instance);
};

/**
 * Установить обработчики кликов на элементы
 */
SchoolApp.components.TransferBox.setupItemClickHandlers = function(instance) {
  instance.element.querySelectorAll('.transfer-box-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Убрать выделение со всех элементов в этом списке
      item.closest('.transfer-box-list').querySelectorAll('.transfer-box-item').forEach(i => {
        i.classList.remove('selected');
      });
      
      // Выделить текущий элемент
      item.classList.add('selected');
      
      this.updateButtonStates(instance);
    });
  });
};

/**
 * Обновить состояние кнопок
 */
SchoolApp.components.TransferBox.updateButtonStates = function(instance) {
  const sourceSelected = instance.sourceList?.querySelectorAll('.transfer-box-item.selected:not(.hidden)').length || 0;
  const targetSelected = instance.targetList?.querySelectorAll('.transfer-box-item.selected:not(.hidden)').length || 0;
  const sourceVisible = instance.sourceList?.querySelectorAll('.transfer-box-item:not(.hidden)').length || 0;
  const targetVisible = instance.targetList?.querySelectorAll('.transfer-box-item:not(.hidden)').length || 0;

  // Кнопки перемещения
  const moveRightBtn = instance.element.querySelector('.move-right');
  const moveLeftBtn = instance.element.querySelector('.move-left');
  const moveAllRightBtn = instance.element.querySelector('.move-all-right');
  const moveAllLeftBtn = instance.element.querySelector('.move-all-left');
  const sortUpBtn = instance.element.querySelector('.sort-up');
  const sortDownBtn = instance.element.querySelector('.sort-down');

  if (moveRightBtn) {
    moveRightBtn.disabled = sourceSelected === 0;
  }

  if (moveLeftBtn) {
    moveLeftBtn.disabled = targetSelected === 0;
  }

  if (moveAllRightBtn) {
    moveAllRightBtn.disabled = sourceVisible === 0;
  }

  if (moveAllLeftBtn) {
    moveAllLeftBtn.disabled = targetVisible === 0;
  }

  if (sortUpBtn) {
    sortUpBtn.disabled = targetSelected === 0;
  }

  if (sortDownBtn) {
    sortDownBtn.disabled = targetSelected === 0;
  }
};

/**
 * Обновить счетчики элементов
 */
SchoolApp.components.TransferBox.updateCounts = function(instance) {
  const sourceCount = instance.element.querySelector('.source-count');
  const targetCount = instance.element.querySelector('.target-count');

  if (sourceCount) {
    sourceCount.textContent = instance.sourceItems.size;
  }

  if (targetCount) {
    targetCount.textContent = instance.targetItems.size;
  }
};

/**
 * Обновить порядок элементов
 */
SchoolApp.components.TransferBox.updateOrder = function(instance) {
  const items = Array.from(instance.targetList.querySelectorAll('.transfer-box-item'));
  const order = items.map(item => item.dataset.id);
  
  // Вызвать обработчик изменения
  const event = new CustomEvent('transferbox:orderchange', {
    detail: { instance, order }
  });
  
  instance.element.dispatchEvent(event);
  
  // Вызвать callback если он установлен
  if (typeof instance.onOrderChange === 'function') {
    instance.onOrderChange(instance, order);
  }

  // Обновить скрытое поле если оно есть
  const orderField = instance.element.querySelector('.transfer-box-order');
  if (orderField) {
    orderField.value = JSON.stringify(order);
  }
};

/**
 * Получить данные компонента
 */
SchoolApp.components.TransferBox.getData = function(instanceId) {
  const instance = this.instances.get(instanceId);
  
  if (!instance) {
    return null;
  }

  return {
    source: Array.from(instance.sourceItems.values()).map(item => item.data),
    target: Array.from(instance.targetItems.values()).map(item => item.data),
    targetOrder: Array.from(instance.targetItems.keys())
  };
};

/**
 * Проверить валидность
 */
SchoolApp.components.TransferBox.isValid = function(instanceId) {
  const instance = this.instances.get(instanceId);
  
  if (!instance) {
    return false;
  }

  const targetCount = instance.targetItems.size;
  const { minItems, maxItems } = instance.options;

  if (targetCount < minItems) {
    SchoolApp.showNotification(
      `Минимальное количество элементов: ${minItems}`,
      'warning'
    );
    return false;
  }

  if (targetCount > maxItems) {
    SchoolApp.showNotification(
      `Максимальное количество элементов: ${maxItems}`,
      'warning'
    );
    return false;
  }

  return true;
};

/**
 * Сбросить компонент
 */
SchoolApp.components.TransferBox.reset = function(instanceId) {
  const instance = this.instances.get(instanceId);
  
  if (!instance) {
    return false;
  }

  // Вернуть все элементы в исходный список
  instance.targetItems.forEach((item, itemId) => {
    instance.sourceItems.set(itemId, item);
    instance.targetItems.delete(itemId);
  });

  this.updateUI(instance);
  this.updateButtonStates(instance);
  this.updateCounts(instance);
  this.updateOrder(instance);

  return true;
};

// Экспорт для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SchoolApp.components.TransferBox;
}