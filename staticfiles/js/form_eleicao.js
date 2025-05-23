// JavaScript para a página de criação de eleição
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar variáveis globais
    let chapas = [];
    let chapaEmEdicao = null;
    
    // Elementos DOM
    const listaChapas = document.getElementById('lista-chapas');
    const formCadastroChapa = document.getElementById('cadastro-chapa-form');
    const btnAdicionarChapa = document.getElementById('adicionar-chapa-btn');
    const btnFinalizarEleicao = document.getElementById('finalizar-eleicao-btn');
    const totalChapasBadge = document.getElementById('total-chapas-badge');
    const alertContainer = document.getElementById('alert-container');
    const semChapas = document.getElementById('sem-chapas');
    
    // Elementos de upload de foto
    const uploadBtn = document.getElementById('btn-upload-foto');
    const fileInput = document.getElementById('foto-presidente');
    const imgPreview = document.getElementById('img-preview');
    
    // Inicializar eventos se os elementos existirem
    if (uploadBtn && fileInput) {
        // Evento para botão de upload de foto
        uploadBtn.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Evento para mudança no input de arquivo
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    imgPreview.src = e.target.result;
                    imgPreview.style.display = 'block';
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Evento para adicionar chapa
    if (btnAdicionarChapa) {
        btnAdicionarChapa.addEventListener('click', adicionarChapa);
    }
    
    // Evento para finalizar eleição
    if (btnFinalizarEleicao) {
        btnFinalizarEleicao.addEventListener('click', finalizarEleicao);
    }
    
    // Funções para gerenciar chapas
    function exibirAlerta(mensagem, tipo) {
        if (!alertContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${tipo}`;
        alert.textContent = mensagem;
        
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alert);
        
        // Remover o alerta após 5 segundos
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
    
    function atualizarListaChapas() {
        if (!listaChapas || !totalChapasBadge || !semChapas) return;
        
        // Atualizar o contador de chapas
        totalChapasBadge.textContent = chapas.length;
        
        // Mostrar ou esconder a mensagem "sem chapas"
        if (chapas.length === 0) {
            semChapas.style.display = 'block';
            return;
        } else {
            semChapas.style.display = 'none';
        }
        
        // Limpar a lista atual
        listaChapas.innerHTML = '';
        
        // Adicionar cada chapa à lista
        chapas.forEach((chapa, index) => {
            const chapaElement = document.createElement('div');
            chapaElement.className = 'chapa-item';
            
            chapaElement.innerHTML = `
                <div class="chapa-info">
                    <div class="chapa-nome">${chapa.numero} - ${chapa.nome}</div>
                    <div>Candidato: ${chapa.presidente.nome} | Slogan: ${chapa.slogan}</div>
                </div>
                <div class="chapa-actions">
                    <button class="btn btn-warning btn-sm btn-editar" data-index="${index}">Editar</button>
                    <button class="btn btn-danger btn-sm btn-remover" data-index="${index}">Remover</button>
                </div>
            `;
            
            listaChapas.appendChild(chapaElement);
        });
        
        // Adicionar event listeners aos botões
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                editarChapa(index);
            });
        });
        
        document.querySelectorAll('.btn-remover').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                removerChapa(index);
            });
        });
    }
    
    function coletarDadosFormulario() {
        if (!formCadastroChapa) return null;
        
        // Validar campos obrigatórios
        const campos = [
            'nome-chapa', 'numero-chapa', 'slogan', 
            'nome-presidente', 'serie-presidente', 'matricula-presidente',
            'email-presidente', 'telefone-presidente', 'propostas'
        ];
        
        for (const campo of campos) {
            const elemento = document.getElementById(campo);
            if (!elemento || !elemento.value.trim()) {
                exibirAlerta(`O campo ${elemento ? elemento.labels[0].textContent.replace(' *', '') : campo} é obrigatório.`, 'danger');
                if (elemento) elemento.focus();
                return null;
            }
        }
        
        // Validar propostas (mínimo 3)
        const propostas = document.getElementById('propostas').value.trim().split('\n').filter(p => p.trim());
        if (propostas.length < 3) {
            exibirAlerta('É necessário informar pelo menos 3 propostas.', 'danger');
            document.getElementById('propostas').focus();
            return null;
        }
        
        // Validar foto do candidato
        if (!imgPreview.src && !chapaEmEdicao) {
            exibirAlerta('É necessário selecionar uma foto para o candidato.', 'danger');
            return null;
        }
        
        // Coletar os dados
        return {
            nome: document.getElementById('nome-chapa').value.trim(),
            numero: document.getElementById('numero-chapa').value.trim(),
            slogan: document.getElementById('slogan').value.trim(),
            presidente: {
                nome: document.getElementById('nome-presidente').value.trim(),
                serie: document.getElementById('serie-presidente').value.trim(),
                matricula: document.getElementById('matricula-presidente').value.trim(),
                email: document.getElementById('email-presidente').value.trim(),
                telefone: document.getElementById('telefone-presidente').value.trim(),
                foto: imgPreview.src || (chapaEmEdicao ? chapaEmEdicao.presidente.foto : '')
            },
            propostas: propostas
        };
    }
    
    function limparFormulario() {
        if (!formCadastroChapa) return;
        
        formCadastroChapa.reset();
        if (imgPreview) {
            imgPreview.src = '';
            imgPreview.style.display = 'none';
        }
        chapaEmEdicao = null;
        if (btnAdicionarChapa) {
            btnAdicionarChapa.textContent = 'Adicionar Esta Chapa';
        }
    }
    
    function adicionarChapa() {
        const dados = coletarDadosFormulario();
        if (!dados) return;
        
        // Verificar se já existe uma chapa com o mesmo número
        const chapaExistente = chapas.find(c => c.numero === dados.numero && c !== chapaEmEdicao);
        if (chapaExistente) {
            exibirAlerta(`Já existe uma chapa com o número ${dados.numero}.`, 'danger');
            return;
        }
        
        if (chapaEmEdicao) {
            // Atualizar a chapa existente
            const index = chapas.findIndex(c => c === chapaEmEdicao);
            chapas[index] = dados;
            exibirAlerta(`Chapa "${dados.nome}" atualizada com sucesso!`, 'success');
        } else {
            // Adicionar nova chapa
            chapas.push(dados);
            exibirAlerta(`Chapa "${dados.nome}" adicionada com sucesso!`, 'success');
        }
        
        // Atualizar a lista e limpar o formulário
        atualizarListaChapas();
        limparFormulario();
    }
    
    function editarChapa(index) {
        chapaEmEdicao = chapas[index];
        
        // Preencher o formulário com os dados da chapa
        document.getElementById('nome-chapa').value = chapaEmEdicao.nome;
        document.getElementById('numero-chapa').value = chapaEmEdicao.numero;
        document.getElementById('slogan').value = chapaEmEdicao.slogan;
        
        document.getElementById('nome-presidente').value = chapaEmEdicao.presidente.nome;
        document.getElementById('serie-presidente').value = chapaEmEdicao.presidente.serie;
        document.getElementById('matricula-presidente').value = chapaEmEdicao.presidente.matricula;
        document.getElementById('email-presidente').value = chapaEmEdicao.presidente.email;
        document.getElementById('telefone-presidente').value = chapaEmEdicao.presidente.telefone;
        
        document.getElementById('propostas').value = chapaEmEdicao.propostas.join('\n');
        
        if (chapaEmEdicao.presidente.foto && imgPreview) {
            imgPreview.src = chapaEmEdicao.presidente.foto;
            imgPreview.style.display = 'block';
        }
        
        if (btnAdicionarChapa) {
            btnAdicionarChapa.textContent = 'Atualizar Esta Chapa';
        }
        
        // Rolar até o formulário
        formCadastroChapa.scrollIntoView({ behavior: 'smooth' });
    }
    
    function removerChapa(index) {
        const chapa = chapas[index];
        if (confirm(`Tem certeza que deseja remover a chapa "${chapa.nome}"?`)) {
            chapas.splice(index, 1);
            atualizarListaChapas();
            exibirAlerta(`Chapa "${chapa.nome}" removida com sucesso!`, 'success');
            
            // Se a chapa em edição foi removida, limpar o formulário
            if (chapaEmEdicao === chapa) {
                limparFormulario();
            }
        }
    }
    
    function finalizarEleicao() {
        // Verificar se há chapas cadastradas
        if (chapas.length === 0) {
            alert("Você deve cadastrar pelo menos uma chapa antes de finalizar a eleição.");
            return;
        }
        
        // Enviar as chapas para o servidor via AJAX
        const eleicaoId = new URLSearchParams(window.location.search).get('eleicao_id');
        if (!eleicaoId) {
            // Se estamos criando uma nova eleição, submeter o formulário
            document.getElementById('criar-eleicao-form').submit();
            return;
        }
        
        // Enviar as chapas para o servidor
        fetch(`/election/processar-chapas/${eleicaoId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ chapas: chapas })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                window.location.href = `/election/gerenciar-chapas/${eleicaoId}/`;
            } else {
                alert(`Erro: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Ocorreu um erro ao processar as chapas. Verifique o console para mais detalhes.');
        });
    }
    
    // Função para obter o valor de um cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Inicializar a lista de chapas se existir
    if (listaChapas) {
        atualizarListaChapas();
    }
});