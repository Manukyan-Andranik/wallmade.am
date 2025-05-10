document.addEventListener("DOMContentLoaded", function() {
    const dots = document.querySelectorAll('.nav-dot');
    const prevBtn = document.querySelector('.nav-arrow.left');
    const nextBtn = document.querySelector('.nav-arrow.right');
    let currentIndex = 0;
    let isAnimating = false;
    const animationDuration = 600;


    // Update carousel
    function updateCarousel(newIndex) {
        if (isAnimating) return;
        isAnimating = true;
        
        // Update dots
        dots.forEach(dot => dot.classList.remove('active'));
        dots[newIndex].classList.add('active');
        
        currentIndex = newIndex;
        
        setTimeout(() => {
            isAnimating = false;
        }, animationDuration);
    }

    // Event listeners
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);

    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            const index = parseInt(dot.dataset.index);
            updateCarousel(index);
        });
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') nextSlide();
        if (e.key === 'ArrowLeft') prevSlide();
    });

    // Initialize
    initCarousel();
});


// Initialize AOS animations with smoother settings
document.addEventListener('DOMContentLoaded', function() {
    AOS.init({
        duration: 1000,
        easing: 'ease-in-out-back',
        once: true,
        offset: 120,
        delay: 100,
        mirror: false
    });
});


document.addEventListener('DOMContentLoaded', function() {
    // Initialize scroll animations
    const animateElements = document.querySelectorAll('.animate-text, .product-card, .work-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('aos-animate');
            }
        });
    }, {
        threshold: 0.1
    });

    animateElements.forEach(el => {
        observer.observe(el);
    });

    // Parallax effect for hero background
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.pageYOffset;
            hero.style.backgroundPositionY = scrollPosition * 0.5 + 'px';
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Button hover effects
    const buttons = document.querySelectorAll('.btn-secondary, .btn-primary, .btn-modern');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = this.style.transform.replace('scale(1)', 'scale(1.05)');
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = this.style.transform.replace('scale(1.05)', 'scale(1)');
        });
    });
});