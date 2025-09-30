/**
 * Script de Limpeza Manual de Service Workers
 * Execute este código no console do navegador (F12) para limpar completamente Service Workers
 */

// Função para limpar Service Workers manualmente
async function clearServiceWorkers() {
    console.log('🚀 Iniciando limpeza completa de Service Workers...');
    
    try {
        // 1. Desregistrar todos os Service Workers
        if ('serviceWorker' in navigator) {
            const registrations = await navigator.serviceWorker.getRegistrations();
            
            for (let registration of registrations) {
                const result = await registration.unregister();
                console.log(`🗑️ Service Worker removido: ${registration.scope} - Sucesso: ${result}`);
            }
            
            if (registrations.length === 0) {
                console.log('✅ Nenhum Service Worker encontrado para remover');
            }
        }
        
        // 2. Limpar Cache Storage
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            
            for (let cacheName of cacheNames) {
                const result = await caches.delete(cacheName);
                console.log(`🗑️ Cache removido: ${cacheName} - Sucesso: ${result}`);
            }
            
            if (cacheNames.length === 0) {
                console.log('✅ Nenhum cache encontrado para remover');
            }
        }
        
        // 3. Limpar Local Storage relacionado
        const localStorageKeys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && (
                key.includes('sw') || 
                key.includes('service') || 
                key.includes('worker') ||
                key.includes('cache')
            )) {
                localStorageKeys.push(key);
            }
        }
        
        localStorageKeys.forEach(key => {
            localStorage.removeItem(key);
            console.log(`🗑️ LocalStorage removido: ${key}`);
        });
        
        // 4. Limpar Session Storage relacionado
        const sessionStorageKeys = [];
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            if (key && (
                key.includes('sw') || 
                key.includes('service') || 
                key.includes('worker') ||
                key.includes('cache')
            )) {
                sessionStorageKeys.push(key);
            }
        }
        
        sessionStorageKeys.forEach(key => {
            sessionStorage.removeItem(key);
            console.log(`🗑️ SessionStorage removido: ${key}`);
        });
        
        // 5. Bloquear novos registros
        if ('serviceWorker' in navigator) {
            // Bloquear novos registros sem usar a referência original
            navigator.serviceWorker.register = function() {
                console.log('🚫 Service Worker registration blocked');
                return Promise.reject(new Error('Service Worker disabled'));
            };
            console.log('🔒 Service Worker registration bloqueado');
        }
        
        console.log('✅ Limpeza completa finalizada!');
        console.log('💡 Recarregue a página (Ctrl+F5 ou Ctrl+Shift+R) para garantir que as mudanças tenham efeito');
        
        return {
            success: true,
            serviceWorkersRemoved: registrations ? registrations.length : 0,
            cachesRemoved: cacheNames ? cacheNames.length : 0,
            localStorageKeysRemoved: localStorageKeys.length,
            sessionStorageKeysRemoved: sessionStorageKeys.length
        };
        
    } catch (error) {
        console.error('❌ Erro durante a limpeza:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

// Função para verificar status atual
function checkServiceWorkerStatus() {
    console.log('🔍 Verificando status atual dos Service Workers...');
    
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(registrations => {
            console.log(`📊 Service Workers ativos: ${registrations.length}`);
            registrations.forEach((reg, index) => {
                console.log(`  ${index + 1}. Scope: ${reg.scope}, State: ${reg.active ? reg.active.state : 'unknown'}`);
            });
        });
        
        console.log(`📊 Service Worker controller: ${navigator.serviceWorker.controller ? 'Ativo' : 'Nenhum'}`);
    }
    
    if ('caches' in window) {
        caches.keys().then(cacheNames => {
            console.log(`📊 Caches ativos: ${cacheNames.length}`);
            cacheNames.forEach((name, index) => {
                console.log(`  ${index + 1}. ${name}`);
            });
        });
    }
}

// Executar limpeza automaticamente se este arquivo for carregado em desenvolvimento
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🏠 Ambiente de desenvolvimento detectado');
    checkServiceWorkerStatus();
    
    // Aguardar um pouco para que a página carregue completamente
    setTimeout(() => {
        clearServiceWorkers().then(result => {
            if (result.success) {
                console.log('🎉 Limpeza automática concluída com sucesso!');
            }
        });
    }, 1000);
}

// Expor funções globalmente para uso manual
window.clearServiceWorkers = clearServiceWorkers;
window.checkServiceWorkerStatus = checkServiceWorkerStatus;

console.log('🛠️ Funções disponíveis:');
console.log('  clearServiceWorkers() - Limpar tudo');
console.log('  checkServiceWorkerStatus() - Verificar status');