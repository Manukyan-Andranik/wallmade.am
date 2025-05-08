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