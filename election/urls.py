from django.urls import path
from . import views

app_name = 'election'

urlpatterns = [
    # Página inicial de votação
    path('', views.home, name='acesso_votacao'),
    
    # Cadastro de chapa (para uma eleição específica ou sem eleição específica)
    path('cadastro-chapa/', views.cadastro_chapa, name='cadastro_chapa'),  # Cadastro sem 'eleicao_id'
    path('cadastro-chapa/<int:eleicao_id>/', views.cadastro_chapa, name='cadastro_chapa_eleicao'),  # Cadastro com 'eleicao_id'
    
    # Votação
    path('votacao/', views.votacao, name='votacao'),
    path('votacao/<int:eleicao_id>/', views.votacao, name='votacao_eleicao'),
    
    # Confirmação de voto
    path('confirmar-voto/<int:eleicao_id>/<int:chapa_id>/', views.confirmar_voto, name='confirmar_voto'),
    
    # Resultados da eleição
    path('resultados/<int:eleicao_id>/', views.resultados, name='resultados'),
    
    # URLs para administração de eleições
    path('criar-eleicao/', views.criar_eleicao, name='criar_eleicao'),
    path('gerenciar-chapas/<int:eleicao_id>/', views.gerenciar_chapas, name='gerenciar_chapas'),
    
    # URLs para editar e remover chapas
    path('editar-chapa/<int:chapa_id>/', views.editar_chapa, name='editar_chapa'),
    path('remover-chapa/<int:chapa_id>/', views.remover_chapa, name='remover_chapa'),
    
    # Gerenciamento de tipos de eleição
    path('gerenciar-tipos-eleicao/', views.gerenciar_tipos_eleicao, name='gerenciar_tipos_eleicao'),
    
    # Listagem de eleições
    path('listar-eleicoes/', views.listar_eleicoes, name='listar_eleicoes'),
    
    # Processamento de chapas via AJAX
    path('processar-chapas/<int:eleicao_id>/', views.processar_chapas, name='processar_chapas'),
    
    # Exclusão de eleição
    path('excluir-eleicao/<int:eleicao_id>/', views.excluir_eleicao, name='excluir_eleicao'),
]