document.addEventListener('DOMContentLoaded', function() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    const enlargeButtons = document.querySelectorAll('.enlarge-btn');
    const fullscreenOverlay = document.querySelector('.fullscreen-overlay');
    const fullscreenContent = document.querySelector('.fullscreen-content');
    const closeBtn = document.querySelector('.close-btn');
    const fullscreenTitle = document.querySelector('.fullscreen-title');
    const fullscreenCode = document.querySelector('.fullscreen-code');

    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const codeBlock = this.closest('.response-box').querySelector('pre code');
            navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                alert('Copied to clipboard!');
            });
        });
    });

    enlargeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const responseBox = this.closest('.response-box');
            const title = responseBox.querySelector('h2').textContent;
            const codeElement = responseBox.querySelector('pre code');
            const fullText = codeElement.textContent;

            fullscreenTitle.textContent = title;
            fullscreenCode.textContent = fullText;
            fullscreenOverlay.style.display = 'flex';

            setTimeout(() => {
                fullscreenContent.style.opacity = '1';
                fullscreenContent.style.transform = 'scale(1)';
            }, 10);
        });
    });

    closeBtn.addEventListener('click', closeFullscreen);

    fullscreenOverlay.addEventListener('click', function(e) {
        if (e.target === fullscreenOverlay) {
            closeFullscreen();
        }
    });

    function closeFullscreen() {
        fullscreenContent.style.opacity = '0';
        fullscreenContent.style.transform = 'scale(0.9)';
        setTimeout(() => {
            fullscreenOverlay.style.display = 'none';
        }, 300);
    }
});