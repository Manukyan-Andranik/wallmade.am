document.addEventListener('DOMContentLoaded', function () {
    // Initialize AOS animations
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        offset: 120,
        delay: 100,
        mirror: false
    });

    // Function to check for iOS devices
    function isIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) ||
            (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    }

    // Adjust background elements for iOS
    console.log(isIOS());
    if (isIOS()) {
        const heroBg = document.querySelector('.hero-background');

        // Ensure backgrounds are fixed
        if (heroBg) {
            heroBg.style.position = 'fixed';
            heroBg.style.top = '0';
            heroBg.style.left = '0';
        }
    }
    else {
        // For non-iOS: add ::before via class
        const hero = document.querySelector('.hero');
        const heroBg = document.querySelector('.hero-background');

        if (hero) {
            hero.classList.add('use-before');
            heroBg.classList.remove('hero-background');

        }
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Button hover effects
    const buttons = document.querySelectorAll('.btn-secondary, .btn-primary, .btn-modern');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-3px) scale(1.05)';
            this.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.15)';
        });

        button.addEventListener('mouseleave', function () {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });

    // Intersection Observer for scroll animations
    const animateElements = document.querySelectorAll('.animate-text, .product-card, .work-card');

    if (animateElements.length) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('aos-animate');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animateElements.forEach(el => {
            observer.observe(el);
        });
    }

    // Video player functionality
    const playButtons = document.querySelectorAll('.play-button');
    playButtons.forEach(button => {
        button.addEventListener('click', function () {
            const videoContainer = this.closest('.video-container');
            const video = videoContainer.querySelector('video');

            if (video.paused) {
                video.play()
                    .then(() => {
                        this.innerHTML = '<i class="fas fa-pause"></i>';
                        videoContainer.classList.add('playing');
                    })
                    .catch(error => {
                        console.error('Video playback failed:', error);
                    });
            } else {
                video.pause();
                this.innerHTML = '<i class="fas fa-play"></i>';
                videoContainer.classList.remove('playing');
            }
        });
    });
});
