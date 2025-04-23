// Contador regressivo para o próximo evento
document.addEventListener('DOMContentLoaded', function() {
    // Set the date we're counting down to (exemplo: 15 dias a partir de agora)
    const countDownDate = new Date();
    countDownDate.setDate(countDownDate.getDate() + 15);
    
    // Update the count down every 1 second
    const x = setInterval(function() {
        // Get today's date and time
        const now = new Date().getTime();
        
        // Find the distance between now and the count down date
        const distance = countDownDate - now;
        
        // Time calculations for days, hours, minutes and seconds
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        // Update elements if they exist
        if (document.getElementById("days")) document.getElementById("days").innerHTML = days;
        if (document.getElementById("hours")) document.getElementById("hours").innerHTML = hours;
        if (document.getElementById("minutes")) document.getElementById("minutes").innerHTML = minutes;
        if (document.getElementById("seconds")) document.getElementById("seconds").innerHTML = seconds;
        
        // If the count down is finished, write some text
        if (distance < 0) {
            clearInterval(x);
            const countdownContainers = document.querySelectorAll('.countdown-container');
            countdownContainers.forEach(container => {
                container.innerHTML = "<p class='h5'>O evento já começou!</p>";
            });
        }
    }, 1000);
    
    // Animação suave para os contadores
    const counters = document.querySelectorAll('.stat-counter');
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        let count = 0;
        const speed = Math.ceil(target / 30); // Ajustar velocidade baseado no valor
        
        const updateCount = () => {
            if (count < target) {
                count += speed;
                if (count > target) count = target;
                counter.innerText = count;
                setTimeout(updateCount, 60);
            }
        }
        
        updateCount();
    });
    
    // Smooth scroll para âncoras
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Ativar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Detectar aparição de elementos na tela
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeIn');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.highlight-card, .feature-card, .testimonial-card').forEach(elem => {
        observer.observe(elem);
    });

    // Filtro de esportes
    const sportButtons = document.querySelectorAll('#sportsFilter button');
    const sportFilterMobile = document.getElementById('sportFilterMobile');
    const gameCards = document.querySelectorAll('.game-card');
    
    function filterSports(sport) {
        gameCards.forEach(card => {
            if (card.dataset.sport === sport) {
                card.classList.remove('d-none');
            } else {
                card.classList.add('d-none');
            }
        });
    }
    
    sportButtons.forEach(button => {
        button.addEventListener('click', function() {
            sportButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            filterSports(this.dataset.sport);
            
            if (sportFilterMobile) {
                sportFilterMobile.value = this.dataset.sport;
            }
        });
    });
    
    if (sportFilterMobile) {
        sportFilterMobile.addEventListener('change', function() {
            filterSports(this.value);
            
            sportButtons.forEach(btn => {
                if (btn.dataset.sport === this.value) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        });
    }
    
    // Contagem regressiva para jogos
    const countdownElements = document.querySelectorAll('.countdown-mini');
    countdownElements.forEach(element => {
        const targetDate = new Date(element.dataset.time).getTime();
        
        const updateCountdown = function() {
            const now = new Date().getTime();
            const distance = targetDate - now;
            
            if (distance < 0) {
                element.innerHTML = 'Iniciando...';
                return;
            }
            
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            
            element.innerHTML = `Começa em: ${hours}h ${minutes}m`;
        };
        
        updateCountdown();
        setInterval(updateCountdown, 60000); // Atualiza a cada minuto
    });
    
    // Botões de lembrete
    const reminderButtons = document.querySelectorAll('.reminder-btn');
    reminderButtons.forEach(button => {
        button.addEventListener('click', function() {
            const gameId = this.dataset.gameId;
            const reminderText = this.querySelector('.reminder-text');
            
            if (reminderText.textContent === 'Lembrar deste jogo') {
                reminderText.textContent = 'Lembrete ativado';
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-success');
                // Aqui você adicionaria lógica para salvar o lembrete
            } else {
                reminderText.textContent = 'Lembrar deste jogo';
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-primary');
                // Aqui você removeria o lembrete
            }
        });
    });
});