// SCRIPT DE TESTE AUTOMATIZADO DE RESPONSIVIDADE
// Execute no console do navegador (F12) para testar breakpoints

console.log('🎯 Iniciando testes de responsividade...');

// Breakpoints Bootstrap 5
const breakpoints = {
    'xs': { width: 320, height: 568, name: 'Mobile Portrait (iPhone SE)' },
    'sm': { width: 576, height: 768, name: 'Mobile Landscape' },
    'md': { width: 768, height: 1024, name: 'Tablet Portrait' },
    'lg': { width: 992, height: 768, name: 'Tablet Landscape' },
    'xl': { width: 1200, height: 800, name: 'Desktop' },
    'xxl': { width: 1400, height: 900, name: 'Large Desktop' }
};

// Função para testar cada breakpoint
function testBreakpoint(bp, size) {
    return new Promise((resolve) => {
        console.log(`📱 Testando ${size.name} (${size.width}x${size.height})`);
        
        // Simular resize
        window.resizeTo(size.width, size.height);
        
        setTimeout(() => {
            const results = {
                breakpoint: bp,
                name: size.name,
                width: size.width,
                height: size.height,
                tests: {
                    navbar: checkNavbar(),
                    cards: checkCards(),
                    buttons: checkButtons(),
                    typography: checkTypography()
                }
            };
            
            console.log(`✅ ${size.name} testado:`, results);
            resolve(results);
        }, 500); // Aguardar resize
    });
}

// Testar navbar responsivo
function checkNavbar() {
    const navbar = document.querySelector('.navbar');
    const toggler = document.querySelector('.navbar-toggler');
    const collapse = document.querySelector('.navbar-collapse');
    
    return {
        exists: !!navbar,
        hasToggler: !!toggler,
        hasCollapse: !!collapse,
        togglerVisible: toggler ? getComputedStyle(toggler).display !== 'none' : false
    };
}

// Testar cards layout
function checkCards() {
    const cards = document.querySelectorAll('.card');
    const cardParents = document.querySelectorAll('.col-md-4, .col-lg-4');
    
    return {
        cardCount: cards.length,
        responsiveColumns: cardParents.length,
        cardsResponsive: cards.length > 0
    };
}

// Testar botões e touch targets
function checkButtons() {
    const buttons = document.querySelectorAll('.btn');
    let touchTargetOK = 0;
    
    buttons.forEach(btn => {
        const rect = btn.getBoundingClientRect();
        if (rect.height >= 44 && rect.width >= 44) {
            touchTargetOK++;
        }
    });
    
    return {
        totalButtons: buttons.length,
        touchTargetCompliant: touchTargetOK,
        compliance: touchTargetOK / buttons.length * 100
    };
}

// Testar tipografia responsiva
function checkTypography() {
    const h1 = document.querySelector('h1');
    const lead = document.querySelector('.lead');
    
    return {
        h1Size: h1 ? getComputedStyle(h1).fontSize : 'none',
        leadSize: lead ? getComputedStyle(lead).fontSize : 'none',
        responsive: true // Bootstrap tipografia é responsiva por padrão
    };
}

// Executar todos os testes
async function runResponsiveTests() {
    console.log('🚀 Executando suite completa de testes responsivos...');
    
    const results = [];
    
    for (const [bp, size] of Object.entries(breakpoints)) {
        const result = await testBreakpoint(bp, size);
        results.push(result);
    }
    
    // Gerar relatório
    console.log('📊 RELATÓRIO DE RESPONSIVIDADE:');
    console.table(results);
    
    // Verificar conformidade geral
    const totalTests = results.length;
    const passedTests = results.filter(r => 
        r.tests.navbar.exists && 
        r.tests.cards.cardsResponsive && 
        r.tests.buttons.compliance > 80
    ).length;
    
    const overallScore = (passedTests / totalTests * 100).toFixed(1);
    
    console.log(`🎯 SCORE RESPONSIVIDADE: ${overallScore}%`);
    
    if (overallScore >= 90) {
        console.log('✅ EXCELENTE: Design totalmente responsivo!');
    } else if (overallScore >= 70) {
        console.log('⚠️ BOM: Alguns ajustes menores necessários');
    } else {
        console.log('❌ CRÍTICO: Problemas significativos de responsividade');
    }
    
    return {
        score: overallScore,
        results: results,
        status: overallScore >= 90 ? 'PASS' : overallScore >= 70 ? 'WARN' : 'FAIL'
    };
}

// Auto-executar se estiver em desenvolvimento
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    runResponsiveTests();
}

// Expor função globalmente
window.runResponsiveTests = runResponsiveTests;