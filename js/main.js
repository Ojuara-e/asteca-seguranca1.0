// Asteca Segurança - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Header scroll effect
    const header = document.querySelector('.header');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            header.style.background = 'linear-gradient(135deg, rgba(45, 80, 22, 0.95), rgba(74, 124, 89, 0.95))';
            header.style.backdropFilter = 'blur(10px)';
        } else {
            header.style.background = 'linear-gradient(135deg, var(--primary-green), var(--secondary-green))';
            header.style.backdropFilter = 'none';
        }
    });

    // Card hover animations
    const cards = document.querySelectorAll('.card, .offer-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Button click animations
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // WhatsApp click tracking
    const whatsappLinks = document.querySelectorAll('a[href*="wa.me"]');
    whatsappLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Track WhatsApp clicks for analytics
            console.log('WhatsApp link clicked:', this.href);
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for scroll animations
    const animatedElements = document.querySelectorAll('.card, .offer-card, .badge-item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Mobile menu toggle (if needed)
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }

    // Form validation helpers
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function validatePhone(phone) {
        const re = /^[\d\s\-\(\)]+$/;
        return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
    }

    // Accessibility improvements
    document.addEventListener('keydown', function(e) {
        // Skip to main content with Tab key
        if (e.key === 'Tab' && !e.shiftKey && document.activeElement === document.body) {
            const mainContent = document.querySelector('main') || document.querySelector('#inicio');
            if (mainContent) {
                mainContent.focus();
                e.preventDefault();
            }
        }
    });

    // High contrast mode detection
    if (window.matchMedia && window.matchMedia('(prefers-contrast: high)').matches) {
        document.body.classList.add('high-contrast');
    }

    // Reduced motion detection
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.body.classList.add('reduced-motion');
    }

    // Loading state management
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
    });
});

// Gamification functions
const Gamification = {
    // Initialize gamification system
    init: function() {
        this.loadUserProgress();
        this.setupProgressTracking();
    },

    // Load user progress from localStorage
    loadUserProgress: function() {
        const progress = localStorage.getItem('asteca_user_progress');
        if (progress) {
            this.userProgress = JSON.parse(progress);
        } else {
            this.userProgress = {
                completedCourses: [],
                badges: [],
                points: 0,
                level: 1,
                teamRanking: 0
            };
        }
    },

    // Save user progress to localStorage
    saveUserProgress: function() {
        localStorage.setItem('asteca_user_progress', JSON.stringify(this.userProgress));
    },

    // Award badge to user
    awardBadge: function(badgeId, badgeName) {
        if (!this.userProgress.badges.includes(badgeId)) {
            this.userProgress.badges.push(badgeId);
            this.showBadgeNotification(badgeName);
            this.saveUserProgress();
        }
    },

    // Show badge notification
    showBadgeNotification: function(badgeName) {
        const notification = document.createElement('div');
        notification.className = 'badge-notification';
        notification.innerHTML = `
            <div class="badge-notification-content">
                <h4>🏆 Parabéns!</h4>
                <p>Você conquistou o badge: <strong>${badgeName}</strong></p>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    },

    // Add points to user
    addPoints: function(points) {
        this.userProgress.points += points;
        this.checkLevelUp();
        this.saveUserProgress();
    },

    // Check if user leveled up
    checkLevelUp: function() {
        const newLevel = Math.floor(this.userProgress.points / 100) + 1;
        if (newLevel > this.userProgress.level) {
            this.userProgress.level = newLevel;
            this.showLevelUpNotification(newLevel);
        }
    },

    // Show level up notification
    showLevelUpNotification: function(level) {
        const notification = document.createElement('div');
        notification.className = 'level-notification';
        notification.innerHTML = `
            <div class="level-notification-content">
                <h4>🎉 Level Up!</h4>
                <p>Você alcançou o nível <strong>${level}</strong>!</p>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    },

    // Setup progress tracking
    setupProgressTracking: function() {
        // Track course completions
        const courseLinks = document.querySelectorAll('.card a, .offer-card a');
        courseLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.addPoints(10);
            });
        });
    }
};

// Initialize gamification when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    Gamification.init();
});

// CSS for notifications
const notificationStyles = `
    .badge-notification, .level-notification {
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 10000;
        max-width: 300px;
    }
    
    .badge-notification.show, .level-notification.show {
        transform: translateX(0);
    }
    
    .badge-notification-content h4, .level-notification-content h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    
    .badge-notification-content p, .level-notification-content p {
        margin: 0;
        font-size: 0.9rem;
    }
`;

// Add notification styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

