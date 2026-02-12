const MAX_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_MIMETYPES = ['image/jpeg', 'image/png', 'image/gif'];

let currentUrl = '';

function showStatus(message, type){
  const status = document.getElementById('upload-status');
  if(!status) return;

  status.textContent = message;
  status.className = `upload-status ${type}`;
  status.style.display = 'block';

  if (type === 'success') {
    setTimeout(() => status.style.display = 'none', 3000);
  }
}

function validateFile(file){
  if(!ALLOWED_MIMETYPES.includes(file.type)){
    showStatus('Поддерживаются только JPG/PNG/GIF.', 'error');
    return false;
  }
  if(file.size > MAX_SIZE){
    showStatus('Файл слишком большой. Максимум 5 MB.', 'error');
    return false;
  }
  return true;
}

async function handleFile(file){
  if(!file || !validateFile(file)) return;

  showStatus('Загрузка...', 'info');

  try{
    const image = await API.upload(file);
    currentUrl = image.url;

    const input = document.getElementById('currentUploadInput');
    if(input) input.value = currentUrl;

    const preview = document.getElementById('upload-preview');
    if (preview) {
      preview.src = `${currentUrl}?t=${Date.now()}`;
      preview.style.display = 'block';
    }

    showStatus('Загрузка успешна!', 'success');
  } catch (e) {
    showStatus(e.message || 'Ошибка загрузки', 'error');
  }
}

function copyCurrentUrl(){
  if(!currentUrl) return;
  navigator.clipboard.writeText(currentUrl).then(
    () => showStatus('Ссылка скопирована в буфер обмена.', 'success'),
    () => showStatus('Не удалось скопировать ссылку.', 'error')
  );
}

// Drag&Drop + input
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('file-input') || document.getElementById('fileInput');
  const dropArea = document.getElementById('drop-area');
  const copyBtn = document.getElementById('copy-url-btn') || document.getElementById('copyButton');

  if (copyBtn) copyBtn.addEventListener('click', copyCurrentUrl);

  if (input) {
    input.addEventListener('change', (e) => {
      const f = e.target.files && e.target.files[0];
      handleFile(f);
    });
  }

  if (dropArea) {
    ['dragenter','dragover'].forEach(evt => dropArea.addEventListener(evt, (e) => {
      e.preventDefault(); e.stopPropagation();
      dropArea.classList.add('dragover');
    }));
    ['dragleave','drop'].forEach(evt => dropArea.addEventListener(evt, (e) => {
      e.preventDefault(); e.stopPropagation();
      dropArea.classList.remove('dragover');
    }));
    dropArea.addEventListener('drop', (e) => {
      const f = e.dataTransfer.files && e.dataTransfer.files[0];
      handleFile(f);
    });
  }
});
