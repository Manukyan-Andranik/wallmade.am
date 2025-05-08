document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');

    // Toggle mobile menu
    mobileMenuToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        mobileMenuOverlay.classList.toggle('active');
        document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    });

    // Close mobile menu
    mobileMenuClose.addEventListener('click', function() {
        mobileMenuToggle.classList.remove('active');
        mobileMenu.classList.remove('active');
        mobileMenuOverlay.classList.remove('active');
        document.body.style.overflow = '';
    });

    // Close mobile menu when clicking on overlay
    mobileMenuOverlay.addEventListener('click', function() {
        mobileMenuToggle.classList.remove('active');
        mobileMenu.classList.remove('active');
        this.classList.remove('active');
        document.body.style.overflow = '';
    });

    // Close mobile menu when clicking on a link
    const mobileNavLinks = document.querySelectorAll('.mobile-nav a:not(.submenu-toggle a)');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', function() {
            mobileMenuToggle.classList.remove('active');
            mobileMenu.classList.remove('active');
            mobileMenuOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    // Header scroll effect
    const header = document.querySelector('.main-header');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Language switcher as submenu (desktop)
    const languageSwitcher = document.querySelector('.language-switcher-desktop');
    if (languageSwitcher) {
        // Create language submenu structure
        const languageSubmenu = document.createElement('ul');
        languageSubmenu.className = 'submenu language-submenu';
        
        // Get all language links
        const languageLinks = languageSwitcher.querySelectorAll('a');
        
        // Create parent item
        const languageParent = document.createElement('li');
        languageParent.className = 'has-submenu';
        languageParent.innerHTML = `
            <a href="#">
                <span class="current-language">
                    <img src="${languageSwitcher.querySelector('a.active img').src}" 
                         alt="${languageSwitcher.querySelector('a.active img').alt}" 
                         class="flag-icon">
                    ${languageSwitcher.querySelector('a.active').textContent.trim()}
                </span>
                <i class="fas fa-chevron-down"></i>
            </a>
        `;
        
        // Add language options to submenu
        languageLinks.forEach(link => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="${link.href}">
                    <img src="${link.querySelector('img').src}" 
                         alt="${link.querySelector('img').alt}" 
                         class="flag-icon">
                    ${link.textContent.trim()}
                </a>
            `;
            languageSubmenu.appendChild(li);
        });
        
        // Append submenu to parent
        languageParent.appendChild(languageSubmenu);
        
        // Replace original language switcher with new structure
        languageSwitcher.innerHTML = '';
        languageSwitcher.appendChild(languageParent);
    }

    // Mobile submenu toggle (including language switcher)
    const submenuToggles = document.querySelectorAll('.submenu-toggle');
    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            this.classList.toggle('active');
            const submenu = this.nextElementSibling;
            submenu.classList.toggle('active');
            
            // Close other open submenus at the same level
            const parentLi = this.closest('li');
            if (parentLi) {
                const siblings = parentLi.parentElement.querySelectorAll('li');
                siblings.forEach(sibling => {
                    if (sibling !== parentLi) {
                        const otherToggle = sibling.querySelector('.submenu-toggle');
                        const otherSubmenu = sibling.querySelector('.submenu');
                        if (otherToggle) otherToggle.classList.remove('active');
                        if (otherSubmenu) otherSubmenu.classList.remove('active');
                    }
                });
            }
        });
    });

    // Product/Work Image Gallery
    const thumbnails = document.querySelectorAll('.thumbnail-image');
    if (thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                const mainImage = document.getElementById('main-product-image') ||
                    document.getElementById('main-project-image');
                if (mainImage) {
                    mainImage.src = this.dataset.full;
                    mainImage.alt = this.alt;
                }

                // Update active thumbnail
                document.querySelectorAll('.thumbnail').forEach(t => {
                    t.classList.remove('active');
                });
                this.parentElement.classList.add('active');
            });
        });

        // Activate first thumbnail by default
        if (thumbnails[0]) {
            thumbnails[0].click();
        }
    }

    // Filter Functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            const filterValue = this.dataset.filter;
            const items = document.querySelectorAll('.product-card, .portfolio-item');

            items.forEach(item => {
                if (filterValue === 'all' || item.dataset.category === filterValue) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // Animation on Scroll
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-fade, .animate-left, .animate-right');

        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;

            if (elementPosition < windowHeight - 100) {
                element.style.opacity = '1';
                element.style.transform = 'translate(0, 0)';
            }
        });
    };

    // Initial check
    animateOnScroll();

    // Check on scroll
    window.addEventListener('scroll', animateOnScroll);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                mobileMenu.classList.remove('active');
                mobileMenuOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    // Image Zoom on Hover
    const zoomImages = document.querySelectorAll('.zoom-on-hover');
    zoomImages.forEach(img => {
        img.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });

        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Form submission handling
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            // You can add form validation here if needed
            // If validation passes, the form will submit normally
            // If using AJAX, prevent default and handle submission
        });
    });
});