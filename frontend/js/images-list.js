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

async function loadImages(){
  const container = document.getElementById('images-list');
  if(!container) return;

  container.innerHTML = '';
  try {
    const data = await API.list(1, 200);
    const images = data.images || [];
    if(images.length === 0){
      container.innerHTML = '<div style="padding:12px;">Пока нет загруженных изображений.</div>';
      return;
    }
    images.forEach(img => container.appendChild(createImageItem(img)));
  } catch(e) {
    container.innerHTML = `<div style="padding:12px;color:#b00;">Ошибка: ${e.message}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', loadImages);
