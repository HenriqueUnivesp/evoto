document.addEventListener('DOMContentLoaded', function() {
    // Animar as barras de votação quando a página carregar
    animarBarrasDeResultado();
    
    // Adicionar efeitos visuais extras
    adicionarEfeitosVisuais();
});

function animarBarrasDeResultado() {
    const barras = document.querySelectorAll('.vote-bar');
    
    barras.forEach(barra => {
        // Obtém a largura que a barra deve ter
        const percentual = barra.dataset.percentual || '0';
        
        // Primeiro define como 0 para poder animar
        barra.style.width = '0%';
        
        // Após um pequeno atraso, anima para o valor correto
        setTimeout(() => {
            barra.style.width = percentual + '%';
        }, 100);
    });
}

function adicionarEfeitosVisuais() {
    // Destacar a chapa vencedora com uma animação sutil
    const vencedor = document.querySelector('.result-winner');
    if (vencedor) {
        setTimeout(() => {
            vencedor.classList.add('show-winner');
        }, 500);
    }
    
    // Adicionar efeito de ordenação (opcional, para resultados que mudam em tempo real)
    const resultCards = document.querySelectorAll('.result-card');
    if (resultCards.length > 1) {
        resultCards.forEach((card, index) => {
            card.style.transitionDelay = (index * 0.1) + 's';
        });
    }
}

// Funções para exportar resultados (se necessário)
function exportarResultadosPDF() {
    alert('Exportação para PDF seria implementada aqui.');
    // Aqui implementaria a exportação real para PDF usando uma biblioteca como jsPDF
}

function exportarResultadosCSV() {
    const eleicaoTitulo = document.querySelector('.results-title').textContent;
    const data = [];
    
    // Cabeçalho
    data.push(['Posição', 'Chapa', 'Número', 'Votos', 'Percentual']);
    
    // Dados das chapas
    document.querySelectorAll('.result-card').forEach((card, index) => {
        const posicao = index + 1;
        const nome = card.querySelector('.chapa-meta h4')?.textContent || '';
        const numero = card.querySelector('.chapa-number')?.textContent.replace('Chapa nº ', '') || '';
        const votos = card.querySelector('.total-votes')?.textContent.replace(' votos', '') || '';
        const percentual = card.querySelector('.percentage')?.textContent.replace('%', '') || '';
        
        data.push([posicao, nome, numero, votos, percentual]);
    });
    
    // Converter para formato CSV
    let csvContent = "data:text/csv;charset=utf-8,";
    
    data.forEach(row => {
        csvContent += row.join(',') + '\r\n';
    });
    
    // Criar link para download
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Resultados - ${eleicaoTitulo}.csv`);
    document.body.appendChild(link);
    
    // Acionar o download e remover o link
    link.click();
    document.body.removeChild(link);
}