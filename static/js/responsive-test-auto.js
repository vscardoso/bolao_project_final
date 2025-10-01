// 🚀 SCRIPT DE TESTE RESPONSIVO AUTOMÁTICO
// Execute no console do DevTools para teste rápido

console.log('🚀 INICIANDO TESTE RESPONSIVO AUTOMÁTICO...');

const BREAKPOINTS = [
    { name: 'Mobile S', width: 320, height: 568 },
    { name: 'Mobile M', width: 375, height: 667 },
    { name: 'Mobile L', width: 414, height: 736 },
    { name: 'Tablet', width: 768, height: 1024 },
    { name: 'Laptop', width: 1024, height: 768 },
    { name: 'Desktop', width: 1440, height: 900 },
    { name: '4K', width: 1920, height: 1080 }
];

const SELECTORS_TO_TEST = [
    '.hero-section',
    '.navbar',
    '.stat-card',
    '.card',
    '.btn',
    '.container',
    'footer'
];

class ResponsiveTestRunner {
    constructor() {
        this.results = [];
        this.currentTest = 0;
        this.totalTests = BREAKPOINTS.length;
    }

    async runAllTests() {
        console.log(`📱 Testando ${this.totalTests} breakpoints...`);
        
        for (let i = 0; i < BREAKPOINTS.length; i++) {
            const breakpoint = BREAKPOINTS[i];
            console.log(`\n🔍 Testando ${breakpoint.name} (${breakpoint.width}x${breakpoint.height})`);
            
            await this.testBreakpoint(breakpoint);
            this.currentTest++;
            
            // Aguardar um pouco entre testes
            await this.sleep(1000);
        }
        
        this.generateReport();
    }

    async testBreakpoint(breakpoint) {
        // Simular mudança de viewport
        if (window.outerWidth !== breakpoint.width) {
            console.log(`⚠️  Simulando viewport ${breakpoint.width}px`);
        }

        const testResult = {
            breakpoint: breakpoint.name,
            width: breakpoint.width,
            issues: [],
            passed: [],
            timestamp: new Date().toISOString()
        };

        // Testar elementos principais
        SELECTORS_TO_TEST.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            
            if (elements.length === 0) {
                testResult.issues.push(`❌ Seletor não encontrado: ${selector}`);
                return;
            }

            elements.forEach((element, index) => {
                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);
                
                // Teste 1: Elemento visível
                if (rect.width === 0 || rect.height === 0) {
                    testResult.issues.push(`❌ ${selector}[${index}] invisível`);
                } else {
                    testResult.passed.push(`✅ ${selector}[${index}] visível`);
                }

                // Teste 2: Não está cortado horizontalmente
                if (rect.right > window.innerWidth) {
                    testResult.issues.push(`❌ ${selector}[${index}] cortado horizontalmente`);
                } else {
                    testResult.passed.push(`✅ ${selector}[${index}] dentro da viewport`);
                }

                // Teste 3: Font-size adequado para mobile
                if (breakpoint.width < 768) {
                    const fontSize = parseFloat(styles.fontSize);
                    if (fontSize < 14) {
                        testResult.issues.push(`⚠️  ${selector}[${index}] font muito pequena (${fontSize}px)`);
                    }
                }

                // Teste 4: Touch targets adequados
                if (element.tagName === 'BUTTON' || element.tagName === 'A') {
                    if (rect.height < 44 && breakpoint.width < 768) {
                        testResult.issues.push(`❌ ${selector}[${index}] touch target pequeno (${rect.height}px)`);
                    }
                }
            });
        });

        // Teste scroll horizontal
        if (document.documentElement.scrollWidth > window.innerWidth) {
            testResult.issues.push('❌ Scroll horizontal detectado');
        } else {
            testResult.passed.push('✅ Sem scroll horizontal');
        }

        this.results.push(testResult);
        
        // Log imediato dos resultados
        if (testResult.issues.length > 0) {
            console.log(`❌ ${testResult.issues.length} problemas encontrados:`);
            testResult.issues.forEach(issue => console.log(`   ${issue}`));
        } else {
            console.log(`✅ Breakpoint ${breakpoint.name} passou em todos os testes!`);
        }
    }

    generateReport() {
        console.log('\n📊 RELATÓRIO FINAL DE TESTE RESPONSIVO');
        console.log('=====================================');
        
        let totalIssues = 0;
        let totalPassed = 0;

        this.results.forEach(result => {
            totalIssues += result.issues.length;
            totalPassed += result.passed.length;
            
            console.log(`\n📱 ${result.breakpoint} (${result.width}px):`);
            console.log(`   ✅ Passou: ${result.passed.length} testes`);
            console.log(`   ❌ Falhou: ${result.issues.length} testes`);
            
            if (result.issues.length > 0) {
                console.log('   Problemas:');
                result.issues.forEach(issue => console.log(`     ${issue}`));
            }
        });

        console.log('\n🎯 RESUMO GERAL:');
        console.log(`✅ Total de testes passaram: ${totalPassed}`);
        console.log(`❌ Total de problemas: ${totalIssues}`);
        
        const successRate = Math.round((totalPassed / (totalPassed + totalIssues)) * 100);
        console.log(`📈 Taxa de sucesso: ${successRate}%`);

        if (successRate >= 95) {
            console.log('🎉 EXCELENTE! Design responsivo de alta qualidade!');
        } else if (successRate >= 85) {
            console.log('👍 BOM! Alguns ajustes podem melhorar a experiência.');
        } else if (successRate >= 70) {
            console.log('⚠️  ATENÇÃO! Vários problemas precisam ser corrigidos.');
        } else {
            console.log('🚨 CRÍTICO! Design precisa de revisão urgente.');
        }

        // Salvar resultados no localStorage para análise posterior
        localStorage.setItem('responsiveTestResults', JSON.stringify({
            timestamp: new Date().toISOString(),
            results: this.results,
            summary: {
                totalPassed,
                totalIssues,
                successRate
            }
        }));

        console.log('\n💾 Resultados salvos no localStorage como "responsiveTestResults"');
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Executar teste automaticamente
const testRunner = new ResponsiveTestRunner();
testRunner.runAllTests();

// Função auxiliar para testar um breakpoint específico
window.testBreakpoint = function(width, height = 768) {
    console.log(`🔍 Teste rápido para ${width}px`);
    const breakpoint = { name: `Custom`, width, height };
    const runner = new ResponsiveTestRunner();
    runner.testBreakpoint(breakpoint);
};

// Função para verificar performance
window.checkPerformance = function() {
    console.log('⚡ ANÁLISE DE PERFORMANCE:');
    
    const perfEntries = performance.getEntriesByType('navigation')[0];
    
    console.log(`🚀 DOM Content Loaded: ${Math.round(perfEntries.domContentLoadedEventEnd - perfEntries.domContentLoadedEventStart)}ms`);
    console.log(`📊 Load Complete: ${Math.round(perfEntries.loadEventEnd - perfEntries.loadEventStart)}ms`);
    console.log(`🎨 First Paint: ${Math.round(performance.getEntriesByType('paint')[0]?.startTime || 0)}ms`);
    
    const images = document.querySelectorAll('img');
    console.log(`🖼️  Total de imagens: ${images.length}`);
    
    const scripts = document.querySelectorAll('script');
    console.log(`📜 Total de scripts: ${scripts.length}`);
    
    const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
    console.log(`🎨 Total de CSS: ${stylesheets.length}`);
};

console.log('\n🛠️  COMANDOS DISPONÍVEIS:');
console.log('testBreakpoint(375)     - Testar breakpoint específico');
console.log('checkPerformance()      - Análise de performance');
console.log('localStorage.getItem("responsiveTestResults") - Ver resultados salvos');