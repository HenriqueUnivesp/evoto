/**
 * votacao.js - Script para funcionalidades da página de votação
 */

document.addEventListener('DOMContentLoaded', function() {
    // Atualiza o contador regressivo
    atualizarContadorRegressivo();
});

/**
 * Atualiza o contador regressivo da votação
 */
function atualizarContadorRegressivo() {
    // Elemento que contém a contagem regressiva
    const timerElement = document.querySelector('.timer-count');
    
    // Verifica se o elemento existe e se tem a data final
    if (timerElement && timerElement.getAttribute('data-data-fim')) {
        // Obtém a data final da votação
        const dataFim = new Date(timerElement.getAttribute('data-data-fim'));
        
        // Função para atualizar o contador
        function atualizarContagem() {
            // Data e hora atual
            const agora = new Date();
            
            // Diferença em milissegundos
            let diferenca = dataFim - agora;
            
            // Se a votação já terminou
            if (diferenca <= 0) {
                timerElement.textContent = 'Votação encerrada';
                return;
            }
            
            // Cálculo dos valores
            const dias = Math.floor(diferenca / (1000 * 60 * 60 * 24));
            diferenca -= dias * (1000 * 60 * 60 * 24);
            
            const horas = Math.floor(diferenca / (1000 * 60 * 60));
            diferenca -= horas * (1000 * 60 * 60);
            
            const minutos = Math.floor(diferenca / (1000 * 60));
            diferenca -= minutos * (1000 * 60);
            
            const segundos = Math.floor(diferenca / 1000);
            
            // Atualiza o texto com formatação
            timerElement.textContent = `${dias}d ${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
        }
        
        // Executa imediatamente e depois a cada segundo
        atualizarContagem();
        setInterval(atualizarContagem, 1000);
    }
}