// Script para corrigir problemas de layout e comportamento

document.addEventListener('DOMContentLoaded', function() {
    console.log('Layout Fix Script carregado');
    
    // Fix para problemas de CSS
    function fixLayoutIssues() {
        // Remover estilos inline problemáticos
        const problematicElements = document.querySelectorAll('[style*="background-color: rgb"]');
        problematicElements.forEach(element => {
            element.removeAttribute('style');
        });
        
        // Garantir que o body tenha a classe correta
        document.body.classList.add('layout-fixed');
        
        // Fix para navbar
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.style.backgroundColor = '#ffffff';
            navbar.style.borderBottom = '1px solid #dee2e6';
        }
        
        // Fix para sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.style.backgroundColor = '#ffffff';
            sidebar.style.borderRight = '1px solid #dee2e6';
        }
        
        // Fix para cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.backgroundColor = '#ffffff';
            card.style.border = '1px solid #dee2e6';
            card.style.borderRadius = '8px';
        });
        
        // Fix para botões
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            if (button.classList.contains('btn-primary')) {
                button.style.backgroundColor = '#007bff';
                button.style.borderColor = '#007bff';
                button.style.color = '#ffffff';
            }
        });
        
        // Fix para formulários
        const formControls = document.querySelectorAll('.form-control');
        formControls.forEach(control => {
            control.style.backgroundColor = '#ffffff';
            control.style.border = '1px solid #dee2e6';
            control.style.color = '#2c3e50';
        });
        
        console.log('Layout fixes aplicados');
    }
    
    // Aplicar fixes imediatamente
    fixLayoutIssues();
    
    // Aplicar fixes após carregamento completo
    window.addEventListener('load', function() {
        setTimeout(fixLayoutIssues, 100);
    });
    
    // Fix para problemas de fonte
    function fixFontIssues() {
        const style = document.createElement('style');
        style.textContent = `
            body, .form-control, .btn, .card {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    fixFontIssues();
    
    // Observer para mudanças no DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Aplicar fixes em novos elementos
                        if (node.classList && node.classList.contains('card')) {
                            node.style.backgroundColor = '#ffffff';
                        }
                        if (node.classList && node.classList.contains('btn-primary')) {
                            node.style.backgroundColor = '#007bff';
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('Layout Fix Script executado com sucesso');
});

// Função global para debug
window.debugLayout = function() {
    console.log('=== DEBUG LAYOUT ===');
    console.log('Body classes:', document.body.className);
    console.log('CSS files carregados:');
    document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
        console.log('- ' + link.href);
    });
    console.log('Scripts carregados:');
    document.querySelectorAll('script[src]').forEach(script => {
        console.log('- ' + script.src);
    });
    console.log('Cores computadas:');
    const body = getComputedStyle(document.body);
    console.log('- Background:', body.backgroundColor);
    console.log('- Color:', body.color);
    console.log('- Font:', body.fontFamily);
};