document.addEventListener('DOMContentLoaded', function() {
    // Animação dos campos de placar
    const scoreInputs = document.querySelectorAll('.score-input');
    
    scoreInputs.forEach(input => {
        // Limitar a valores entre 0 e 99
        input.addEventListener('input', function(e) {
            let value = e.target.value;
            
            // Remover caracteres não numéricos
            value = value.replace(/[^0-9]/g, '');
            
            // Limitar a 2 dígitos
            if (value.length > 2) {
                value = value.slice(0, 2);
            }
            
            e.target.value = value;
        });
        
        // Adicionar efeito de foco
        input.addEventListener('focus', function(e) {
            const teamName = e.target.parentNode.querySelector('label').textContent;
            if (teamName.includes('(Casa)')) {
                document.querySelector('.team-name.home').style.color = 'var(--primary-color)';
            } else {
                document.querySelector('.team-name.away').style.color = 'var(--primary-color)';
            }
        });
        
        // Remover efeito ao perder foco
        input.addEventListener('blur', function(e) {
            document.querySelector('.team-name.home').style.color = '#2c3e50';
            document.querySelector('.team-name.away').style.color = '#2c3e50';
        });
    });
    
    // Verificar se a aposta é válida antes de enviar
    const betForm = document.querySelector('.bet-form');
    if (betForm) {
        betForm.addEventListener('submit', function(e) {
            const homeScore = document.getElementById('id_home_score_bet').value;
            const awayScore = document.getElementById('id_away_score_bet').value;
            
            if (homeScore === '' || awayScore === '') {
                e.preventDefault();
                alert('Por favor, preencha os placares para ambos os times.');
            }
        });
    }
    
    // Inicializar cronômetro regressivo
    initCountdown();
});

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
            document.querySelector('.days').textContent = '00';
            document.querySelector('.hours').textContent = '00';
            document.querySelector('.minutes').textContent = '00';
            document.querySelector('.seconds').textContent = '00';
            
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
                countdownContainer.innerHTML = '<div class="alert alert-danger mb-0">Tempo para apostar esgotado!</div>';
            }
            
            return;
        }
        
        // Calcular dias, horas, minutos e segundos
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        // Atualizar os números no cronômetro
        document.querySelector('.days').textContent = days.toString().padStart(2, '0');
        document.querySelector('.hours').textContent = hours.toString().padStart(2, '0');
        document.querySelector('.minutes').textContent = minutes.toString().padStart(2, '0');
        document.querySelector('.seconds').textContent = seconds.toString().padStart(2, '0');
        
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