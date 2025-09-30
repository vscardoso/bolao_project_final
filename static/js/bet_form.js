/**
 * JavaScript aprimorado para formulário de apostas
 * Validação em tempo real, análise de probabilidades e melhorias de UX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Animação dos campos de placar
    const scoreInputs = document.querySelectorAll('.score-input');
    
    scoreInputs.forEach(input => {
        // Validação e formatação em tempo real
        input.addEventListener('input', function(e) {
            let value = e.target.value;
            
            // Remover caracteres não numéricos
            value = value.replace(/[^0-9]/g, '');
            
            // Limitar a 2 dígitos
            if (value.length > 2) {
                value = value.slice(0, 2);
            }
            
            e.target.value = value;
            
            // Validar score
            validateScore(this);
            updateTotalGoals();
            showPredictionAnalysis();
        });
        
        // Finalizar validação ao sair do campo
        input.addEventListener('blur', function() {
            finalizeScore(this);
            
            // Remover efeito de destaque dos times
            const homeTeam = document.querySelector('.team-name.home');
            const awayTeam = document.querySelector('.team-name.away');
            if (homeTeam) homeTeam.style.color = '#2c3e50';
            if (awayTeam) awayTeam.style.color = '#2c3e50';
        });
        
        // Adicionar efeito de foco
        input.addEventListener('focus', function(e) {
            highlightField(this);
            
            const teamName = e.target.parentNode.querySelector('label')?.textContent;
            if (teamName && teamName.includes('(Casa)')) {
                const homeTeam = document.querySelector('.team-name.home');
                if (homeTeam) homeTeam.style.color = 'var(--primary-color)';
            } else {
                const awayTeam = document.querySelector('.team-name.away');
                if (awayTeam) awayTeam.style.color = 'var(--primary-color)';
            }
        });

        // Permitir apenas números
        input.addEventListener('keypress', function(e) {
            if (!/[0-9]/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Enter'].includes(e.key)) {
                e.preventDefault();
            }
        });
    });
    
    // Verificar se a aposta é válida antes de enviar
    const betForm = document.querySelector('.bet-form, form');
    if (betForm) {
        betForm.addEventListener('submit', function(e) {
            const homeScore = document.getElementById('id_home_score_bet')?.value;
            const awayScore = document.getElementById('id_away_score_bet')?.value;
            
            if (homeScore === '' || awayScore === '') {
                e.preventDefault();
                alert('Por favor, preencha os placares para ambos os times.');
                return;
            }

            // Adicionar animação de envio
            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando aposta...';
                submitBtn.disabled = true;
            }
        });
    }
    
    // Inicializar cronômetro regressivo
    initCountdown();
    
    // Inicializar análise de probabilidades
    initializeProbabilityAnalysis();
});

/**
 * Validar score em tempo real
 */
function validateScore(input) {
    const value = parseInt(input.value);
    const container = input.closest('.form-group') || input.closest('.mb-3');
    
    // Remover classes de validação anteriores
    input.classList.remove('is-valid', 'is-invalid');
    
    // Remover feedback anterior
    const existingFeedback = container?.querySelector('.invalid-feedback, .valid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }

    if (input.value === '') {
        return; // Campo vazio, não validar ainda
    }

    if (isNaN(value) || value < 0) {
        showFieldError(input, 'Valor deve ser um número positivo');
        return;
    }

    if (value > 20) {
        showFieldError(input, 'Máximo 20 gols');
        return;
    }

    if (value > 15) {
        showFieldWarning(input, 'Placar alto - tem certeza?');
        return;
    }

    // Validação passou
    showFieldSuccess(input);
}

/**
 * Finalizar validação do score
 */
function finalizeScore(input) {
    if (input.value === '') {
        showFieldError(input, 'Este campo é obrigatório');
    }
}

/**
 * Destacar campo ao focar
 */
function highlightField(input) {
    const container = input.closest('.form-group, .mb-3');
    if (container) {
        container.style.transform = 'scale(1.02)';
        container.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            container.style.transform = 'scale(1)';
        }, 200);
    }
}

/**
 * Mostrar erro no campo
 */
function showFieldError(input, message) {
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    
    const container = input.closest('.form-group') || input.closest('.mb-3');
    if (container) {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback d-block';
        feedback.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        container.appendChild(feedback);
    }
}

/**
 * Mostrar aviso no campo
 */
function showFieldWarning(input, message) {
    input.classList.add('is-valid'); // Usa verde mas com aviso
    input.classList.remove('is-invalid');
    
    const container = input.closest('.form-group') || input.closest('.mb-3');
    if (container) {
        const feedback = document.createElement('div');
        feedback.className = 'valid-feedback d-block text-warning';
        feedback.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        container.appendChild(feedback);
    }
}

/**
 * Mostrar sucesso no campo
 */
function showFieldSuccess(input) {
    input.classList.add('is-valid');
    input.classList.remove('is-invalid');
    
    const container = input.closest('.form-group') || input.closest('.mb-3');
    if (container) {
        const feedback = document.createElement('div');
        feedback.className = 'valid-feedback d-block';
        feedback.innerHTML = '<i class="fas fa-check-circle"></i> Ótimo!';
        container.appendChild(feedback);
    }
}

/**
 * Atualizar total de gols
 */
function updateTotalGoals() {
    const homeInput = document.querySelector('input[name="home_score_bet"]');
    const awayInput = document.querySelector('input[name="away_score_bet"]');
    
    if (!homeInput || !awayInput) return;
    
    const homeValue = parseInt(homeInput.value) || 0;
    const awayValue = parseInt(awayInput.value) || 0;
    const total = homeValue + awayValue;
    
    // Encontrar ou criar elemento de total
    let totalElement = document.querySelector('#total-goals');
    if (!totalElement) {
        totalElement = document.createElement('div');
        totalElement.id = 'total-goals';
        totalElement.className = 'mt-3 text-center';
        
        const form = document.querySelector('.bet-form, form');
        if (form) {
            form.appendChild(totalElement);
        }
    }
    
    // Atualizar conteúdo do total
    let badge = 'secondary';
    let icon = 'fas fa-calculator';
    let message = 'Total de gols';
    
    if (total > 10) {
        badge = 'warning';
        icon = 'fas fa-exclamation-triangle';
        message = 'Muitos gols!';
    } else if (total > 6) {
        badge = 'info';
        icon = 'fas fa-fire';
        message = 'Jogo movimentado!';
    } else if (total > 3) {
        badge = 'success';
        icon = 'fas fa-futbol';
        message = 'Bom placar!';
    } else if (total > 0) {
        badge = 'primary';
        icon = 'fas fa-shield-alt';
        message = 'Jogo defensivo';
    }
    
    totalElement.innerHTML = `
        <span class="badge bg-${badge} fs-6">
            <i class="${icon}"></i> ${message}: ${total} gols
        </span>
    `;
}

/**
 * Mostrar análise de predição
 */
function showPredictionAnalysis() {
    const homeInput = document.querySelector('input[name="home_score_bet"]');
    const awayInput = document.querySelector('input[name="away_score_bet"]');
    
    if (!homeInput || !awayInput || !homeInput.value || !awayInput.value) return;
    
    const homeScore = parseInt(homeInput.value);
    const awayScore = parseInt(awayInput.value);
    
    // Encontrar ou criar elemento de análise
    let analysisElement = document.querySelector('#prediction-analysis');
    if (!analysisElement) {
        analysisElement = document.createElement('div');
        analysisElement.id = 'prediction-analysis';
        analysisElement.className = 'mt-3 p-3 bg-light rounded';
        
        const totalElement = document.querySelector('#total-goals');
        if (totalElement) {
            totalElement.after(analysisElement);
        }
    }
    
    // Determinar resultado
    let result, resultClass, resultIcon;
    if (homeScore > awayScore) {
        result = 'Vitória da Casa';
        resultClass = 'text-success';
        resultIcon = 'fas fa-home';
    } else if (awayScore > homeScore) {
        result = 'Vitória Visitante';
        resultClass = 'text-primary';
        resultIcon = 'fas fa-plane';
    } else {
        result = 'Empate';
        resultClass = 'text-warning';
        resultIcon = 'fas fa-equals';
    }
    
    // Calcular "probabilidade" baseada no placar (simulação)
    const total = homeScore + awayScore;
    const diff = Math.abs(homeScore - awayScore);
    
    let probability;
    if (total <= 3 && diff <= 1) {
        probability = 'Alta';
    } else if (total <= 6 && diff <= 2) {
        probability = 'Média';
    } else {
        probability = 'Baixa';
    }
    
    analysisElement.innerHTML = `
        <h6><i class="fas fa-chart-line"></i> Análise da Aposta</h6>
        <div class="row">
            <div class="col-md-6">
                <small class="text-muted">Resultado:</small><br>
                <span class="${resultClass}">
                    <i class="${resultIcon}"></i> ${result}
                </span>
            </div>
            <div class="col-md-6">
                <small class="text-muted">Probabilidade:</small><br>
                <span class="badge bg-info">${probability}</span>
            </div>
        </div>
    `;
}

/**
 * Inicializar análise de probabilidades
 */
function initializeProbabilityAnalysis() {
    // Adicionar dicas de apostas comuns
    const form = document.querySelector('.bet-form, form');
    if (form) {
        const tipsElement = document.createElement('div');
        tipsElement.className = 'mt-4 p-3 bg-info bg-opacity-10 rounded';
        tipsElement.innerHTML = `
            <h6><i class="fas fa-lightbulb text-warning"></i> Dicas de Apostas</h6>
            <div class="row">
                <div class="col-md-4">
                    <small><strong>Placares Comuns:</strong><br>
                    1-0, 2-1, 1-1, 2-0</small>
                </div>
                <div class="col-md-4">
                    <small><strong>Jogos com Gols:</strong><br>
                    2-2, 3-1, 2-3, 3-2</small>
                </div>
                <div class="col-md-4">
                    <small><strong>Goleadas:</strong><br>
                    3-0, 4-1, 0-3, 5-0</small>
                </div>
            </div>
        `;
        
        form.appendChild(tipsElement);
    }
}

/**
 * Inicializa e atualiza o cronômetro regressivo
 */
function initCountdown() {
    const countdownElement = document.querySelector('.countdown-timer');
    if (!countdownElement) return;
    
    const matchTimeStr = countdownElement.getAttribute('data-match-time');
    const matchTime = new Date(matchTimeStr);
    
    function updateCountdown() {
        const now = new Date();
        const diff = matchTime - now;
        
        if (diff <= 0) {
            // Tempo esgotado
            const timeElements = ['days', 'hours', 'minutes', 'seconds'];
            timeElements.forEach(element => {
                const el = document.querySelector(`.${element}`);
                if (el) el.textContent = '00';
            });
            
            // Desabilitar formulário se o tempo acabou
            const inputs = document.querySelectorAll('.score-input');
            const submitBtn = document.querySelector('button[type="submit"]');
            
            inputs.forEach(input => {
                input.disabled = true;
            });
            
            if (submitBtn) submitBtn.disabled = true;
            
            // Adicionar mensagem de tempo esgotado
            const countdownContainer = document.querySelector('.countdown-container');
            if (countdownContainer) {
                countdownContainer.innerHTML = '<div class="alert alert-danger mb-0">⏰ Tempo para apostar esgotado!</div>';
            }
            
            return;
        }
        
        // Calcular dias, horas, minutos e segundos
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        // Atualizar os números no cronômetro
        const daysEl = document.querySelector('.days');
        const hoursEl = document.querySelector('.hours');
        const minutesEl = document.querySelector('.minutes');
        const secondsEl = document.querySelector('.seconds');
        
        if (daysEl) daysEl.textContent = days.toString().padStart(2, '0');
        if (hoursEl) hoursEl.textContent = hours.toString().padStart(2, '0');
        if (minutesEl) minutesEl.textContent = minutes.toString().padStart(2, '0');
        if (secondsEl) secondsEl.textContent = seconds.toString().padStart(2, '0');
        
        // Adicionar classe de destaque quando estiver perto do prazo
        if (diff < 3600000) { // Menos de 1 hora
            countdownElement.classList.add('countdown-urgent');
        }
        
        // Chamar esta função novamente em 1 segundo
        setTimeout(updateCountdown, 1000);
    }
    
    // Iniciar o cronômetro
    updateCountdown();
}