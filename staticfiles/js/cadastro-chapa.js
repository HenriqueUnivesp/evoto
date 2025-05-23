document.addEventListener('DOMContentLoaded', function() {
    // Inicialização da funcionalidade de upload de imagem
    inicializarUploadImagem();
    
    // Inicialização da funcionalidade de adicionar membros
    inicializarAdicionarMembros();
    
    // Validação do formulário
    validarFormulario();
});

function inicializarUploadImagem() {
    const btnUpload = document.getElementById('btn-upload-foto');
    const inputFoto = document.getElementById('foto-presidente');
    const previewContainer = document.getElementById('preview-foto-presidente');
    const previewImage = document.getElementById('img-preview');
    
    if (!btnUpload || !inputFoto || !previewContainer || !previewImage) return;
    
    btnUpload.addEventListener('click', function() {
        inputFoto.click();
    });
    
    inputFoto.addEventListener('change', function() {
        const file = this.files[0];
        
        if (file) {
            const reader = new FileReader();
            
            reader.addEventListener('load', function() {
                previewImage.setAttribute('src', this.result);
                previewImage.style.display = 'block';
                previewContainer.classList.add('has-image');
            });
            
            reader.readAsDataURL(file);
        } else {
            previewImage.setAttribute('src', '');
            previewImage.style.display = 'none';
            previewContainer.classList.remove('has-image');
        }
    });
}

function inicializarAdicionarMembros() {
    const addMembroBtn = document.getElementById('add-membro-btn');
    const membrosContainer = document.getElementById('membros-adicionais-container');
    
    if (!addMembroBtn || !membrosContainer) return;
    
    let membroCount = 0;
    
    addMembroBtn.addEventListener('click', function() {
        membroCount++;
        
        const membroDiv = document.createElement('div');
        membroDiv.className = 'membro-adicional';
        membroDiv.dataset.membroId = membroCount;
        
        membroDiv.innerHTML = `
            <button type="button" class="remove-membro" data-membro-id="${membroCount}">×</button>
            <div class="form-row">
                <div class="form-col">
                    <div class="form-group">
                        <label for="nome-membro-${membroCount}" class="required-label">Nome do Membro</label>
                        <input type="text" id="nome-membro-${membroCount}" name="membros_nome[]" class="form-control" required>
                    </div>
                </div>
                <div class="form-col">
                    <div class="form-group">
                        <label for="cargo-membro-${membroCount}" class="required-label">Cargo na Chapa</label>
                        <input type="text" id="cargo-membro-${membroCount}" name="membros_cargo[]" class="form-control" placeholder="Ex: Secretário, Tesoureiro, etc" required>
                    </div>
                </div>
            </div>
            <div class="form-row">
                <div class="form-col">
                    <div class="form-group">
                        <label for="serie-membro-${membroCount}" class="required-label">Série/Turma</label>
                        <input type="text" id="serie-membro-${membroCount}" name="membros_serie[]" class="form-control" placeholder="Ex: 2º Ano C" required>
                    </div>
                </div>
                <div class="form-col">
                    <div class="form-group">
                        <label for="matricula-membro-${membroCount}" class="required-label">Número de Matrícula</label>
                        <input type="text" id="matricula-membro-${membroCount}" name="membros_matricula[]" class="form-control" required>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="email-membro-${membroCount}" class="required-label">E-mail</label>
                <input type="email" id="email-membro-${membroCount}" name="membros_email[]" class="form-control" required>
            </div>
        `;
        
        membrosContainer.appendChild(membroDiv);
        
        // Adicionar evento para o botão de remover
        const removeBtn = membroDiv.querySelector('.remove-membro');
        removeBtn.addEventListener('click', function() {
            const membroId = this.dataset.membroId;
            const membroToRemove = document.querySelector(`.membro-adicional[data-membro-id="${membroId}"]`);
            if (membroToRemove) {
                membrosContainer.removeChild(membroToRemove);
            }
        });
    });
}

function validarFormulario() {
    const form = document.getElementById('cadastro-chapa-form');
    
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        let valid = true;
        
        // Verificar campos obrigatórios
        const requiredInputs = form.querySelectorAll('[required]');
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                valid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        // Validar número da chapa (2 dígitos)
        const numeroChapa = document.getElementById('numero-chapa');
        if (numeroChapa && (numeroChapa.value < 10 || numeroChapa.value > 99)) {
            numeroChapa.classList.add('is-invalid');
            valid = false;
        }
        
        // Validar propostas (pelo menos 3)
        const propostasField = document.getElementById('propostas');
        if (propostasField) {
            const propostas = propostasField.value.split('\n').filter(linha => linha.trim() !== '');
            if (propostas.length < 3) {
                propostasField.classList.add('is-invalid');
                alert('É necessário informar pelo menos 3 propostas.');
                valid = false;
            } else {
                propostasField.classList.remove('is-invalid');
            }
        }
        
        // Verificar aceite dos termos
        const aceiteTermos = document.getElementById('aceite-termos');
        if (aceiteTermos && !aceiteTermos.checked) {
            aceiteTermos.classList.add('is-invalid');
            alert('É necessário aceitar os termos para prosseguir.');
            valid = false;
        } else if (aceiteTermos) {
            aceiteTermos.classList.remove('is-invalid');
        }
        
        if (!valid) {
            event.preventDefault();
            // Scroll para o primeiro campo com erro
            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });
}