/**
 * Timer de inatividade para logout automático
 * Monitora a atividade do usuário e desloga após um período de inatividade
 */

class InactivityTimer {
    constructor(options = {}) {
        // Tempo de inatividade em minutos (padrão: 2 minutos)
        this.timeout = (options.timeout || 2) * 60 * 1000;
        
        // URL para logout (padrão: '/accounts/logout/')
        this.logoutUrl = options.logoutUrl || '/accounts/logout/';
        
        // Tempo de aviso antes do logout em segundos (padrão: 60 segundos)
        this.warningTime = (options.warningTime || 60) * 1000;
        
        // Se deve mostrar modal de aviso (padrão: true)
        this.showWarning = options.showWarning !== undefined ? options.showWarning : true;
        
        // Contador de tempo 
        this.timer = null;
        
        // Contador de aviso
        this.warningTimer = null;
        
        // Estado
        this.isWarningShown = false;
        
        // Inicializa
        this.init();
    }
    
    init() {
        // Reset do timer quando a página carrega
        this.resetTimer();
        
        // Eventos que resetam o timer
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        events.forEach(event => {
            document.addEventListener(event, (e) => {
                // Verificar se o evento ocorreu dentro do modal
                const modal = document.getElementById('inactivityModal');
                const isModalEvent = modal && 
                    (modal.style.display === 'flex') && 
                    (e.target === modal || modal.contains(e.target));
                
                // Só resetar timer se o evento não for no modal de aviso
                if (!isModalEvent) {
                    this.resetTimer();
                }
            });
        });
        
        // Garantir que o timer é reiniciado ao voltar para a página
        window.addEventListener('focus', () => this.resetTimer());
    }
    
    resetTimer() {
        // Limpa timers existentes
        if (this.timer) {
            clearTimeout(this.timer);
        }
        
        if (this.warningTimer) {
            clearTimeout(this.warningTimer);
        }
        
        // Remover aviso se estiver sendo exibido
        if (this.isWarningShown) {
            this.hideWarning();
        }
        
        // Definir novo timer para o aviso
        this.warningTimer = setTimeout(() => {
            this.showWarningMessage();
        }, this.timeout - this.warningTime);
        
        // Definir timer para o logout
        this.timer = setTimeout(() => {
            this.logout();
        }, this.timeout);
    }
    
    showWarningMessage() {
        if (!this.showWarning) return;
        
        this.isWarningShown = true;
        
        // Criar o modal de aviso se não existir
        if (!document.getElementById('inactivityModal')) {
            const modal = document.createElement('div');
            modal.id = 'inactivityModal';
            modal.className = 'inactivity-modal';
            
            modal.innerHTML = `
                <div class="inactivity-modal-content">
                    <h4><i class="fas fa-clock"></i> Aviso de Inatividade</h4>
                    <p>Você será desconectado em <span id="logoutCountdown">60</span> segundos por inatividade.</p>
                    <div class="inactivity-modal-footer">
                        <button id="stayLoggedIn" class="btn btn-primary">Continuar Conectado</button>
                        <button id="logoutNow" class="btn btn-secondary">Sair Agora</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Adicionar estilos ao modal (sem alterações)
            
            // Melhorar os event listeners para os botões
            const self = this; // Armazenar referência ao 'this' para usar dentro dos event listeners
            
            document.getElementById('stayLoggedIn').addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Botão Continuar Conectado clicado');
                self.resetTimer();
            });
            
            document.getElementById('logoutNow').addEventListener('click', function(e) {
                e.preventDefault(); 
                console.log('Botão Sair Agora clicado');
                
                // Ocultar o modal primeiro
                self.hideWarning();
                
                // Adicionar um pequeno delay para garantir que a UI foi atualizada
                setTimeout(function() {
                    console.log('Executando logout após delay...');
                    
                    // Usar uma abordagem mais direta
                    const logoutForm = document.getElementById('logout-form');
                    if (logoutForm) {
                        console.log('Submetendo formulário de logout via click direto');
                        
                        // Criar um botão de submit e clicar nele (mais confiável que form.submit())
                        const submitBtn = document.createElement('input');
                        submitBtn.type = 'submit';
                        submitBtn.style.display = 'none';
                        logoutForm.appendChild(submitBtn);
                        
                        // Simular clique real
                        submitBtn.click();
                        
                        // Remover o botão depois
                        logoutForm.removeChild(submitBtn);
                    } else {
                        // Fallback para o método anterior se o formulário não for encontrado
                        console.log('Formulário não encontrado, tentando método anterior');
                        self.performLogout();
                    }
                }, 200); // Delay de 200ms
            });
        }
        
        // Mostrar o modal
        document.getElementById('inactivityModal').style.display = 'flex';
        
        // Iniciar contagem regressiva (sem alterações)
        let secondsLeft = Math.floor(this.warningTime / 1000);
        const countdownElement = document.getElementById('logoutCountdown');
        
        const countdownInterval = setInterval(() => {
            secondsLeft -= 1;
            if (countdownElement) {
                countdownElement.textContent = secondsLeft;
            }
            
            if (secondsLeft <= 0) {
                clearInterval(countdownInterval);
            }
        }, 1000);
    }
    
    hideWarning() {
        this.isWarningShown = false;
        const modal = document.getElementById('inactivityModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    performLogout() {
        console.log('Executando logout via modal de inatividade');
        
        try {
            // Opção 1: Verificar se já existe um formulário com id "logout-form"
            const logoutForm = document.getElementById('logout-form');
            if (logoutForm) {
                console.log('Formulário de logout encontrado, submetendo...');
                logoutForm.submit();
                return;
            }
            
            // Opção 2: Verificar se existe link com onclick que submete o formulário
            const logoutLinks = document.querySelectorAll('a[onclick*="logout-form"]');
            if (logoutLinks.length > 0) {
                console.log('Link de logout encontrado, simulando clique');
                logoutLinks[0].click();
                return;
            }
            
            // Opção 3: Criar formulário simulando exatamente o padrão que você está usando
            console.log('Criando formulário de logout');
            
            // Criar o formulário de logout se não existir
            const form = document.createElement('form');
            form.id = 'logout-form';
            form.method = 'POST';
            form.action = '/accounts/logout/';
            form.style.display = 'none';
            
            // Adicionar token CSRF
            const csrfToken = this.getCsrfToken();
            if (csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
                
                // Adicionar ao documento e submetê-lo
                document.body.appendChild(form);
                console.log('Formulário criado e sendo submetido');
                form.submit();
            } else {
                console.error('Não foi possível obter o token CSRF para o logout');
                alert('Não foi possível realizar o logout. Por favor, tente novamente ou faça logout manualmente.');
            }
        } catch (error) {
            console.error('Erro ao tentar fazer logout:', error);
        }
    }
    
    getCsrfToken() {
        // Tentar obter de um input existente
        const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfElement) {
            return csrfElement.value;
        }
        
        // Tentar obter do cookie
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.indexOf('csrftoken=') === 0) {
                return cookie.substring('csrftoken='.length);
            }
        }
        
        // Última tentativa: extrair de uma meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
        return null;
    }
    
    logout() {
        // Armazenar URL atual para redirecionamento após login
        if (window.location.pathname !== '/accounts/login/') {
            sessionStorage.setItem('returnUrl', window.location.pathname);
        }
        
        this.performLogout();
    }
}

// Inicializar o timer quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    // Adicione dentro do DOMContentLoaded, antes da verificação userIsLoggedIn
    console.log('Verificando autenticação:');
    console.log('- Classe user-logged-in:', document.body.classList.contains('user-logged-in'));
    console.log('- Elemento .logged-user:', document.querySelector('.logged-user') !== null);
    console.log('- Variável window.isAuthenticated:', window.isAuthenticated);

    // Verificar se o usuário está logado - método mais confiável
    const userIsLoggedIn = document.querySelector('.logged-user') !== null || 
                           document.body.classList.contains('user-logged-in') ||
                           window.isAuthenticated === true;
    
    // Configurações de produção
    if (userIsLoggedIn) {
        window.inactivityTimer = new InactivityTimer({
            timeout: 30,            // 30 minutos
            warningTime: 60,        // 60 segundos de aviso
            logoutUrl: '/accounts/logout/'  // URL correta
        });
        
        console.log('Inactivity timer initialized: 30 minutes');

        // Adicione após inicializar o timer:

        // Verificar se o formulário de logout existe
        console.log('Verificando formulário de logout...');
        const logoutForm = document.getElementById('logout-form');
        if (logoutForm) {
            console.log('Formulário de logout encontrado:', logoutForm);
        } else {
            console.log('Formulário de logout NÃO encontrado. Verificando links alternados...');
            const logoutLinks = document.querySelectorAll('a[onclick*="logout-form"], a[href*="logout"]');
            console.log('Links de logout encontrados:', logoutLinks.length);
            
            if (logoutLinks.length > 0) {
                logoutLinks.forEach(link => {
                    console.log(' - Link:', link.outerHTML);
                });
            }
        }
    } else {
        console.log('User not logged in, timer not initialized');
    }
});