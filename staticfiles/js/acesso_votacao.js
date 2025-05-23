// JavaScript para a página de acesso à votação

document.addEventListener('DOMContentLoaded', function() {
    // Animar entrada dos cards de eleição
    const cards = document.querySelectorAll('.eleicao-card');
    
    // Aplicar animação com pequeno delay entre cada card
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
    
    // Adicionar feedback visual ao clicar nos botões
    const actionButtons = document.querySelectorAll('.actions-container .btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Adiciona classe para animação de click
            this.classList.add('btn-clicked');
            
            // Remove a classe após a animação
            setTimeout(() => {
                this.classList.remove('btn-clicked');
            }, 300);
        });
    });
    
    // Adicionar verificação para exibir mensagem de confirmação em ações críticas
    const adminButtons = document.querySelectorAll('.btn-success, .btn-danger');
    
    adminButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.dataset.confirm === 'true') {
                if (!confirm('Tem certeza que deseja realizar esta ação?')) {
                    e.preventDefault();
                }
            }
        });
    });
});

// Melhorar interatividade das cards
function setupCardInteractions() {
    const cards = document.querySelectorAll('.eleicao-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
        });
    });
}

// Inicializar interações quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupCardInteractions);
} else {
    setupCardInteractions();
}