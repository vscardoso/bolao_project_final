// Funções auxiliares para o projeto Bolão Online

// Valida formato de telefone: (00) 00000-0000
function validatePhone(phone) {
    const regex = /^\([0-9]{2}\) [0-9]{5}-[0-9]{4}$/;
    return regex.test(phone);
}

// Aplica máscara de telefone
function applyPhoneMask(input) {
    input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        if (value.length > 0) {
            value = '(' + value;
        }
        if (value.length > 3) {
            value = value.substring(0, 3) + ') ' + value.substring(3);
        }
        if (value.length > 10) {
            value = value.substring(0, 10) + '-' + value.substring(10, 14);
        }
        
        e.target.value = value;
    });
}

// Função para inicializar elementos de forma segura
function safelyInitialize(selector, callback) {
    const elements = document.querySelectorAll(selector);
    if (elements && elements.length > 0) {
        elements.forEach(callback);
        return true;
    }
    return false;
}

// Inicializa as funcionalidades quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Aplica máscaras de telefone a todos os campos com ID que contém 'phone'
    safelyInitialize('input[id*="phone"]', applyPhoneMask);
    
    // Adiciona classes Bootstrap aos alertas de mensagens
    safelyInitialize('.alert:not(.alert-info):not(.info-message)', function(message) {
        setTimeout(function() {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(message);
                bsAlert.close();
            }
        }, 5000); // Fecha automaticamente após 5 segundos
    });
    
    // Inicializa tooltips do Bootstrap
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        safelyInitialize('[data-bs-toggle="tooltip"]', function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Animar scroll suave para links de âncora
    safelyInitialize('a[href^="#"]', function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Ativa animações ao scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        function checkIfInView() {
            const windowHeight = window.innerHeight;
            const windowTopPosition = window.scrollY;
            const windowBottomPosition = windowTopPosition + windowHeight;
            
            animatedElements.forEach(function(element) {
                const elementHeight = element.offsetHeight;
                const elementTopPosition = element.offsetTop;
                const elementBottomPosition = elementTopPosition + elementHeight;
                
                // Verifica se o elemento está visível
                if (
                    (elementBottomPosition >= windowTopPosition) && 
                    (elementTopPosition <= windowBottomPosition)
                ) {
                    element.classList.add('animated');
                }
            });
        }
        
        window.addEventListener('scroll', checkIfInView);
        checkIfInView(); // Verifica elementos visíveis no carregamento inicial
    }
});