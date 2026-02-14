/**
 * @file Скрипт для страницы со списком изображений.
 * Управляет отображением списка, пагинацией и удалением изображений.
 */

/**
 * Возвращает иконку в зависимости от расширения файла.
 * @param {string} filename - Имя файла.
 * @returns {string} Строка с emoji-иконкой.
 */
function getFileIcon(filename) {
  const ext = (filename.split('.').pop() || '').toLowerCase();
  const icons = { 'jpg': '📷', 'png': '📷', 'jpeg': '📷', 'gif': '🎥' };
  return icons[ext] || '🗂️';
}

/**
 * Открывает URL в новой вкладке.
 * @param {string} url - URL для открытия.
 */
function openImageInNewTab(url) {
  window.open(url, "_blank");
}

/**
 * Создает DOM-элемент для одного изображения в списке.
 * @param {object} image - Объект изображения из API.
 * @property {number} image.id - ID изображения.
 * @property {string} image.url - URL изображения.
 * @property {string} image.filename - Уникальное имя файла на сервере.
 * @property {string} image.original_name - Оригинальное имя файла.
 * @returns {HTMLElement} Готовый DOM-элемент.
 */
function createImageItem(image) {
  const item = document.createElement('div');
  item.className = 'image-item';
  item.dataset.id = image.id;

  const shortUrl = (image.url || '').length > 60 ? (image.url.substring(0, 60) + '...') : image.url;
  const icon = getFileIcon(image.filename || image.original_name);

  item.innerHTML = `
    <div class='image-name'>
      <div class='image-icon'>${icon}</div>
      <span title="${image.original_name || image.filename}">${image.original_name || image.filename}</span>
    </div>
    <div class="image-url-wrapper">
      <a href="#" class="image-url" title="${image.url}">${shortUrl}</a>
    </div>
    <div class="image-delete">
      <button class="delete-btn" title="Удалить">✖</button>
    </div>
  `;

  // Обработчик для открытия полного изображения
  item.querySelector('.image-url').addEventListener('click', (e) => {
    e.preventDefault();
    openImageInNewTab(image.url);
  });

  // Обработчик для кнопки удаления
  item.querySelector('.delete-btn').addEventListener('click', async () => {
    if (!confirm('Вы уверены, что хотите удалить это изображение?')) return;
    try {
      await API.remove(image.id);
      item.remove(); // Удаляем элемент из DOM
    } catch (e) {
      alert(e.message || 'Ошибка удаления');
    }
  });

  return item;
}

/**
 * @class PaginationManager
 * @description Управляет состоянием пагинации и взаимодействием с API для загрузки страниц.
 */
class PaginationManager {
  /**
   * @constructor
   */
  constructor() {
    /** @type {number} */
    this.currentPage = 1;
    /** @type {number} */
    this.itemsPerPage = 50;
    /** @type {number} */
    this.totalItems = 0;
    /** @type {number} */
    this.maxPerPage = 50;
    /** @type {number} */
    this.minPerPage = 10;
  }

  /**
   * Рассчитывает общее количество страниц.
   * @type {number}
   * @readonly
   */
  get totalPages() {
    if (this.totalItems === 0) return 1;
    return Math.ceil(this.totalItems / this.itemsPerPage);
  }

  /**
   * Загружает и отображает данные для текущей страницы.
   * @async
   */
  async loadPage() {
    const container = document.getElementById('images-list');
    const pageDisplay = document.getElementById('page-display');
    const pageCounter = document.getElementById('page-counter');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    try {
      const data = await API.list(this.currentPage, this.itemsPerPage);
      const images = data.images || [];
      this.totalItems = data.total || 0;
      this.maxPerPage = data.max_per_page || 50;
      this.minPerPage = data.min_per_page || 10;

      container.innerHTML = '';
      if (images.length === 0) {
        container.innerHTML = '<div class="empty-list-message">На этой странице нет изображений.</div>';
      } else {
        images.forEach(img => container.appendChild(createImageItem(img)));
      }

      pageDisplay.textContent = `Страница ${this.currentPage} из ${this.totalPages}`;
      pageCounter.textContent = `Показано ${images.length} из ${this.totalItems}`;

      prevBtn.disabled = this.currentPage === 1;
      nextBtn.disabled = this.currentPage >= this.totalPages;
    } catch (e) {
      container.innerHTML = `<div class="error-message">Ошибка: ${e.message}</div>`;
    }
  }

  /**
   * Устанавливает новое количество элементов на странице и перезагружает данные.
   * @param {number} count - Новое количество элементов.
   */
  setItemsPerPage(count) {
    const validCount = Math.max(this.minPerPage, Math.min(count, this.maxPerPage));
    this.itemsPerPage = validCount;
    this.currentPage = 1; // Сбрасываем на первую страницу
    this.loadPage();
  }

  /**
   * Переключается на следующую страницу.
   */
  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadPage();
    }
  }

  /**
   * Переключается на предыдущую страницу.
   */
  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadPage();
    }
  }
}

const paginationManager = new PaginationManager();

/**
 * Инициализирует пагинацию и обработчики событий после загрузки DOM.
 */
document.addEventListener('DOMContentLoaded', () => {
  paginationManager.loadPage();

  document.getElementById('next-btn').addEventListener('click', () => paginationManager.nextPage());
  document.getElementById('prev-btn').addEventListener('click', () => paginationManager.prevPage());
  document.getElementById('items-select').addEventListener('change', (e) => {
    paginationManager.setItemsPerPage(parseInt(e.target.value, 10));
  });
});
