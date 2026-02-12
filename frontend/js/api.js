// Единая точка работы с backend API (через Nginx это будет тот же домен/порт)
const API = {
  async upload(file) {
    const fd = new FormData();
    fd.append('file', file);
    const res = await fetch('/api/upload', { method: 'POST', body: fd });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Upload failed');
    return data.image;
  },

  async list(page = 1, perPage = 50) {
    const url = `/api/images?page=${encodeURIComponent(page)}&per_page=${encodeURIComponent(perPage)}`;
    const res = await fetch(url);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'List failed');
    return data;
  },

  async remove(id) {
    const res = await fetch(`/api/images/${encodeURIComponent(id)}`, { method: 'DELETE' });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Delete failed');
    return data;
  },

  async random() {
    const res = await fetch('/api/random');
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Random failed');
    return data.image; // может быть null
  }
};
