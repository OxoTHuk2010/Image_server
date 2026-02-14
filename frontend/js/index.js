/**
 * @file Скрипт для главной страницы.
 * Управляет фоновым слайд-шоу из случайных изображений.
 */

/**
 * Ссылка на DOM-элемент изображения.
 * @type {HTMLImageElement|null}
 */
const imageEl = document.getElementById('image');

/**
 * ID таймера для `setInterval`, используется для остановки слайд-шоу.
 * @type {number|null}
 */
let timerId = null;

/**
 * Запрашивает у API случайное изображение и плавно устанавливает его как `src`
 * для фонового элемента. Ошибки игнорируются, чтобы не нарушать работу
 * главной страницы, если API недоступен.
 * @async
 */
async function setRandomImage() {
  if (!imageEl) return;

  try {
    const img = await API.random();
    if (!img || !img.url) return;

    // Плавное исчезновение
    imageEl.style.opacity = 0;

    // Установка нового источника и плавное появление после небольшой задержки
    setTimeout(() => {
      imageEl.src = `${img.url}?t=${Date.now()}`; // ?t=... для обхода кэша
      imageEl.style.opacity = 1;
    }, 250); // Задержка соответствует transition в CSS

  } catch (e) {
    // Тихо подавляем ошибку, чтобы главная страница работала,
    // даже если бэкенд временно недоступен.
    console.warn('Не удалось загрузить случайное изображение:', e);
  }
}

/**
 * Запускает или перезапускает цикл слайд-шоу.
 * Немедленно показывает первое изображение, а затем меняет его каждые 5 секунд.
 */
function startSlideShow() {
  if (timerId) {
    clearInterval(timerId);
  }
  setRandomImage(); // Показать первое изображение сразу
  timerId = setInterval(setRandomImage, 5000); // Менять каждые 5 секунд
}

/**
 * Запускает слайд-шоу после полной загрузки DOM.
 */
document.addEventListener('DOMContentLoaded', startSlideShow);
