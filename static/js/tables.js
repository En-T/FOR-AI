/**
 * Интерактивные таблицы
 * Сортировка, фильтрация, выделение строк, пагинация
 */

SchoolApp.components = SchoolApp.components || {};
SchoolApp.components.Tables = {
  tables: new Map(),
  state: new Map()
};

/**
 * Инициализация таблиц
 */
SchoolApp.components.Tables.init = function() {
  this.initTableHeaders();
  this.initTableSearch();
  this.initTableFilters();
  this.initTablePagination();
  this.initTableActions();
  this.initTableCardView();
};

/**
 * Инициализация заголовков таблиц (сортировка)
 */
SchoolApp.components.Tables.initTableHeaders = function() {
  document.querySelectorAll('.table th[data-sortable]').forEach(header => {
    header.addEventListener('click', (e) => {
      const table = header.closest('.table');
      const columnIndex = Array.from(header.parentNode.children).indexOf(header);
      const sortDir = header.classList.contains('sort-asc') ? 'desc' : 'asc';
      
      this.sortTable(table, columnIndex, sortDir);
      this.updateSortIndicators(header, sortDir);
    });
    
    // Обновить курсор
    header.style.cursor = 'pointer';
    header.title = 'Нажмите для сортировки';
  });
};

/**
 * Сортировка таблицы
 */
SchoolApp.components.Tables.sortTable = function(table, columnIndex, sortDir = 'asc') {
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const headerCell = table.querySelectorAll('th')[columnIndex];
  
  // Получить тип данных для сортировки
  const dataType = headerCell.getAttribute('data-type') || 'string';
  
  rows.sort((a, b) => {
    const aValue = this.getCellValue(a, columnIndex);
    const bValue = this.getCellValue(b, columnIndex);
    
    let comparison = 0;
    
    switch (dataType) {
      case 'number':
        const aNum = parseFloat(aValue.replace(/[^\d.-]/g, '')) || 0;
        const bNum = parseFloat(bValue.replace(/[^\d.-]/g, '')) || 0;
        comparison = aNum - bNum;
        break;
        
      case 'date':
        const aDate = this.parseDate(aValue);
        const bDate = this.parseDate(bValue);
        comparison = aDate.getTime() - bDate.getTime();
        break;
        
      case 'status':
        const statusOrder = { 'active': 0, 'pending': 1, 'inactive': 2 };
        const aStatus = statusOrder[aValue.toLowerCase()] || 99;
        const bStatus = statusOrder[bValue.toLowerCase()] || 99;
        comparison = aStatus - bStatus;
        break;
        
      default: // string
        comparison = aValue.toLowerCase().localeCompare(bValue.toLowerCase());
    }
    
    return sortDir === 'asc' ? comparison : -comparison;
  });
  
  // Переставить строки
  rows.forEach(row => tbody.appendChild(row));
};

/**
 * Получить значение ячейки
 */
SchoolApp.components.Tables.getCellValue = function(row, columnIndex) {
  const cell = row.cells[columnIndex];
  if (!cell) return '';
  
  // Проверить data-value атрибут
  if (cell.hasAttribute('data-value')) {
    return cell.getAttribute('data-value');
  }
  
  // Получить текстовое значение
  let value = cell.textContent.trim() || cell.innerText.trim();
  
  // Получить значение из input/select если есть
  const input = cell.querySelector('input, select, textarea');
  if (input) {
    value = input.value;
  }
  
  return value;
};

/**
 * Разбор даты
 */
SchoolApp.components.Tables.parseDate = function(dateString) {
  // Принимает форматы: DD.MM.YYYY, YYYY-MM-DD, DD/MM/YYYY
  let parts = dateString.match(/(\d+)/g);
  if (!parts) return new Date(0);
  
  if (dateString.includes('/')) {
    return new Date(parts[2], parts[1] - 1, parts[0]);
  } else if (dateString.includes('-')) {
    return new Date(parts[0], parts[1] - 1, parts[2]);
  } else {
    return new Date(parts[2], parts[1] - 1, parts[0]);
  }
};

/**
 * Обновить индикаторы сортировки
 */
SchoolApp.components.Tables.updateSortIndicators = function(sortedHeader, sortDir) {
  // Удалить все индикаторы
  const table = sortedHeader.closest('.table');
  table.querySelectorAll('th').forEach(th => {
    th.classList.remove('sort-asc', 'sort-desc');
  });
  
  // Установить индикатор на выбранный столбец
  sortedHeader.classList.add(sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
  
  // Установить ARIA атрибуты
  table.setAttribute('aria-sort', sortDir === 'asc' ? 'ascending' : 'descending');
};

/**
 * Инициализация поиска в таблицах
 */
SchoolApp.components.Tables.initTableSearch = function() {
  document.querySelectorAll('.table-search-input').forEach(input => {
    const targetTableId = input.getAttribute('data-table');
    const table = document.getElementById(targetTableId) || input.closest('.table-container').querySelector('.table');
    
    if (table) {
      input.addEventListener('input', SchoolApp.utils.debounce((e) => {
        this.searchTable(table, e.target.value);
        this.updatePagination(table);
      }, 300));
    }
  });
};

/**
 * Поиск в таблице
 */
SchoolApp.components.Tables.searchTable = function(table, searchTerm) {
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  const rows = tbody.querySelectorAll('tr');
  const normalizedSearch = searchTerm.toLowerCase().trim();
  
  rows.forEach(row => {
    let found = false;
    
    // Искать в каждой ячейке
    for (let cell of row.cells) {
      const cellText = cell.textContent.toLowerCase() || cell.innerText.toLowerCase();
      const cellValue = cell.getAttribute('data-value') || '';
      
      if (cellText.includes(normalizedSearch) || cellValue.toLowerCase().includes(normalizedSearch)) {
        found = true;
        break;
      }
    }
    
    // Показать/скрыть строку
    row.style.display = found ? '' : 'none';
  });
  
  // Обновить заголовок результатов
  this.updateResultsCount(table);
};

/**
 * Обновить счетчик результатов
 */
SchoolApp.components.Tables.updateResultsCount = function(table) {
  const visibleRows = table.querySelectorAll('tbody tr:not([style*="display: none"])').length;
  const totalRows = table.querySelectorAll('tbody tr').length;
  
  const countElement = table.closest('.table-container').querySelector('.table-results-count');
  if (countElement) {
    countElement.textContent = `Показано ${visibleRows} из ${totalRows}`;
  }
};

/**
 * Инициализация фильтров таблицы
 */
SchoolApp.components.Tables.initTableFilters = function() {
  document.querySelectorAll('.table-filter').forEach(filter => {
    const targetTableId = filter.getAttribute('data-table');
    const filterColumn = filter.getAttribute('data-column');
    const table = document.getElementById(targetTableId) || filter.closest('.table-container').querySelector('.table');
    
    if (table && filterColumn) {
      filter.addEventListener('change', (e) => {
        this.filterTable(table, filterColumn, e.target.value);
        this.updatePagination(table);
      });
    }
  });
};

/**
 * Фильтрация таблицы
 */
SchoolApp.components.Tables.filterTable = function(table, columnIndex, filterValue) {
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  const rows = tbody.querySelectorAll('tr');
  
  rows.forEach(row => {
    const cell = row.cells[columnIndex];
    if (!cell) return;
    
    const cellValue = this.getCellValue(row, parseInt(columnIndex));
    let show = true;
    
    if (filterValue && filterValue !== 'all') {
      const normalizedFilter = filterValue.toLowerCase();
      const normalizedValue = cellValue.toLowerCase();
      
      if (normalizedFilter === 'not-empty') {
        show = normalizedValue.trim() !== '';
      } else if (cell.hasAttribute('data-filter-type') && cell.getAttribute('data-filter-type') === 'range') {
        // Фильтр по диапазону
        const [min, max] = normalizedFilter.split('-');
        const numValue = parseFloat(normalizedValue) || 0;
        show = numValue >= parseFloat(min) && numValue <= parseFloat(max);
      } else {
        show = normalizedValue.includes(normalizedFilter);
      }
    }
    
    row.style.display = show ? '' : 'none';
  });
  
  this.updateResultsCount(table);
};

/**
 * Инициализация пагинации
 */
SchoolApp.components.Tables.initTablePagination = function() {
  document.querySelectorAll('.table-container[data-pagination="true"]').forEach(container => {
    const table = container.querySelector('.table');
    const rowsPerPage = parseInt(container.dataset.rowsPerPage || '10');
    
    this.setupPagination(table, rowsPerPage);
  });
};

/**
 * Настройка пагинации для таблицы
 */
SchoolApp.components.Tables.setupPagination = function(table, rowsPerPage = 10, currentPage = 1) {
  const container = table.closest('.table-container');
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  const allRows = Array.from(tbody.querySelectorAll('tr'));
  const totalRows = allRows.length;
  const totalPages = Math.ceil(totalRows / rowsPerPage);
  
  // Сохранить состояние
  const tableId = table.id || 'table-' + Date.now();
  this.state.set(tableId, {
    currentPage,
    rowsPerPage,
    totalRows,
    totalPages
  });
  
  // Показать нужные строки
  const startIndex = (currentPage - 1) * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  
  allRows.forEach((row, index) => {
    if (index >= startIndex && index < endIndex) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
  
  // Обновить видимость строк до применения поиска/фильтров
  this.applyCurrentFilters(table);
};

/**
 * Применить текущие фильтры и поиск
 */
SchoolApp.components.Tables.applyCurrentFilters = function(table) {
  const container = table.closest('.table-container');
  
  // Применить поиск
  const searchInput = container.querySelector('.table-search-input');
  if (searchInput && searchInput.value) {
    this.searchTable(table, searchInput.value);
  }
  
  // Применить фильтры
  container.querySelectorAll('.table-filter').forEach(filter => {
    if (filter.value) {
      const columnIndex = filter.getAttribute('data-column');
      this.filterTable(table, columnIndex, filter.value);
    }
  });
};

/**
 * Обновить пагинацию
 */
SchoolApp.components.Tables.updatePagination = function(table) {
  const container = table.closest('.table-container');
  const tableId = table.id || 'table-' + Date.now();
  const state = this.state.get(tableId) || { currentPage: 1, rowsPerPage: 10 };
  
  // Подсчитать видимые строки после фильтрации
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  const visibleRows = tbody.querySelectorAll('tr:not([style*="display: none"])');
  const totalVisible = visibleRows.length;
  const totalPages = Math.ceil(totalVisible / state.rowsPerPage);
  
  // Обновить состояние
  state.totalRows = totalVisible;
  state.totalPages = totalPages;
  
  // Показать нужные строки
  const startIndex = (state.currentPage - 1) * state.rowsPerPage;
  const endIndex = startIndex + state.rowsPerPage;
  
  visibleRows.forEach((row, index) => {
    if (index >= startIndex && index < endIndex) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
  
  // Обновить элементы управления
  this.renderPaginationControls(table, state);
  this.updateResultsCount(table);
};

/**
 * Отрендерить элементы управления пагинацией
 */
SchoolApp.components.Tables.renderPaginationControls = function(table, state) {
  const container = table.closest('.table-container');
  const controlsContainer = container.querySelector('.pagination');
  
  if (!controlsContainer) return;
  
  const { currentPage, totalPages } = state;
  
  let html = '';
  
  // Кнопка "Предыдущая"
  html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
    <a href="#" class="page-link" data-page="${currentPage - 1}">‹</a>
  </li>`;
  
  // Номера страниц
  const maxPages = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
  let endPage = Math.min(totalPages, startPage + maxPages - 1);
  
  if (endPage - startPage < maxPages - 1) {
    startPage = Math.max(1, endPage - maxPages + 1);
  }
  
  for (let i = startPage; i <= endPage; i++) {
    html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
      <a href="#" class="page-link" data-page="${i}">${i}</a>
    </li>`;
  }
  
  // Кнопка "Следующая"
  html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
    <a href="#" class="page-link" data-page="${currentPage + 1}">›</a>
  </li>`;
  
  controlsContainer.innerHTML = html;
  
  // Добавить обработчики
  controlsContainer.querySelectorAll('.page-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const page = parseInt(e.target.getAttribute('data-page'));
      this.goToPage(table, page);
    });
  });
};

/**
 * Переход на страницу
 */
SchoolApp.components.Tables.goToPage = function(table, page) {
  const tableId = table.id || 'table-' + Date.now();
  const state = this.state.get(tableId);
  
  if (state && page >= 1 && page <= state.totalPages) {
    state.currentPage = page;
    this.setupPagination(table, state.rowsPerPage, page);
  }
};

/**
 * Инициализация действий в таблице
 */
SchoolApp.components.Tables.initTableActions = function() {
  // Выбор строк
  document.querySelectorAll('.table-selectable tbody tr').forEach(row => {
    row.addEventListener('click', (e) => {
      // Игнорировать клик на кнопки действий
      if (e.target.closest('.table-action-btn, .table-actions')) {
        return;
      }
      
      this.selectRow(row, !row.classList.contains('selected'));
    });
  });
  
  // Обработчики действий
  this.setupActionHandlers();
};

/**
 * Выбор строки
 */
SchoolApp.components.Tables.selectRow = function(row, select) {
  const isSingleSelect = row.closest('.table').classList.contains('table-single-select');
  
  if (isSingleSelect) {
    // Удалить выделение у всех строк
    row.parentNode.querySelectorAll('tr.selected').forEach(r => {
      r.classList.remove('selected');
    });
  }
  
  if (select) {
    row.classList.add('selected');
    row.setAttribute('aria-selected', 'true');
  } else {
    row.classList.remove('selected');
    row.removeAttribute('aria-selected');
  }
  
  // Обработать выбор
  this.handleRowSelection(row, select);
};

/**
 * Обработка выбора строки
 */
SchoolApp.components.Tables.handleRowSelection = function(row, selected) {
  const table = row.closest('.table');
  const selectedRows = table.querySelectorAll('tr.selected');
  
  // Обновить кнопки bulk действий
  const bulkActions = table.closest('.table-container').querySelector('.table-bulk-actions');
  if (bulkActions) {
    bulkActions.style.display = selectedRows.length > 0 ? 'block' : 'none';
  }
  
  // Вызвать кастомный обработчик
  const tableId = table.id || 'table-' + Date.now();
  if (typeof window[`onTableRowSelect_${tableId}`] === 'function') {
    window[`onTableRowSelect_${tableId}`](row, selected, Array.from(selectedRows));
  }
};

/**
 * Установить обработчик действий
 */
SchoolApp.components.Tables.setupActionHandlers = function() {
  document.querySelectorAll('.table-container').forEach(container => {
    const table = container.querySelector('.table');
    const tableId = table.id || 'table-' + Date.now();
    
    // Редактировать
    container.querySelectorAll('.btn-edit').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const row = e.target.closest('tr');
        
        if (typeof window[`onTableEdit_${tableId}`] === 'function') {
          window[`onTableEdit_${tableId}`](row);
        }
      });
    });
    
    // Удалить
    container.querySelectorAll('.btn-delete').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const row = e.target.closest('tr');
        const shouldDelete = confirm('Вы уверены, что хотите удалить эту запись?');
        
        if (shouldDelete && typeof window[`onTableDelete_${tableId}`] === 'function') {
          window[`onTableDelete_${tableId}`](row);
        }
      });
    });
  });
};

/**
 * Инициализация карточного представления для мобильных
 */
SchoolApp.components.Tables.initTableCardView = function() {
  const checkCardView = () => {
    const width = window.innerWidth;
    document.querySelectorAll('.table-container').forEach(container => {
      const table = container.querySelector('.table');
      
      if (width <= 768) {
        this.renderCardView(table);
      } else {
        this.hideCardView(container);
      }
    });
  };
  
  checkCardView();
  
  // Проверить при изменении размера
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(checkCardView, 250);
  });
};

/**
 * Отрендерить карточное представление
 */
SchoolApp.components.Tables.renderCardView = function(table) {
  const container = table.closest('.table-container');
  let cardsContainer = container.querySelector('.table-cards');
  
  if (!cardsContainer) {
    cardsContainer = document.createElement('div');
    cardsContainer.className = 'table-cards';
    container.appendChild(cardsContainer);
  }
  
  const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
  const tbody = table.querySelector('tbody');
  
  // Генерировать карточки
  let cardsHtml = '';
  tbody.querySelectorAll('tr:not([style*="display: none"])').forEach(row => {
    cardsHtml += '<div class="table-card">';
    
    Array.from(row.cells).forEach((cell, index) => {
      if (headers[index]) {
        const label = headers[index];
        const value = cell.innerHTML;
        cardsHtml += `
          <div class="table-card-row">
            <span class="table-card-label">${label}:</span>
            <span class="table-card-value">${value}</span>
          </div>
        `;
      }
    });
    
    // Добавить действия
    const actions = row.querySelector('.table-actions');
    if (actions) {
      cardsHtml += `<div class="table-card-actions">${actions.innerHTML}</div>`;
    }
    
    cardsHtml += '</div>';
  });
  
  cardsContainer.innerHTML = cardsHtml;
  
  // Скрыть обычную таблицу
  table.style.display = 'none';
};

/**
 * Скрыть карточное представление
 */
SchoolApp.components.Tables.hideCardView = function(container) {
  const table = container.querySelector('.table');
  const cardsContainer = container.querySelector('.table-cards');
  
  if (table) {
    table.style.display = '';
  }
  
  if (cardsContainer) {
    cardsContainer.remove();
  }
};

/**
 * Экспорт таблицы в CSV
 */
SchoolApp.components.Tables.exportToCSV = function(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;
  
  let csv = '';
  
  // Заголовки
  const headers = Array.from(table.querySelectorAll('thead th')).map(th => 
    '"' + th.textContent.replace(/"/g, '""') + '"'
  ).join(',');
  csv += headers + '\n';
  
  // Данные
  const rows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
  rows.forEach(row => {
    const cells = Array.from(row.cells).map(cell => 
      '"' + cell.textContent.trim().replace(/"/g, '""') + '"'
    ).join(',');
    csv += cells + '\n';
  });
  
  // Скачать файл
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `export_${tableId}_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
};

// Экспорт для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SchoolApp.components.Tables;
}