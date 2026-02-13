function getFileIcon(filename){
  const ext = (filename.split('.').pop() || '').toLowerCase();
  const icons = {'jpg': '📷', 'png': '📷', 'jpeg': '📷', 'gif': '🎥'};
  return icons[ext] || '🗂️';
}

function openImageInNewTab(url) {
  window.open(url, "_blank");
}

function createImageItem(image){
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

  item.querySelector('.image-url').addEventListener('click', (e) => {
    e.preventDefault();
    openImageInNewTab(image.url);
  });

  item.querySelector('.delete-btn').addEventListener('click', async () => {
    if(!confirm('Удалить изображение?')) return;
    try {
      await API.remove(image.id);
      item.remove();
    } catch (e) {
      alert(e.message || 'Ошибка удаления');
    }
  });

  return item;
}

class PaginationManager {
  constructor() {
    this.currentPage = 1;
    this.itemsPerPage = 50;
    this.totalItems = 0;
    this.maxPerPage = 50;
    this.minPerPage = 10;  // Будет обновлено из backend
  }

  get totalPages() {
    return Math.ceil(this.totalItems / this.itemsPerPage);
  }

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
      this.minPerPage = data.min_per_page || 10; // Получаем минимум из backend

      container.innerHTML = '';
      if (images.length === 0) {
        container.innerHTML = '<div style="padding:12px;">На этой странице нет изображений.</div>';
      } else {
        images.forEach(img => container.appendChild(createImageItem(img)));
      }

      // Обновляем информацию о странице
      pageDisplay.textContent = `Страница ${this.currentPage} из ${this.totalPages}`;
      pageCounter.textContent = `Страница ${this.currentPage} (всего: ${this.totalItems})`;

      // Управляем кнопками
      prevBtn.disabled = this.currentPage === 1;
      nextBtn.disabled = this.currentPage >= this.totalPages;
    } catch (e) {
      container.innerHTML = `<div style="padding:12px;color:#b00;">Ошибка: ${e.message}</div>`;
    }
  }

  setItemsPerPage(count) {
    // Валидируем значение согласно параметрам backend
    if (count < this.minPerPage) count = this.minPerPage;
    if (count > this.maxPerPage) count = this.maxPerPage;
    
    this.itemsPerPage = count;
    this.currentPage = 1;  // Возвращаемся на первую страницу
    this.loadPage();
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadPage();
    }
  }

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadPage();
    }
  }
}

const paginationManager = new PaginationManager();

document.addEventListener('DOMContentLoaded', () => {
  // Загружаем первую страницу
  paginationManager.loadPage();

  // Обработчики для кнопок пагинации
  document.getElementById('next-btn').addEventListener('click', () => paginationManager.nextPage());
  document.getElementById('prev-btn').addEventListener('click', () => paginationManager.prevPage());

  // Обработчик для выбора количества элементов на странице
  document.getElementById('items-select').addEventListener('change', (e) => {
    paginationManager.setItemsPerPage(parseInt(e.target.value));
  });
});
