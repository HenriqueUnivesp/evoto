from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.forms import formset_factory
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import timedelta
from .models import Eleicao, TipoEleicao, Chapa, MembroChapa, Voto
from .forms import ChapaForm, MembroChapaForm, VotacaoForm, ConfirmarVotoForm, EleicaoForm


def home(request):
    """Página inicial do sistema de eleição"""
    # Lista eleições ativas e próximas
    agora = timezone.now()
    eleicoes_ativas = Eleicao.objects.filter(data_inicio__lte=agora, data_fim__gte=agora).order_by('data_fim')
    eleicoes_proximas = Eleicao.objects.filter(data_inicio__gt=agora).order_by('data_inicio')
    
    # Logs para debug das eleições ativas
    print(f"Momento atual: {agora}")
    print(f"Total de eleições ativas: {eleicoes_ativas.count()}")
    for eleicao in eleicoes_ativas:
        print(f"Eleição: {eleicao.titulo}, Início: {eleicao.data_inicio}, Fim: {eleicao.data_fim}, Status: {eleicao.status}")
        # Verifica se tem chapas
        chapas_count = Chapa.objects.filter(eleicao=eleicao).count()
        print(f"  - Chapas cadastradas: {chapas_count}")
    
    # Log para debug do usuário
    if request.user.is_authenticated:
        print(f"Usuário: {request.user.username}")
        print(f"Tipo de usuário: {getattr(request.user, 'tipo_usuario', 'Não definido')}")
    
    context = {
        'eleicoes_ativas': eleicoes_ativas,
        'eleicoes_proximas': eleicoes_proximas,
        'agora': agora,  # Adicionado para debug no template
    }
    
    return render(request, 'election/acesso_votacao.html', context)

@login_required
def cadastro_chapa(request, eleicao_id=None):
    """View para cadastro de chapas"""
    # Se eleicao_id não for fornecido, pega a primeira eleição agendada
    if eleicao_id:
        eleicao = get_object_or_404(Eleicao, id=eleicao_id)
    else:
        agora = timezone.now()
        eleicao = Eleicao.objects.filter(data_inicio__gt=agora).order_by('data_inicio').first()
        if not eleicao:
            messages.warning(request, "Não há eleições disponíveis para cadastro de chapas no momento.")
            return redirect('election:acesso_votacao')
    
    # Verificando se a eleição está aberta para cadastro de chapas
    if eleicao.status != 'agendada':
        messages.warning(request, "Esta eleição não está aberta para cadastro de chapas.")
        return redirect('election:acesso_votacao')
    
    if request.method == 'POST':
        form = ChapaForm(request.POST, request.FILES)
        if form.is_valid():
            chapa = form.save(commit=False)
            chapa.eleicao = eleicao
            chapa.cadastrado_por = request.user
            chapa.save()
            
            messages.success(request, "Chapa cadastrada com sucesso! Ela será analisada pela Comissão Eleitoral.")
            return redirect('election:acesso_votacao')
    else:
        form = ChapaForm()
    
    context = {
        'form': form,
        'eleicao': eleicao,
    }
    
    return render(request, 'election/cadastro_chapa.html', context)

@login_required
def votacao(request, eleicao_id=None):
    """View para votação"""
    # Se eleicao_id não for fornecido, pega a primeira eleição ativa
    if eleicao_id:
        eleicao = get_object_or_404(Eleicao, id=eleicao_id)
    else:
        agora = timezone.now()
        eleicao = Eleicao.objects.filter(data_inicio__lte=agora, data_fim__gte=agora).order_by('data_fim').first()
        if not eleicao:
            messages.warning(request, "Não há eleições em andamento no momento.")
            return redirect('election:acesso_votacao')
    
    # Verifica se a eleição está em andamento
    eleicao.atualizar_status()
    if eleicao.status != 'em_andamento':
        messages.warning(request, "Esta eleição não está em andamento.")
        return redirect('election:acesso_votacao')
    
    # Verifica se o usuário é aluno
    if not hasattr(request.user, 'tipo_usuario') or request.user.tipo_usuario != 'aluno':
        messages.warning(request, "Apenas alunos podem participar da votação.")
        return redirect('election:acesso_votacao')
    
    # Verifica se o usuário já votou
    if Voto.objects.filter(eleicao=eleicao, eleitor=request.user).exists():
        # Mensagem clara de que o aluno já votou
        messages.info(request, "Você já registrou seu voto nesta eleição. Não é possível votar mais de uma vez.")
        return redirect('election:acesso_votacao')
    
    # Se for um POST, processa o voto
    chapa_escolhida = None
    if request.method == 'POST':
        form = VotacaoForm(eleicao, request.POST)
        if form.is_valid():
            chapa_escolhida = form.cleaned_data['chapa']
            confirmar_form = ConfirmarVotoForm()
            return render(request, 'election/confirmar_voto.html', {
                'eleicao': eleicao,
                'chapa': chapa_escolhida,
                'form': confirmar_form,
            })
    else:
        form = VotacaoForm(eleicao)
    
    # Obtém as chapas para esta eleição
    chapas = Chapa.objects.filter(eleicao=eleicao)
    
    # Calcula o tempo restante
    tempo_restante = None
    horas = 0
    minutos = 0
    segundos = 0
    
    if hasattr(eleicao, 'tempo_restante'):
        tempo_restante = eleicao.tempo_restante()
        if tempo_restante:
            # Calcular horas, minutos e segundos manualmente
            segundos_totais = tempo_restante.seconds
            horas = segundos_totais // 3600
            minutos = (segundos_totais % 3600) // 60
            segundos = segundos_totais % 60
    
    context = {
        'eleicao': eleicao,
        'chapas': chapas,
        'form': form,
        'tempo_restante': tempo_restante,
        'horas': horas,
        'minutos': minutos,
        'segundos': segundos,
    }
    
    return render(request, 'election/votacao.html', context)

@login_required
def confirmar_voto(request, eleicao_id, chapa_id):
    """View para confirmar o voto"""
    eleicao = get_object_or_404(Eleicao, id=eleicao_id)
    chapa = get_object_or_404(Chapa, id=chapa_id, eleicao=eleicao)
    
    # Verifica se a eleição está em andamento
    eleicao.atualizar_status()
    if eleicao.status != 'em_andamento':
        messages.warning(request, "Esta eleição não está em andamento.")
        return redirect('election:acesso_votacao')
    
    # Verifica se o usuário é aluno
    if not hasattr(request.user, 'tipo_usuario') or request.user.tipo_usuario != 'aluno':
        messages.warning(request, "Apenas alunos podem participar da votação.")
        return redirect('election:acesso_votacao')
    
    # Verifica se o usuário já votou
    if Voto.objects.filter(eleicao=eleicao, eleitor=request.user).exists():
        messages.warning(request, "Você já votou nesta eleição.")
        return redirect('election:acesso_votacao')
    
    if request.method == 'POST':
        form = ConfirmarVotoForm(request.POST)
        if form.is_valid():
            # Registra o voto
            voto = Voto(
                eleicao=eleicao,
                chapa=chapa,
                eleitor=request.user,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            voto.save()
            
            messages.success(request, "Seu voto foi registrado com sucesso! Obrigado por participar.")
            return redirect('election:acesso_votacao')
    else:
        form = ConfirmarVotoForm()
    
    context = {
        'eleicao': eleicao,
        'chapa': chapa,
        'form': form,
    }
    
    return render(request, 'election/confirmar_voto.html', context)

@login_required
def resultados(request, eleicao_id):
    """View para mostrar resultados de uma eleição"""
    eleicao = get_object_or_404(Eleicao, id=eleicao_id)
    
    # Verifica se a eleição foi finalizada
    eleicao.atualizar_status()
    
    # Obtém os resultados
    chapas = Chapa.objects.filter(eleicao=eleicao).annotate(
        total_votos=Count('votos')
    ).order_by('-total_votos')
    
    # Calcula o total de votos
    total_votos = Voto.objects.filter(eleicao=eleicao).count()
    
    context = {
        'eleicao': eleicao,
        'chapas': chapas,
        'total_votos': total_votos,
    }
    
    return render(request, 'election/resultados.html', context)

def is_diretor_ou_professor(user):
    """Verifica se o usuário é diretor ou professor"""
    print(f"Verificando permissões para: {user.username}")
    
    # Verifica se é professor
    is_professor = hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'professor'
    print(f"  - É professor: {is_professor}")
    
    # Verifica se é diretor
    is_diretor = False
    if hasattr(user, 'is_diretor'):
        if callable(user.is_diretor):
            try:
                is_diretor = user.is_diretor()
            except Exception as e:
                print(f"Erro ao verificar is_diretor: {e}")
        elif isinstance(user.is_diretor, bool):
            is_diretor = user.is_diretor
    print(f"  - É diretor: {is_diretor}")
    
    # Verifica se é staff
    is_staff = user.is_staff
    print(f"  - É staff: {is_staff}")
    
    return is_professor or is_diretor or is_staff

@login_required
@user_passes_test(is_diretor_ou_professor)
def criar_eleicao(request):
    """View para criar uma nova eleição."""
    if request.method == 'POST':
        form = EleicaoForm(request.POST)
        if form.is_valid():
            eleicao = form.save(commit=False)
            
            # Atualizar o status da eleição com base na data de início
            agora = timezone.now()
            if eleicao.data_inicio <= agora:
                # Se a data de início for agora ou no passado, a eleição já está em andamento
                eleicao.status = 'em_andamento'
            else:
                # Caso contrário, está agendada para o futuro
                eleicao.status = 'agendada'
                
            # Definir o usuário que criou a eleição
            eleicao.criado_por = request.user
            
            # Salvar a eleição com as datas definidas no formulário
            eleicao.save()

            messages.success(request, f"Eleição '{eleicao.titulo}' criada com sucesso!")
            return redirect('election:gerenciar_chapas', eleicao_id=eleicao.id)
    else:
        form = EleicaoForm()

    context = {
        'form': form,
        'tipos_eleicao': TipoEleicao.objects.all(),
    }

    return render(request, 'election/form_eleicao.html', context)

@login_required
def editar_chapa(request, chapa_id):
    """View para editar uma chapa existente"""
    chapa = get_object_or_404(Chapa, id=chapa_id)
    eleicao = chapa.eleicao

    # Verificação de permissão corrigida
    is_professor = hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'professor'
    is_diretor = False
    
    # Verificações mais robustas para is_diretor
    if hasattr(request.user, 'is_diretor'):
        if callable(request.user.is_diretor):
            try:
                is_diretor = request.user.is_diretor()
            except Exception as e:
                print(f"Erro ao chamar is_diretor(): {e}")
        elif isinstance(request.user.is_diretor, bool):
            is_diretor = request.user.is_diretor
    
    # Debug logs
    print(f"DEBUG - User: {request.user.username}")
    print(f"DEBUG - tipo_usuario: {getattr(request.user, 'tipo_usuario', 'N/A')}")
    print(f"DEBUG - is_professor: {is_professor}")
    print(f"DEBUG - is_diretor: {is_diretor}")
    print(f"DEBUG - is_staff: {request.user.is_staff}")
    print(f"DEBUG - É o cadastrador: {chapa.cadastrado_por == request.user}")

    # Condição simplificada para verificar permissão
    if not (request.user.is_staff or is_diretor or is_professor or chapa.cadastrado_por == request.user):
        return HttpResponseForbidden("Você não tem permissão para editar esta chapa.")

    if request.method == 'POST':
        form = ChapaForm(request.POST, request.FILES, instance=chapa)
        if form.is_valid():
            form.save()
            messages.success(request, f"Chapa '{chapa.nome}' atualizada com sucesso!")
            return redirect('election:gerenciar_chapas', eleicao_id=eleicao.id)
    else:
        form = ChapaForm(instance=chapa)

    context = {
        'form': form,
        'chapa': chapa,
        'eleicao': eleicao,
        'modo_edicao': True,
    }

    return render(request, 'election/editar_chapa.html', context)

@login_required
def remover_chapa(request, chapa_id):
    """View para remover uma chapa"""
    chapa = get_object_or_404(Chapa, id=chapa_id)
    eleicao = chapa.eleicao
    
    # Verificação de permissão corrigida
    is_professor = hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'professor'
    is_diretor = False
    
    # Verificações mais robustas para is_diretor
    if hasattr(request.user, 'is_diretor'):
        if callable(request.user.is_diretor):
            try:
                is_diretor = request.user.is_diretor()
            except Exception as e:
                print(f"Erro ao chamar is_diretor(): {e}")
        elif isinstance(request.user.is_diretor, bool):
            is_diretor = request.user.is_diretor
    
    # Condição simplificada para verificar permissão
    if not (request.user.is_staff or is_diretor or is_professor or chapa.cadastrado_por == request.user):
        return HttpResponseForbidden("Você não tem permissão para remover esta chapa.")
    
    if request.method == 'POST':
        nome_chapa = chapa.nome
        chapa.delete()
        messages.success(request, f"Chapa '{nome_chapa}' removida com sucesso!")
        return redirect('election:gerenciar_chapas', eleicao_id=eleicao.id)
    
    context = {
        'chapa': chapa,
        'eleicao': eleicao,
    }
    
    return render(request, 'election/confirmar_exclusao_chapa.html', context)

@login_required
@user_passes_test(is_diretor_ou_professor)
def listar_eleicoes(request):
    """View para listar todas as eleições"""
    eleicoes = Eleicao.objects.all().order_by('-data_inicio')
    
    context = {
        'eleicoes': eleicoes,
    }
    
    return render(request, 'election/listar_eleicoes.html', context)

# Nova view para processar chapas via AJAX
@csrf_exempt
@login_required
@user_passes_test(is_diretor_ou_professor)
def processar_chapas(request, eleicao_id):
    """View para processar chapas via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            eleicao = get_object_or_404(Eleicao, id=eleicao_id)
            
            # Processar as chapas
            for chapa_data in data['chapas']:
                # Criar ou atualizar a chapa
                chapa, created = Chapa.objects.update_or_create(
                    id=chapa_data.get('id'),
                    defaults={
                        'eleicao': eleicao,
                        'nome': chapa_data['nome'],
                        'numero': chapa_data['numero'],
                        'slogan': chapa_data['slogan'],
                        'propostas': '\n'.join(chapa_data['propostas']),
                        'presidente_nome': chapa_data['presidente']['nome'],
                        'presidente_serie': chapa_data['presidente']['serie'],
                        'presidente_matricula': chapa_data['presidente']['matricula'],
                        'presidente_email': chapa_data['presidente']['email'],
                        'presidente_telefone': chapa_data['presidente']['telefone'],
                        'cadastrado_por': request.user
                    }
                )
                
                # Se a chapa tem um ID mas não foi encontrada, pular
                if not created and not chapa:
                    continue
            
            return JsonResponse({'status': 'success', 'message': 'Chapas processadas com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

@login_required
@user_passes_test(is_diretor_ou_professor)
def gerenciar_tipos_eleicao(request):
    """View para gerenciar tipos de eleição"""
    tipos_eleicao = TipoEleicao.objects.all()
    
    if request.method == 'POST':
        # Aqui você deve definir o formulário correto para TipoEleicao
        form = None  # Substitua por TipoEleicaoForm quando estiver disponível
        if form and form.is_valid():
            form.save()
            messages.success(request, 'Tipo de eleição criado com sucesso.')
            return redirect('election:gerenciar_tipos_eleicao')
    else:
        form = None  # Substitua por TipoEleicaoForm quando estiver disponível
    
    context = {
        'tipos_eleicao': tipos_eleicao,
        'form': form
    }
    
    return render(request, 'election/form_eleicao.html', context)

@login_required
@user_passes_test(is_diretor_ou_professor)
def excluir_eleicao(request, eleicao_id):
    """View para excluir uma eleição"""
    eleicao = get_object_or_404(Eleicao, id=eleicao_id)
    
    # Verificação de permissão corrigida
    is_professor = hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'professor'
    is_diretor = False
    
    # Verificações mais robustas para is_diretor
    if hasattr(request.user, 'is_diretor'):
        if callable(request.user.is_diretor):
            try:
                is_diretor = request.user.is_diretor()
            except Exception as e:
                print(f"Erro ao chamar is_diretor(): {e}")
        elif isinstance(request.user.is_diretor, bool):
            is_diretor = request.user.is_diretor
    
    # Condição simplificada para verificar permissão
    if not (request.user.is_staff or is_diretor or is_professor or (hasattr(eleicao, 'criado_por') and eleicao.criado_por == request.user)):
        return HttpResponseForbidden("Você não tem permissão para excluir esta eleição.")
    
    if request.method == 'POST':
        titulo_eleicao = eleicao.titulo
        
        # Excluir chapas relacionadas
        Chapa.objects.filter(eleicao=eleicao).delete()
        
        # Excluir votos relacionados
        Voto.objects.filter(eleicao=eleicao).delete()
        
        # Excluir a eleição
        eleicao.delete()
        
        messages.success(request, f"Eleição '{titulo_eleicao}' excluída com sucesso!")
        return redirect('election:listar_eleicoes')
    
    context = {
        'eleicao': eleicao,
        'confirmar_exclusao': True
    }
    
    return render(request, 'election/form_eleicao.html', context)

@login_required
@user_passes_test(is_diretor_ou_professor)
def gerenciar_chapas(request, eleicao_id):
    """View para gerenciar chapas de uma eleição específica"""
    eleicao = get_object_or_404(Eleicao, id=eleicao_id)
    chapas = Chapa.objects.filter(eleicao=eleicao)
    
    if request.method == 'POST':
        form = ChapaForm(request.POST, request.FILES)
        if form.is_valid():
            chapa = form.save(commit=False)
            chapa.eleicao = eleicao
            chapa.cadastrado_por = request.user
            chapa.save()
            
            messages.success(request, f"Chapa '{chapa.nome}' cadastrada com sucesso!")
            return redirect('election:gerenciar_chapas', eleicao_id=eleicao.id)
    else:
        form = ChapaForm()
    
    context = {
        'eleicao': eleicao,
        'chapas': chapas,
        'form': form,
        'gerenciar_chapas': True
    }
    
    return render(request, 'election/form_eleicao.html', context)

@login_required
def votacao_eleicao(request, eleicao_id):
    """View para a página de votação de uma eleição específica"""
    # Redirecionamos para a view de votação completa que já tem todas as verificações
    return redirect('election:votacao', eleicao_id=eleicao_id)

def atualizar_status(self):
    """Atualiza o status da eleição com base nas datas"""
    agora = timezone.now()
    
    # Não alteramos o status 'em_andamento' até que a data de término seja atingida
    if self.status == 'em_andamento' and self.data_fim >= agora:
        return self.status
    
    # Verifica se a eleição já terminou
    if self.data_fim < agora:
        self.status = 'finalizada'
        self.save()
    
    return self.status

