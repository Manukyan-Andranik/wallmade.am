document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS animation library
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true
    });

    // Video filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    const videoCards = document.querySelectorAll('.video-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active state of buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const filter = button.dataset.filter;
            
            // Filter videos
            videoCards.forEach(card => {
                if (filter === 'all' || card.dataset.category === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Video modal functionality
    const videoModal = document.querySelector('.video-modal');
    const modalContent = document.querySelector('.modal-content');
    const closeModal = document.querySelector('.close-modal');
    const modalVideo = document.querySelector('.video-modal video');
    const modalTitle = document.querySelector('.modal-title');
    const modalDescription = document.querySelector('.modal-description');
    
    document.querySelectorAll('.play-btn').forEach((btn, index) => {
        btn.addEventListener('click', () => {
            const videoCard = btn.closest('.video-card');
            const videoSrc = videoCard.querySelector('video').querySelector('source').src;
            const videoPoster = videoCard.querySelector('video').poster;
            const title = videoCard.querySelector('h3').textContent;
            const description = videoCard.querySelector('p').textContent;
            
            // Set modal content
            modalVideo.querySelector('source').src = videoSrc;
            modalVideo.poster = videoPoster;
            modalVideo.load();
            modalTitle.textContent = title;
            modalDescription.textContent = description;
            
            // Show modal
            videoModal.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Play video
            setTimeout(() => {
                modalVideo.play();
            }, 300);
        });
    });
    
    // Close modal
    closeModal.addEventListener('click', () => {
        videoModal.classList.remove('active');
        document.body.style.overflow = 'auto';
        modalVideo.pause();
    });
    
    // Close modal when clicking outside
    videoModal.addEventListener('click', (e) => {
        if (!modalContent.contains(e.target)) {
            videoModal.classList.remove('active');
            document.body.style.overflow = 'auto';
            modalVideo.pause();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && videoModal.classList.contains('active')) {
            videoModal.classList.remove('active');
            document.body.style.overflow = 'auto';
            modalVideo.pause();
        }
    });
    
    // Pause all videos when scrolling to save resources
    window.addEventListener('scroll', function() {
        document.querySelectorAll('.video-thumbnail').forEach(video => {
            if (isElementInViewport(video)) {
                // Video is in viewport
            } else {
                // Video is not in viewport, pause it
                video.pause();
            }
        });
    });
    
    // Helper function to check if element is in viewport
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
});