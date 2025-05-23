from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser

def register_view(request):
    """View para registro de novos usuários"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('home')  # Redireciona para a página inicial após o cadastro
        else:
            print(f"Erros no formulário: {form.errors}")  # Para depuração
            messages.error(request, 'Corrija os erros no formulário para continuar.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """View para login de usuários"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        print(f"Form errors: {form.errors}")
        
        # Obtém os dados do formulário, independentemente da validação
        username_or_email = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        print(f"Tentando login com: {username_or_email}")
        
        # Método personalizado de autenticação
        user = None
        
        # 1. Busca usuário pelo nome de usuário, email ou matrícula
        try:
            # Busca o usuário por algum dos campos
            user_obj = CustomUser.objects.filter(
                Q(username=username_or_email) | 
                Q(email=username_or_email) | 
                Q(matricula=username_or_email)
            ).first()
            
            if user_obj:
                print(f"Usuário encontrado: {user_obj.username}")
                # Verifica a senha manualmente
                if user_obj.check_password(password):
                    user = user_obj
                    print("Senha verificada com sucesso!")
            else:
                print("Usuário não encontrado")
                
        except Exception as e:
            print(f"Erro durante a autenticação: {e}")
            
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.nome_completo}!')
            
            # Redireciona para a página que o usuário estava tentando acessar, ou para a página inicial
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, 'Nome de usuário, email, RA ou senha inválidos.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """View para logout de usuários"""
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso.')
    return redirect('home')

@login_required
def profile_view(request):
    """View para exibir e editar o perfil do usuário"""
    return render(request, 'accounts/profile.html', {'user': request.user})