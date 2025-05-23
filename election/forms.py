from django import forms
from .models import Eleicao, Chapa, MembroChapa, TipoEleicao, Voto
from django.utils import timezone
from datetime import timedelta 


class ChapaForm(forms.ModelForm):
    propostas = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Digite cada proposta em uma linha separada',
            'rows': 5
        }),
        label='Propostas da Chapa (mínimo 3)',
        help_text='Descreva as principais propostas da chapa, separando cada uma em uma linha.'
    )
    
    aceite_termos = forms.BooleanField(
        required=True,
        label='Declaramos que as informações fornecidas são verdadeiras e que estamos cientes e de acordo com as regras do processo eleitoral estabelecidas pela Comissão Eleitoral.',
    )
    
    comentarios = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Informações adicionais que julgar importante',
            'rows': 3
        }),
        label='Comentários Adicionais (opcional)',
        required=False
    )
    
    class Meta:
        model = Chapa
        fields = [
            'nome', 'numero', 'slogan', 'imagem', 'propostas',
            'presidente_nome', 'presidente_serie', 'presidente_matricula', 
            'presidente_email', 'presidente_telefone',
            'vice_nome', 'vice_serie', 'vice_matricula', 'vice_email',
            'documento_assinaturas'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Renovação Estudantil'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10', 'min': 10, 'max': 99}),
            'slogan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Por uma escola melhor para todos!'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'presidente_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'presidente_serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2º Ano B'}),
            'presidente_matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'presidente_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'presidente_telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'vice_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'vice_serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2º Ano A'}),
            'vice_matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'vice_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'documento_assinaturas': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome da Chapa',
            'numero': 'Número da Chapa (2 dígitos)',
            'slogan': 'Slogan da Chapa',
            'imagem': 'Imagem da Chapa (opcional)',
            'presidente_nome': 'Nome Completo',
            'presidente_serie': 'Série/Turma',
            'presidente_matricula': 'Número de Matrícula',
            'presidente_email': 'E-mail',
            'presidente_telefone': 'Telefone de Contato',
            'vice_nome': 'Nome do Vice-Presidente (opcional)',
            'vice_serie': 'Série/Turma (opcional)',
            'vice_matricula': 'Número de Matrícula (opcional)',
            'vice_email': 'E-mail (opcional)',
            'documento_assinaturas': 'Documento com Assinaturas de Apoio (PDF)',
        }
        help_texts = {
            'documento_assinaturas': 'Anexe o documento com as assinaturas dos estudantes apoiadores (mínimo 50 assinaturas)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornando os campos do vice-presidente opcionais
        self.fields['vice_nome'].required = False
        self.fields['vice_serie'].required = False
        self.fields['vice_matricula'].required = False
        self.fields['vice_email'].required = False
    
    def clean_propostas(self):
        propostas = self.cleaned_data.get('propostas')
        if propostas:
            # Conta quantas propostas foram enviadas (separadas por nova linha)
            linhas = [linha.strip() for linha in propostas.splitlines() if linha.strip()]
            if len(linhas) < 3:
                raise forms.ValidationError("É necessário informar pelo menos 3 propostas.")
        return propostas

class MembroChapaForm(forms.ModelForm):
    class Meta:
        model = MembroChapa
        fields = ['nome', 'serie', 'matricula', 'email', 'cargo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2º Ano C'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Secretário, Tesoureiro, etc'}),
        }

class VotacaoForm(forms.Form):
    chapa = forms.ModelChoiceField(
        queryset=Chapa.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
        label='Selecione uma chapa para votar'
    )
    
    def __init__(self, eleicao, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['chapa'].queryset = Chapa.objects.filter(eleicao=eleicao)

class ConfirmarVotoForm(forms.Form):
    confirmar_voto = forms.BooleanField(
        required=True,
        label="Confirmo meu voto final",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={
            'required': 'Você precisa confirmar seu voto marcando esta caixa'
        }
    )    

class EleicaoForm(forms.ModelForm):
    tipo_eleicao_nome = forms.CharField(
        max_length=100, 
        label='Tipo de Eleição',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o tipo de eleição'
        })
    )

    class Meta:
        model = Eleicao
        fields = ['titulo', 'descricao', 'data_inicio', 'data_fim']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: Eleição do Grêmio Estudantil 2024 - Representantes do Ensino Médio'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descreva as regras e detalhes da eleição'
            }),
            'data_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local',
            }),
            'data_fim': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local',
            }),
        }
        labels = {
            'titulo': 'Nome da Eleição',
            'descricao': 'Descrição da Eleição',
            'data_inicio': 'Data e Hora de Início',
            'data_fim': 'Data e Hora de Término',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define data de início como a data atual
        data_atual = timezone.now()
        
        # Define data de início no formato local
        self.initial['data_inicio'] = data_atual.strftime('%Y-%m-%dT%H:%M')
        
        # Define data de fim 10 minutos após
        data_fim = data_atual + timedelta(minutes=10)
        self.initial['data_fim'] = data_fim.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        # Verifica se as datas foram preenchidas
        if not data_inicio or not data_fim:
            raise forms.ValidationError("Preencha tanto a data de início quanto a data de término.")

        # Verifica se a data de término é posterior à data de início
        if data_fim <= data_inicio:
            raise forms.ValidationError("A data de término deve ser posterior à data de início.")

        return cleaned_data

    def save(self, commit=True):
        eleicao = super().save(commit=False)
        
        # Obtém o nome do tipo de eleição do formulário
        tipo_eleicao_nome = self.cleaned_data.get('tipo_eleicao_nome', self.cleaned_data['titulo'])
        
        # Cria ou obtém o tipo de eleição
        tipo_eleicao, created = TipoEleicao.objects.get_or_create(
            nome=tipo_eleicao_nome,
            defaults={'descricao': f'Tipo de eleição: {tipo_eleicao_nome}'}
        )
        
        # Atribui o tipo de eleição
        eleicao.tipo_eleicao = tipo_eleicao
        
        if commit:
            eleicao.save()
        
        return eleicao