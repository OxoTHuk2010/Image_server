const imageEl = document.getElementById('image');
let timerId = null;

async function setRandomImage(){
  try{
    const img = await API.random();
    if(!img || !img.url) return;
    imageEl.style.opacity = 0;
    setTimeout(() => {
      imageEl.src = `${img.url}?t=${Date.now()}`;
      imageEl.style.opacity = 1;
    }, 250);
  } catch (e) {
    // тихо — главная страница должна жить даже если бэкенд временно недоступен
    console.warn('random failed', e);
  }
}

function startSlideShow(){
  if(timerId) clearInterval(timerId);
  setRandomImage();
  timerId = setInterval(setRandomImage, 5000);
}

document.addEventListener('DOMContentLoaded', startSlideShow);
