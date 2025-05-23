// form_eleicao.js - JavaScript para formulário de criação de eleição

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar variáveis e elementos do DOM
    const form = document.getElementById('criar-eleicao-form');
    const fileInput = document.getElementById('id_imagem');
    
    // Validação do formulário de eleição
    if (form) {
        form.addEventListener('submit', function(event) {
            const dataInicio = new Date(document.getElementById('id_data_inicio').value);
            const dataFim = new Date(document.getElementById('id_data_fim').value);
            
            let hasError = false;
            
            // Validar se a data de término é posterior à data de início
            if (dataFim <= dataInicio) {
                alert('A data de término deve ser posterior à data de início.');
                event.preventDefault();
                hasError = true;
            }
        });
    }
    
    // Preview de imagem para upload de foto
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.createElement('img');
                    preview.src = e.target.result;
                    preview.style.maxWidth = '100px';
                    preview.style.marginTop = '10px';
                    
                    // Remover preview anterior se existir
                    const parent = fileInput.parentNode;
                    const oldPreview = parent.querySelector('img');
                    if (oldPreview) {
                        parent.removeChild(oldPreview);
                    }
                    
                    parent.appendChild(preview);
                };
                reader.readAsDataURL(file);
            }
        });
    }
});