document.addEventListener('DOMContentLoaded', function() {
    // Verificar se há eleições ativas
    checkActiveElections();
    
    // Adicionar animações aos cards
    animateCards();
    
    // Contador regressivo para a próxima eleição (se houver)
    initCountdown();
});

function checkActiveElections() {
    // Esta função pode ser expandida para verificar via AJAX se há eleições ativas
    // Por enquanto, apenas adiciona uma classe visual se houver o elemento
    const proximaEleicao = document.querySelector('.proxima-eleicao');
    if (proximaEleicao) {
        proximaEleicao.classList.add('active-election');
    }
}

function animateCards() {
    // Adiciona classe de animação aos cards à medida que aparecem na viewport
    const cards = document.querySelectorAll('.card');
    
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        observer.observe(card);
    });
}

function initCountdown() {
    // Verifica se há um elemento com data de eleição para iniciar o contador
    const dataTerminoElement = document.querySelector('[data-countdown]');
    
    if (!dataTerminoElement) return;
    
    const dataTermino = new Date(dataTerminoElement.getAttribute('data-countdown'));
    
    if (isNaN(dataTermino.getTime())) return;
    
    const countdownElement = document.getElementById('countdown');
    if (!countdownElement) return;
    
    // Atualiza o contador a cada segundo
    const interval = setInterval(() => {
        const agora = new Date();
        const diff = dataTermino - agora;
        
        if (diff <= 0) {
            clearInterval(interval);
            countdownElement.innerHTML = 'Votação encerrada';
            return;
        }
        
        const dias = Math.floor(diff / (1000 * 60 * 60 * 24));
        const horas = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutos = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const segundos = Math.floor((diff % (1000 * 60)) / 1000);
        
        countdownElement.innerHTML = `${dias}d ${horas}h ${minutos}m ${segundos}s`;
    }, 1000);
}