document.addEventListener('DOMContentLoaded', function() {
    const tipoUsuarioSelect = document.getElementById('tipo-usuario');
    const camposAluno = document.querySelectorAll('.campo-aluno');
    
    // Função para mostrar/esconder campos específicos de aluno
    function toggleCamposAluno() {
        if (tipoUsuarioSelect && tipoUsuarioSelect.value === 'aluno') {
            camposAluno.forEach(campo => campo.style.display = 'block');
        } else {
            camposAluno.forEach(campo => campo.style.display = 'none');
        }
    }
    
    // Executar a função ao carregar a página e quando o select mudar
    if (tipoUsuarioSelect) {
        toggleCamposAluno();
        tipoUsuarioSelect.addEventListener('change', toggleCamposAluno);
    }
});