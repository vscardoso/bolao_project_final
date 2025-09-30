/**
 * Browser Compatibility & Error Prevention
 * Script para prevenir erros comuns em ambiente de desenvolvimento
 */

// Prevenir erros de Service Worker
(function() {
    'use strict';
    
    // Função para desabilitar Service Workers
    function disableServiceWorkers() {
        if ('serviceWorker' in navigator) {
            // Limpar registros existentes
            navigator.serviceWorker.getRegistrations()
                .then(function(registrations) {
                    registrations.forEach(function(registration) {
                        registration.unregister();
                    });
                })
                .catch(function(error) {
                    console.log('Service Worker cleanup failed:', error);
                });
            
            // Interceptar tentativas de registro
            const originalRegister = navigator.serviceWorker.register;
            navigator.serviceWorker.register = function() {
                console.log('Service Worker registration blocked for development');
                return Promise.reject(new Error('Service Worker registration disabled in development'));
            };
        }
    }
    
    // Função para suprimir erros específicos
    function suppressSpecificErrors() {
        // Suprimir erros de Service Worker
        window.addEventListener('error', function(event) {
            const errorMessages = [
                'ServiceWorker',
                'Failed to register a ServiceWorker',
                'InvalidStateError',
                'The document is in an invalid state'
            ];
            
            if (event.message && errorMessages.some(msg => event.message.includes(msg))) {
                console.log('Service Worker error suppressed:', event.message);
                event.preventDefault();
                return false;
            }
        });
        
        // Suprimir promessas rejeitadas relacionadas
        window.addEventListener('unhandledrejection', function(event) {
            if (event.reason && event.reason.message) {
                const errorMessages = [
                    'ServiceWorker',
                    'Failed to register a ServiceWorker',
                    'InvalidStateError'
                ];
                
                if (errorMessages.some(msg => event.reason.message.includes(msg))) {
                    console.log('Service Worker promise rejection suppressed:', event.reason.message);
                    event.preventDefault();
                    return false;
                }
            }
        });
    }
    
    // Função para melhorar compatibilidade de console
    function improveConsoleCompatibility() {
        // Garantir que console.log existe
        if (typeof console === 'undefined') {
            window.console = {
                log: function() {},
                error: function() {},
                warn: function() {},
                info: function() {}
            };
        }
        
        // Interceptar erros de console relacionados a Service Workers
        const originalError = console.error;
        console.error = function() {
            const args = Array.prototype.slice.call(arguments);
            const message = args.join(' ');
            
            if (!message.includes('ServiceWorker') && !message.includes('InvalidStateError')) {
                originalError.apply(console, arguments);
            }
        };
    }
    
    // Função para configurar headers de segurança
    function configureSecurityHeaders() {
        // Adicionar meta tags de segurança se não existirem
        if (!document.querySelector('meta[http-equiv="Content-Security-Policy"]')) {
            const cspMeta = document.createElement('meta');
            cspMeta.setAttribute('http-equiv', 'Content-Security-Policy');
            cspMeta.setAttribute('content', "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:;");
            document.head.appendChild(cspMeta);
        }
        
        // Configurar permissões para desenvolvimento
        if (!document.querySelector('meta[http-equiv="Permissions-Policy"]')) {
            const permissionsMeta = document.createElement('meta');
            permissionsMeta.setAttribute('http-equiv', 'Permissions-Policy');
            permissionsMeta.setAttribute('content', 'service-worker=()');
            document.head.appendChild(permissionsMeta);
        }
    }
    
    // Função para melhorar performance do DOM
    function improveDOMPerformance() {
        // Otimizar carregamento de imagens
        const images = document.querySelectorAll('img');
        images.forEach(function(img) {
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
        });
        
        // Adicionar prefetch para recursos críticos
        const linkPrefetch = document.createElement('link');
        linkPrefetch.rel = 'prefetch';
        linkPrefetch.href = '/static/css/layout-fixes.css';
        document.head.appendChild(linkPrefetch);
    }
    
    // Executar todas as configurações quando o DOM estiver pronto
    function initializeCompatibility() {
        disableServiceWorkers();
        suppressSpecificErrors();
        improveConsoleCompatibility();
        configureSecurityHeaders();
        improveDOMPerformance();
        
        console.log('Browser compatibility initialized');
    }
    
    // Executar imediatamente ou quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeCompatibility);
    } else {
        initializeCompatibility();
    }
    
})();