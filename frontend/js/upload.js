/**
 * @file Скрипт для страницы загрузки изображений.
 * Обеспечивает валидацию, загрузку через API, drag-and-drop и отображение статуса.
 */

/**
 * Максимальный размер файла для загрузки в байтах (5MB).
 * @type {number}
 */
const MAX_SIZE = 5 * 1024 * 1024;

/**
 * Массив разрешенных MIME-типов для загрузки.
 * @type {string[]}
 */
const ALLOWED_MIMETYPES = ['image/jpeg', 'image/png', 'image/gif'];

/**
 * Хранит URL последнего успешно загруженного файла.
 * @type {string}
 */
let currentUrl = '';

/**
 * Отображает статусное сообщение пользователю.
 * @param {string} message - Текст сообщения.
 * @param {'info'|'success'|'error'} type - Тип сообщения, влияющий на стиль.
 */
function showStatus(message, type) {
  const status = document.getElementById('upload-status');
  if (!status) return;

  status.textContent = message;
  status.className = `upload-status ${type}`;
  status.style.display = 'block';

  // Скрывать сообщение об успехе через 3 секунды
  if (type === 'success') {
    setTimeout(() => {
      status.style.display = 'none';
    }, 3000);
  }
}

/**
 * Проверяет файл на соответствие требованиям (MIME-тип и размер).
 * @param {File} file - Файл для валидации.
 * @returns {boolean} `true`, если файл валиден, иначе `false`.
 */
function validateFile(file) {
  if (!ALLOWED_MIMETYPES.includes(file.type)) {
    showStatus('Поддерживаются только JPG/PNG/GIF.', 'error');
    return false;
  }
  if (file.size > MAX_SIZE) {
    showStatus('Файл слишком большой. Максимум 5 MB.', 'error');
    return false;
  }
  return true;
}

/**
 * Обрабатывает выбранный файл: валидирует, загружает и отображает результат.
 * @param {File|null} file - Файл для обработки.
 */
async function handleFile(file) {
  if (!file || !validateFile(file)) {
    return;
  }

  showStatus('Загрузка...', 'info');

  try {
    const image = await API.upload(file);
    currentUrl = image.url;

    const input = document.getElementById('currentUploadInput');
    if (input) input.value = currentUrl;

    const preview = document.getElementById('upload-preview');
    if (preview) {
      // Добавляем timestamp, чтобы обойти кэш браузера для превью
      preview.src = `${currentUrl}?t=${Date.now()}`;
      preview.style.display = 'block';
    }

    showStatus('Загрузка успешна!', 'success');
  } catch (e) {
    showStatus(e.message || 'Ошибка загрузки', 'error');
  }
}

/**
 * Копирует URL последнего загруженного файла в буфер обмена.
 */
function copyCurrentUrl() {
  if (!currentUrl) {
    showStatus('Сначала загрузите файл.', 'info');
    return;
  }
  navigator.clipboard.writeText(window.location.origin + currentUrl).then(
    () => showStatus('Ссылка скопирована в буфер обмена.', 'success'),
    () => showStatus('Не удалось скопировать ссылку.', 'error')
  );
}

/**
 * Инициализирует обработчики событий после полной загрузки DOM.
 * Настраивает:
 * - Кнопку копирования URL.
 * - Поле для выбора файла (`<input type="file">`).
 * - Область для перетаскивания файлов (Drag and Drop).
 */
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('file-input') || document.getElementById('fileInput');
  const dropArea = document.getElementById('drop-area');
  const copyBtn = document.getElementById('copy-url-btn') || document.getElementById('copyButton');

  if (copyBtn) {
    copyBtn.addEventListener('click', copyCurrentUrl);
  }

  if (input) {
    input.addEventListener('change', (e) => {
      const f = e.target.files && e.target.files[0];
      if (f) handleFile(f);
    });
  }

  if (dropArea) {
    // Подсветка области при перетаскивании файла
    ['dragenter', 'dragover'].forEach(evt => {
      dropArea.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.add('dragover');
      });
    });

    // Снятие подсветки
    ['dragleave', 'drop'].forEach(evt => {
      dropArea.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('dragover');
      });
    });

    // Обработка файла при "бросании" в область
    dropArea.addEventListener('drop', (e) => {
      const f = e.dataTransfer.files && e.dataTransfer.files[0];
      if (f) handleFile(f);
    });
  }
});
