/**
 * @file Единый модуль для взаимодействия с backend API.
 * Оборачивает `fetch` для всех эндпоинтов приложения.
 */

/**
 * @namespace API
 * @description Объект, предоставляющий методы для работы с API сервера изображений.
 */
const API = {
  /**
   * Загружает файл на сервер.
   * @param {File} file - Файл изображения для загрузки.
   * @returns {Promise<object>} Объект с данными загруженного изображения.
   * @throws {Error} Если загрузка не удалась или сервер вернул ошибку.
   */
  async upload(file) {
    const fd = new FormData();
    fd.append('file', file);

    const res = await fetch('/api/upload', { method: 'POST', body: fd });
    const data = await res.json().catch(() => ({})); // Обработка случая, если ответ не JSON

    if (!res.ok) {
      throw new Error(data.error || 'Не удалось загрузить файл');
    }
    return data.image;
  },

  /**
   * Получает постраничный список изображений.
   * @param {number} [page=1] - Номер запрашиваемой страницы.
   * @param {number} [perPage=50] - Количество изображений на странице.
   * @returns {Promise<object>} Объект ответа API, содержащий массив изображений и метаданные пагинации.
   * @throws {Error} Если не удалось получить список.
   */
  async list(page = 1, perPage = 50) {
    const url = `/api/images?page=${encodeURIComponent(page)}&per_page=${encodeURIComponent(perPage)}`;
    const res = await fetch(url);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data.error || 'Не удалось получить список изображений');
    }
    return data;
  },

  /**
   * Удаляет изображение по его ID.
   * @param {number|string} id - ID изображения для удаления.
   * @returns {Promise<object>} Объект ответа API с подтверждением успеха.
   * @throws {Error} Если удаление не удалось.
   */
  async remove(id) {
    const res = await fetch(`/api/images/${encodeURIComponent(id)}`, { method: 'DELETE' });
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data.error || 'Не удалось удалить изображение');
    }
    return data;
  },

  /**
   * Запрашивает одно случайное изображение.
   * @returns {Promise<object|null>} Объект изображения или `null`, если изображений нет.
   * @throws {Error} Если запрос не удался.
   */
  async random() {
    const res = await fetch('/api/random');
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data.error || 'Не удалось получить случайное изображение');
    }
    return data.image;
  }
};
