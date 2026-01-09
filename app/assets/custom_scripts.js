// Scripts personalizados para la aplicación de Optimización de Rutas

// Variables globales para controlar animaciones
let animationFrameId = null;
let isAlgorithmRunning = false;

// Función para inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    initializeAnimations();
    setupEventListeners();
    initializeParticles();
});

// Inicializar animaciones de entrada
function initializeAnimations() {
    // Animar elementos al cargar la página
    const cards = document.querySelectorAll('.custom-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Animar métricas con efecto de conteo
    initializeMetricCounters();
}

// Configurar event listeners
function setupEventListeners() {
    // Escuchar cambios en el estado del algoritmo
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-running') {
                const isRunning = document.body.getAttribute('data-running') === 'true';
                toggleAlgorithmState(isRunning);
            }
        });
    });

    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['data-running']
    });

    // Agregar efectos hover a botones
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Agregar efectos a sliders
    const sliders = document.querySelectorAll('.rc-slider');
    sliders.forEach(slider => {
        slider.addEventListener('mousedown', function() {
            this.closest('.slider-container').classList.add('slider-active');
        });

        document.addEventListener('mouseup', function() {
            document.querySelectorAll('.slider-active').forEach(el => {
                el.classList.remove('slider-active');
            });
        });
    });
}

// Inicializar contadores de métricas
function initializeMetricCounters() {
    const metricElements = document.querySelectorAll('.metric-value');

    metricElements.forEach(element => {
        const originalText = element.textContent;

        // Solo animar si es un número
        if (!isNaN(parseFloat(originalText))) {
            animateCounter(element, 0, parseFloat(originalText), 1000);
        }
    });
}

// Función para animar contadores
function animateCounter(element, start, end, duration) {
    const startTime = performance.now();

    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Función de easing
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const currentValue = start + (end - start) * easeOutCubic;

        // Formatear según el tipo de métrica
        if (element.id.includes('fitness')) {
            element.textContent = currentValue.toFixed(4);
        } else if (element.id.includes('distancia')) {
            element.textContent = `${currentValue.toFixed(1)} km`;
        } else if (element.id.includes('tiempo')) {
            element.textContent = formatTime(currentValue);
        } else {
            element.textContent = Math.round(currentValue);
        }

        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }

    requestAnimationFrame(updateCounter);
}

// Formatear tiempo en minutos a formato legible
function formatTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);

    if (hours > 0) {
        return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
}

// Controlar estado del algoritmo
function toggleAlgorithmState(running) {
    isAlgorithmRunning = running;

    const body = document.body;
    const statusIndicator = document.querySelector('.status-indicator');

    if (running) {
        body.classList.add('algorithm-running');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-running';
        }
        startEvolutionAnimation();
    } else {
        body.classList.remove('algorithm-running');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-completed';
        }
        stopEvolutionAnimation();
        triggerCompletionAnimation();
    }
}

// Animación durante la evolución
function startEvolutionAnimation() {
    const chartContainer = document.querySelector('.chart-container');
    if (chartContainer) {
        chartContainer.classList.add('evolucion-activa');
    }

    // Animar elementos periódicamente
    function animateElements() {
        if (!isAlgorithmRunning) return;

        // Animar métricas aleatoriamente
        const metrics = document.querySelectorAll('.metric-card');
        metrics.forEach(metric => {
            if (Math.random() > 0.7) {
                metric.style.transform = `scale(${1 + Math.random() * 0.05})`;
                setTimeout(() => {
                    metric.style.transform = 'scale(1)';
                }, 200);
            }
        });

        animationFrameId = setTimeout(animateElements, 500);
    }

    animateElements();
}

// Detener animación de evolución
function stopEvolutionAnimation() {
    const chartContainer = document.querySelector('.chart-container');
    if (chartContainer) {
        chartContainer.classList.remove('evolucion-activa');
    }

    if (animationFrameId) {
        clearTimeout(animationFrameId);
        animationFrameId = null;
    }
}

// Animación de completitud
function triggerCompletionAnimation() {
    // Crear confetti o celebración
    createConfetti();

    // Animar tabla de resultados
    const table = document.querySelector('.table-container');
    if (table) {
        table.style.animation = 'none';
        setTimeout(() => {
            table.style.animation = 'fadeInUp 0.8s ease-out, glow 2s ease-in-out';
        }, 10);
    }

    // Animar métricas finales
    const metrics = document.querySelectorAll('.metric-card');
    metrics.forEach((metric, index) => {
        setTimeout(() => {
            metric.style.animation = 'pulse 0.6s ease-out';
        }, index * 200);
    });
}

// Crear efecto de confetti
function createConfetti() {
    const colors = ['#667eea', '#764ba2', '#4facfe', '#00f2fe', '#f093fb', '#f5576c'];

    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.position = 'fixed';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.top = '-10px';
            confetti.style.width = '10px';
            confetti.style.height = '10px';
            confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
            confetti.style.zIndex = '9999';
            confetti.style.pointerEvents = 'none';

            document.body.appendChild(confetti);

            // Animar confetti
            const animation = confetti.animate([
                { transform: 'translateY(-10px) rotate(0deg)', opacity: 1 },
                { transform: `translateY(${window.innerHeight + 20}px) rotate(${Math.random() * 720}deg)`, opacity: 0 }
            ], {
                duration: 3000 + Math.random() * 2000,
                easing: 'ease-out'
            });

            animation.onfinish = () => {
                if (confetti.parentNode) {
                    confetti.parentNode.removeChild(confetti);
                }
            };
        }, i * 50);
    }
}

// Inicializar efecto de partículas de fondo
function initializeParticles() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particle-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-1';

    document.body.insertBefore(canvas, document.body.firstChild);

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.1
        };
    }

    function initParticles() {
        particles = [];
        for (let i = 0; i < 50; i++) {
            particles.push(createParticle());
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Rebotar en bordes
            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;

            // Dibujar partícula
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(102, 126, 234, ${particle.opacity})`;
            ctx.fill();
        });

        animationId = requestAnimationFrame(animateParticles);
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    initParticles();
    animateParticles();

    // Cleanup function
    window.addParticleCleanup = function() {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        if (canvas.parentNode) {
            canvas.parentNode.removeChild(canvas);
        }
    };
}

// Funciones de utilidad para interacciones
function showToast(message, type = 'info') {
    // Crear elemento de toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#16a34a' : type === 'error' ? '#dc2626' : '#0891b2'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    // Remover después de 3 segundos
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Funciones para mejorar accesibilidad
function enhanceAccessibility() {
    // Agregar labels ARIA
    const sliders = document.querySelectorAll('[data-testid*="slider"]');
    sliders.forEach(slider => {
        const label = slider.previousElementSibling;
        if (label && label.tagName === 'LABEL') {
            slider.setAttribute('aria-label', label.textContent);
        }
    });

    // Mejorar navegación por teclado
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.setAttribute('tabindex', '0');
    });
}

// Inicializar mejoras de accesibilidad
enhanceAccessibility();

// Funciones globales para uso desde Python
window.showToast = showToast;
window.createConfetti = createConfetti;
