// Solução definitiva para Service Worker - bloquear ANTES de qualquer carregamento
(function() {
    'use strict';
    
    console.log('🔒 Service Worker Blocker ativado');
    
    // 1. Bloquear completamente Service Workers
    if ('serviceWorker' in navigator) {
        // Desregistrar qualquer SW existente imediatamente
        navigator.serviceWorker.getRegistrations()
            .then(registrations => {
                registrations.forEach(registration => {
                    registration.unregister();
                    console.log('🗑️ Service Worker desregistrado:', registration.scope);
                });
            })
            .catch(() => {}); // Silenciar erros
        
        // Substituir a função register por uma que sempre falha silenciosamente
        const originalRegister = navigator.serviceWorker.register;
        navigator.serviceWorker.register = function() {
            console.log('🚫 Service Worker registration blocked');
            return Promise.reject(new Error('Service Worker disabled for development'));
        };
        
        // Bloquear controller
        Object.defineProperty(navigator.serviceWorker, 'controller', {
            value: null,
            writable: false,
            configurable: false
        });
        
        // Bloquear ready
        Object.defineProperty(navigator.serviceWorker, 'ready', {
            value: Promise.reject(new Error('Service Worker disabled')),
            writable: false,
            configurable: false
        });
    }
    
    // 2. Interceptar e bloquear tentativas de registro via scripts
    const originalCreateElement = document.createElement;
    document.createElement = function(tagName) {
        const element = originalCreateElement.call(this, tagName);
        
        if (tagName.toLowerCase() === 'script') {
            // Interceptar mudanças no src para bloquear SWs
            Object.defineProperty(element, 'src', {
                set: function(value) {
                    if (value && (
                        value.includes('service-worker') ||
                        value.includes('sw.js') ||
                        value.includes('serviceworker')
                    )) {
                        console.log('🚫 Script de Service Worker bloqueado:', value);
                        return; // Não definir o src
                    }
                    element.setAttribute('src', value);
                },
                get: function() {
                    return element.getAttribute('src');
                }
            });
        }
        
        return element;
    };
    
    // 3. Bloquear via fetch/xhr se necessário
    const originalFetch = window.fetch;
    window.fetch = function(input, init) {
        const url = typeof input === 'string' ? input : input.url;
        if (url && (
            url.includes('service-worker') ||
            url.includes('sw.js') ||
            url.includes('serviceworker')
        )) {
            console.log('🚫 Fetch de Service Worker bloqueado:', url);
            return Promise.reject(new Error('Service Worker fetch blocked'));
        }
        return originalFetch.call(this, input, init);
    };
    
    // 4. Suprimir TODOS os erros relacionados a SW
    const originalError = window.console.error;
    window.console.error = function(...args) {
        const message = args.join(' ');
        if (message.includes('ServiceWorker') || 
            message.includes('InvalidStateError') ||
            message.includes('Failed to register') ||
            message.includes('service worker')) {
            console.log('🔇 Erro de SW suprimido:', message);
            return;
        }
        originalError.apply(console, args);
    };
    
    // 5. Bloquear via event listeners
    window.addEventListener('error', function(event) {
        if (event.message && (
            event.message.includes('ServiceWorker') ||
            event.message.includes('InvalidStateError') ||
            event.message.includes('Failed to register')
        )) {
            event.preventDefault();
            event.stopPropagation();
            console.log('🔇 Erro de SW interceptado e bloqueado');
            return false;
        }
    }, true); // Capture phase
    
    window.addEventListener('unhandledrejection', function(event) {
        if (event.reason && event.reason.message && (
            event.reason.message.includes('ServiceWorker') ||
            event.reason.message.includes('InvalidStateError') ||
            event.reason.message.includes('Failed to register')
        )) {
            event.preventDefault();
            console.log('🔇 Promise rejection de SW interceptada e bloqueada');
        }
    });
    
    // 6. Definir permissions policy via meta tag
    const meta = document.createElement('meta');
    meta.httpEquiv = 'Permissions-Policy';
    meta.content = 'service-worker=()';
    document.head.insertBefore(meta, document.head.firstChild);
    
    console.log('✅ Service Worker completamente bloqueado');
})();