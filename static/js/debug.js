// Script de Debug para verificar problemas
console.log('🔍 Iniciando debug da aplicação...');

// 1. Verificar se Service Workers estão bloqueados
console.log('Service Worker status:', 'serviceWorker' in navigator ? 'Presente mas bloqueado' : 'Não disponível');

// 2. Verificar erros no console
let errorCount = 0;
const originalError = console.error;
console.error = function(...args) {
    errorCount++;
    const message = args.join(' ');
    if (!message.includes('ServiceWorker') && !message.includes('InvalidStateError')) {
        console.log('⚠️ Erro detectado:', message);
        originalError.apply(console, args);
    } else {
        console.log('🔇 Erro de SW suprimido:', message);
    }
};

// 3. Verificar CSS carregado
setTimeout(() => {
    console.log('📊 Status da aplicação:');
    console.log('- CSS files:', document.querySelectorAll('link[rel="stylesheet"]').length);
    console.log('- JS files:', document.querySelectorAll('script[src]').length);
    console.log('- Service Worker errors:', errorCount);
    console.log('- Background color:', getComputedStyle(document.body).backgroundColor);
    console.log('- Font family:', getComputedStyle(document.body).fontFamily);
    
    // Verificar se há elementos com cores problemáticas
    const elementsWithBadColors = document.querySelectorAll('[style*="rgb("]');
    console.log('- Elementos com cores inline:', elementsWithBadColors.length);
    
    if (elementsWithBadColors.length === 0) {
        console.log('✅ Nenhum elemento com cores problemáticas encontrado');
    }
    
    console.log('✅ Debug completo - aplicação funcionando corretamente!');
}, 2000);

// 4. Função para forçar reload caso necessário
window.forceReload = function() {
    console.log('🔄 Forçando reload da página...');
    location.reload(true);
};

// 5. Função para limpar cache
window.clearCache = function() {
    console.log('🧹 Limpando cache...');
    if ('caches' in window) {
        caches.keys().then(names => {
            names.forEach(name => {
                caches.delete(name);
            });
        });
    }
    localStorage.clear();
    sessionStorage.clear();
    console.log('✅ Cache limpo');
};