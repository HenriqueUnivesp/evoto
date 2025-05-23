from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import CustomUser

class CustomAuthenticationForm(AuthenticationForm):
    """Formulário de login personalizado"""
    
    # Renomeando o campo username para aceitar também nome de usuário ou RA
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome de usuário ou RA'}),
        label='Nome de usuário / RA'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}),
        label='Senha'
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class CustomUserCreationForm(UserCreationForm):
    """Formulário para criação de usuário"""
    
    # Campos comuns para todos os tipos de usuário
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu email'}),
        label='Email'
    )
    
    nome_completo = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome completo'}),
        label='Nome completo'
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome de usuário ou RA'}),
        label='Nome de usuário / RA'
    )
    
    tipo_usuario = forms.ChoiceField(
        choices=CustomUser.TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'tipo-usuario'}),
        label='Tipo de usuário'
    )
    
    # Campos específicos para alunos
    matricula = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua matrícula'}),
        label='Matrícula'
    )
    
    serie = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua série/turma'}),
        label='Série/Turma'
    )
    
    # Campos de senha
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}),
        label='Senha'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'}),
        label='Confirme a senha'
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'nome_completo', 'username', 'tipo_usuario',
            'matricula', 'serie', 'password1', 'password2'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos obrigatórios para UserCreationForm
        self.fields['password1'].help_text = 'A senha deve ter pelo menos 8 caracteres e não pode ser similar às suas informações pessoais.'
        self.fields['password2'].help_text = 'Digite a mesma senha novamente para verificação.'
    
    # A validação de CPF foi removida
    
    def clean(self):
        """Validação específica para diferentes tipos de usuário"""
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        matricula = cleaned_data.get('matricula')
        serie = cleaned_data.get('serie')
        
        # Verifica se o nome de usuário foi preenchido
        if not cleaned_data.get('username'):
            self.add_error('username', 'Nome de usuário é obrigatório.')
        
        # Verifica se aluno preencheu matrícula e série
        if tipo_usuario == 'aluno':
            if not matricula:
                self.add_error('matricula', 'Matrícula é obrigatória para alunos.')
            if not serie:
                self.add_error('serie', 'Série/Turma é obrigatória para alunos.')
        
        return cleaned_data