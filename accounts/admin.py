from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'nome_completo', 'tipo_usuario', 'is_active', 'is_staff']
    list_filter = ['tipo_usuario', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'nome_completo']
    ordering = ['nome_completo']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informações Pessoais', {'fields': ('nome_completo', 'tipo_usuario')}),
        ('Informações de Aluno', {'fields': ('matricula', 'serie'), 'classes': ('collapse',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined', 'data_cadastro', 'ultima_atualizacao'), 'classes': ('collapse',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'nome_completo', 'tipo_usuario'),
        }),
        ('Informações de Aluno', {
            'classes': ('collapse',),
            'fields': ('matricula', 'serie'),
        }),
    )
    
    readonly_fields = ['data_cadastro', 'ultima_atualizacao']

admin.site.register(CustomUser, CustomUserAdmin)