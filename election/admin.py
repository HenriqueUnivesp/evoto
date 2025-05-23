from django.contrib import admin
from .models import TipoEleicao, Eleicao, Chapa, MembroChapa, Voto

class MembroChapaInline(admin.TabularInline):
    model = MembroChapa
    extra = 0
    min_num = 0

@admin.register(TipoEleicao)
class TipoEleicaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Eleicao)
class EleicaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_eleicao', 'data_inicio', 'data_fim', 'status', 'criado_por')
    list_filter = ('status', 'tipo_eleicao')
    search_fields = ('titulo', 'descricao')
    date_hierarchy = 'data_inicio'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(Chapa)
class ChapaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'numero', 'eleicao', 'presidente_nome', 'data_cadastro')
    list_filter = ('eleicao',)
    search_fields = ('nome', 'presidente_nome', 'vice_nome')
    readonly_fields = ('data_cadastro', 'cadastrado_por')
    inlines = [MembroChapaInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.cadastrado_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(MembroChapa)
class MembroChapaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'chapa', 'serie')
    list_filter = ('chapa__eleicao', 'chapa')
    search_fields = ('nome', 'cargo', 'chapa__nome')

@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('eleicao', 'chapa', 'eleitor', 'data_voto')
    list_filter = ('eleicao', 'chapa')
    date_hierarchy = 'data_voto'
    readonly_fields = ('eleicao', 'chapa', 'eleitor', 'data_voto', 'ip_address')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False