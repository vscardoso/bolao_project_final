function copyInviteLink() {
    const inviteLinkInput = document.getElementById('inviteLink');
    
    if (!inviteLinkInput) {
        console.error('Elemento de input não encontrado');
        return;
    }
    
    // Seleciona o texto
    inviteLinkInput.select();
    inviteLinkInput.setSelectionRange(0, 99999);
    
    // Copia para a área de transferência
    try {
        const successful = document.execCommand('copy');
        
        // Mostra um feedback
        const feedbackMessage = successful ? 
            'Link copiado para a área de transferência!' : 
            'Não foi possível copiar o link';
            
        // Exibe mensagem usando o sistema de alertas do Bootstrap
        showAlert(feedbackMessage, successful ? 'success' : 'danger');
    } catch (err) {
        console.error('Erro ao copiar texto: ', err);
        showAlert('Erro ao copiar o link', 'danger');
    }
    
    // Remove a seleção
    window.getSelection().removeAllRanges();
}

function showAlert(message, type = 'info') {
    // Cria um elemento de alerta
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertEl.setAttribute('role', 'alert');
    alertEl.style.zIndex = '9999';
    
    // Adiciona o conteúdo
    alertEl.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Adiciona ao corpo do documento
    document.body.appendChild(alertEl);
    
    // Remove após 3 segundos
    setTimeout(() => {
        if (alertEl.parentNode) {
            const bsAlert = new bootstrap.Alert(alertEl);
            bsAlert.close();
        }
    }, 3000);
}

// Compartilhar via redes sociais
function shareViaWhatsApp(link, poolName) {
    const text = encodeURIComponent(`Junte-se ao bolão "${poolName}" no Bolão Online: ${link}`);
    window.open(`https://wa.me/?text=${text}`, '_blank');
}

function shareViaTelegram(link, poolName) {
    const text = encodeURIComponent(`Junte-se ao bolão "${poolName}" no Bolão Online: ${link}`);
    window.open(`https://t.me/share/url?url=${link}&text=${text}`, '_blank');
}

function shareViaEmail(link, poolName) {
    const subject = encodeURIComponent(`Convite para o bolão "${poolName}"`);
    const body = encodeURIComponent(`Olá!\n\nGostaria de convidar você para participar do bolão "${poolName}" na plataforma Bolão Online.\n\nClique no link abaixo para participar:\n${link}\n\nAté mais!`);
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
}

// Inicializa todos os elementos que precisam de inicialização quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa botões de compartilhamento
    const shareButtons = document.querySelectorAll('[data-share-type]');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const type = this.getAttribute('data-share-type');
            const link = this.getAttribute('data-share-link');
            const poolName = this.getAttribute('data-share-name');
            
            switch(type) {
                case 'whatsapp':
                    shareViaWhatsApp(link, poolName);
                    break;
                case 'telegram':
                    shareViaTelegram(link, poolName);
                    break;
                case 'email':
                    shareViaEmail(link, poolName);
                    break;
            }
        });
    });
    
    // Inicializa botões de copiar
    const copyButtons = document.querySelectorAll('.btn-copy-link');
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            copyInviteLink();
        });
    });
});