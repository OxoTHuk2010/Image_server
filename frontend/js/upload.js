const MAX_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_MIMETYPES = ['image/jpeg', 'image/png', 'image/gif'];

let currentUrl = '';

function showStatus(message, type){
    const status = document.getElementById('upload-status')
    if(!status) return;

    status.textContent = message
    status.className = `upload-status ${type}`
    status.style.display = 'block'

    if (type === 'success') {
        setTimeout(() => {
            status.style.display = 'none'
        }, 3000)
    }
}

function validateFile(file){
    if(!ALLOWED_MIMETYPES.includes(file.type)){
        showStatus('Onle .jpg .png and .gif', 'error')
        return false;
    }

    if(file.size > MAX_SIZE){
        showStatus('File too large! Maximum file size is 5 MB.', 'error')
        return false;
    }

    return true;
}

async function handleFile(file){
    if(!file || !validateFile(file)) return;

    showStatus('Uploading....', 'info')

    try{
        const base64 = await fileToBase64(file)
        const success = saveImage(file.name, base64, file.size)

        if(success) {
            showStatus('Upload successful!', 'success')

            const input = document.getElementById('currentUploadInput')
            if(input){
                input.value = base64.substring(0, 50 ) + '...'
                currentUrl = base64
            }
            document.getElementById('fileInput').value = ''
        }
        else{
            showStatus('Upload failed. Please try again', 'error')
        }
    }
    catch(error){
        showStatus('Upload failed. Please try again', 'error')
    }
}

async function copyUrl() {
    if(!currentUrl) return;

    try{
        await navigator.clipboard.writeText(currentUrl)
        showStatus('URL copied', 'success')

        const btn = document.getElementById('copyButton')
        const oldText = btn.textContent
        btn.textContent = 'Copied'
        setTimeout(()=> btn.textContent = oldText, 2000)
    }
    catch{
        showStatus('Failed to copy URL', 'error')
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area')
    const fileInput = document.getElementById('fileInput')
    const browseBtn = document.querySelector('.send_file button')
    const copyBtn = document.getElementById('copyButton')

    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault()
        dropArea.classList.add('dragover')
    })

    dropArea.addEventListener('dragleave', (e) => {
        e.preventDefault()
        dropArea.classList.remove('dragover')
    })

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault()
        dropArea.classList.add('dragover')
        if (e.dataTransfer.files[0]){
            handleFile(e.dataTransfer.files[0])
        }
    })

    fileInput.addEventListener('change', (e) => {
        if(e.target.files[0]){
            handleFile(e.target.files[0])
        }
    })

    browseBtn.addEventListener('click', (e) =>{
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('dragover')
        fileInput.click()
    } )

    if (copyBtn) {
        copyBtn.addEventListener('click', copyUrl)
    }

})