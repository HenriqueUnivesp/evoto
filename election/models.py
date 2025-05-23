from django.db import models
from django.utils import timezone
from accounts.models import CustomUser

class TipoEleicao(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome do tipo de eleição')
    descricao = models.TextField(verbose_name='Descrição', blank=True)
    
    class Meta:
        verbose_name = 'Tipo de Eleição'
        verbose_name_plural = 'Tipos de Eleição'
    
    def __str__(self):
        return self.nome

class Eleicao(models.Model):
    STATUS_CHOICES = (
        ('agendada', 'Agendada'),
        ('em_andamento', 'Em andamento'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    )
    
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(verbose_name='Descrição')
    tipo_eleicao = models.ForeignKey(TipoEleicao, on_delete=models.CASCADE, verbose_name='Tipo de Eleição')
    data_inicio = models.DateTimeField(verbose_name='Data de início')
    data_fim = models.DateTimeField(verbose_name='Data de término')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='agendada', verbose_name='Status')
    criado_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='eleicoes_criadas', verbose_name='Criado por')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última atualização')
    
    class Meta:
        verbose_name = 'Eleição'
        verbose_name_plural = 'Eleições'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return self.titulo
    
    def esta_em_andamento(self):
        agora = timezone.now()
        return self.data_inicio <= agora <= self.data_fim
    
    def pode_votar(self, user):
        # Verifica se o usuário pode votar nesta eleição
        if not user.is_authenticated or user.tipo_usuario != 'aluno':
            return False
        
        # Verifica se o usuário já votou
        return not Voto.objects.filter(eleicao=self, eleitor=user).exists()
    
    def atualizar_status(self):
        """Atualiza o status da eleição com base nas datas"""
        agora = timezone.now()
        
        if self.status == 'cancelada':
            return
        
        if agora < self.data_inicio:
            self.status = 'agendada'
        elif agora <= self.data_fim:
            self.status = 'em_andamento'
        else:
            self.status = 'finalizada'
        
        self.save(update_fields=['status'])
    
    def tempo_restante(self):
        """Retorna o tempo restante para o término da eleição"""
        if self.status != 'em_andamento':
            return None
        
        agora = timezone.now()
        if agora > self.data_fim:
            return None
        
        diff = self.data_fim - agora
        return diff

class Chapa(models.Model):
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='chapas', verbose_name='Eleição')
    nome = models.CharField(max_length=100, verbose_name='Nome da chapa')
    numero = models.PositiveSmallIntegerField(verbose_name='Número da chapa')
    slogan = models.CharField(max_length=200, verbose_name='Slogan')
    imagem = models.ImageField(upload_to='chapas/', verbose_name='Imagem', blank=True, null=True)
    propostas = models.TextField(verbose_name='Propostas')
    
    # Dados do presidente e vice
    presidente_nome = models.CharField(max_length=200, verbose_name='Nome do Presidente')
    presidente_serie = models.CharField(max_length=50, verbose_name='Série/Turma do Presidente')
    presidente_matricula = models.CharField(max_length=50, verbose_name='Matrícula do Presidente')
    presidente_email = models.EmailField(verbose_name='Email do Presidente')
    presidente_telefone = models.CharField(max_length=20, verbose_name='Telefone do Presidente')
    
    # Campos do vice-presidente tornados opcionais
    vice_nome = models.CharField(max_length=200, verbose_name='Nome do Vice-Presidente', blank=True, null=True)
    vice_serie = models.CharField(max_length=50, verbose_name='Série/Turma do Vice-Presidente', blank=True, null=True)
    vice_matricula = models.CharField(max_length=50, verbose_name='Matrícula do Vice-Presidente', blank=True, null=True)
    vice_email = models.EmailField(verbose_name='Email do Vice-Presidente', blank=True, null=True)
    
    documento_assinaturas = models.FileField(upload_to='documentos/', verbose_name='Documento de Assinaturas', blank=True, null=True)
    
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')
    cadastrado_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='chapas_cadastradas', verbose_name='Cadastrado por')
    
    class Meta:
        verbose_name = 'Chapa'
        verbose_name_plural = 'Chapas'
        unique_together = [('eleicao', 'numero')]
    
    def __str__(self):
        return f"{self.nome} - {self.eleicao.titulo}"
    
    def get_total_votos(self):
        return self.votos.count()

class MembroChapa(models.Model):
    chapa = models.ForeignKey(Chapa, on_delete=models.CASCADE, related_name='membros', verbose_name='Chapa')
    nome = models.CharField(max_length=200, verbose_name='Nome')
    serie = models.CharField(max_length=50, verbose_name='Série/Turma')
    matricula = models.CharField(max_length=50, verbose_name='Matrícula')
    email = models.EmailField(verbose_name='Email')
    cargo = models.CharField(max_length=100, verbose_name='Cargo na chapa')
    
    class Meta:
        verbose_name = 'Membro da Chapa'
        verbose_name_plural = 'Membros da Chapa'
    
    def __str__(self):
        return f"{self.nome} - {self.cargo} ({self.chapa.nome})"

class Voto(models.Model):
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='votos', verbose_name='Eleição')
    chapa = models.ForeignKey(Chapa, on_delete=models.CASCADE, related_name='votos', verbose_name='Chapa')
    eleitor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='votos', verbose_name='Eleitor')
    data_voto = models.DateTimeField(auto_now_add=True, verbose_name='Data do voto')
    ip_address = models.GenericIPAddressField(verbose_name='Endereço IP', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Voto'
        verbose_name_plural = 'Votos'
        # Garante que cada eleitor só vote uma vez por eleição
        unique_together = [('eleicao', 'eleitor')]
    
    def __str__(self):
        return f"Voto de {self.eleitor} em {self.chapa.nome} - {self.eleicao.titulo}"