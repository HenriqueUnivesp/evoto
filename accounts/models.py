from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    """Define um model manager para User com email como identificador único."""

    def create_user(self, email, username, nome_completo, password=None, **extra_fields):
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            username=username,
            nome_completo=nome_completo,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, nome_completo, password=None, **extra_fields):
        """Cria e salva um superusuário com o email e senha fornecidos."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, nome_completo, password, **extra_fields)


class CustomUser(AbstractUser):
    """Modelo de usuário personalizado para permitir diferentes tipos e informações"""
    
    TIPO_CHOICES = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('diretor', 'Diretor'),
    )
    
    # Campos básicos
    email = models.EmailField(unique=True, verbose_name='Email')
    username = models.CharField(max_length=150, unique=True, verbose_name='Nome de usuário')
    nome_completo = models.CharField(max_length=255, verbose_name='Nome completo')
    
    # Tipo de usuário
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_CHOICES, default='aluno', verbose_name='Tipo de usuário')
    
    # Campos específicos para alunos
    matricula = models.CharField(max_length=20, blank=True, null=True, verbose_name='Matrícula')
    serie = models.CharField(max_length=20, blank=True, null=True, verbose_name='Série/Turma')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_staff = models.BooleanField(default=False, verbose_name='Equipe')
    
    # Metadados
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')
    ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última atualização')
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome_completo']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        
    def __str__(self):
        return f"{self.nome_completo} ({self.get_tipo_usuario_display()})"
    
    def is_aluno(self):
        return self.tipo_usuario == 'aluno'
    
    def is_professor(self):
        return self.tipo_usuario == 'professor'
    
    def is_diretor(self):
        return self.tipo_usuario == 'diretor'