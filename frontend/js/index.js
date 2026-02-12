const image = document.getElementById('image');
let index = 0;
let images = [];
let timerId = null;

function uniq(arr) {
    return Array.from(new Set(arr.filter(Boolean)));
}

function changeImage(){
    if(images.length === 0) return;

    image.style.opacity = 0;
    setTimeout(()=> {
        image.src = images[index];
        image.style.opacity = 1;
        index = (index + 1) % images.length;
    }, 800);
}

function startSlideShow() {
    if (timerId) clearInterval(timerId);
    if(images.length === 0) return;

    if (!images.includes(image.src)) {
        image.src = images[0];
        index = 1 % images.length;
    }
    changeImage();
    timerId = setInterval(changeImage, 5000);
}

async function loadBaseImages() {
    try {
        const res = await fetch('images.json');
        if (!res.ok) throw new Error('Failed to load images.json');
        const data = await res.json();
        return Array.isArray(data) ? data : [];
    } catch {
        return [];
    }
}

async function refreshImagesAndRestart() {
    const base = await loadBaseImages();
    const uploaded = getAllImages().map(img => img.url);

    images = uniq([...base, ...uploaded]);

    if (index >= images.length) index = 0;

    startSlideShow();
}

refreshImagesAndRestart();

window.addEventListener('storage', (e) => {
    if (e.key === 'uploadedImages') {
        refreshImagesAndRestart();
    }
});