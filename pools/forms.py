from django import forms
from django.utils import timezone
from .models import Pool, Participation, Sport, Competition, Bet, Match, Invitation

class PoolForm(forms.ModelForm):
    """Formulário para criação e edição de bolões"""
    
    class Meta:
        model = Pool
        fields = [
            'name', 'description', 'competition', 'entry_fee', 
            'visibility', 'max_participants', 'betting_deadline'
        ]
        labels = {
            'name': 'Nome do Bolão',
            'description': 'Descrição',
            'competition': 'Competição',
            'entry_fee': 'Valor da Aposta',
            'visibility': 'Visibilidade',
            'max_participants': 'Número máximo de participantes',
            'betting_deadline': 'Data limite para apostas',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bolão Copa do Mundo 2026'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Descreva as regras e informações do seu bolão...'
            }),
            'competition': forms.Select(attrs={'class': 'form-select'}),
            'entry_fee': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'step': 0.01
            }),
            'visibility': forms.RadioSelect(),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0
            }),
            'betting_deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # O usuário atual será o proprietário
        super().__init__(*args, **kwargs)
        
        # Adicionar "Selecione" como empty_label para campos de seleção
        if 'competition' in self.fields:
            self.fields['competition'].empty_label = "Selecione"
        
        # Filtra apenas competições ativas
        competitions = Competition.objects.filter(is_active=True)
        
        # Verifica se existem competições disponíveis
        if not competitions.exists():
            self.fields['competition'].widget = forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True,
                'placeholder': 'Não há competições disponíveis no momento'
            })
            self.fields['competition'].help_text = "Não existem competições ativas. Entre em contato com um administrador."
        else:
            self.fields['competition'].queryset = competitions
        
        # Para outros campos de seleção que possam existir no futuro
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField) and field_name != 'competition':
                field.empty_label = "Selecione"
        
        # Adicionar classes e traduzir placeholders se necessário
        if 'betting_deadline' in self.fields:
            self.fields['betting_deadline'].input_formats = ['%Y-%m-%dT%H:%M']
        
        # Atualizar os choices para visibility (traduzir)
        if 'visibility' in self.fields:
            self.fields['visibility'].choices = [
                ('public', 'Público - Qualquer pessoa pode encontrar e participar'),
                ('private', 'Privado - Somente por convite')
            ]
    
    def clean_betting_deadline(self):
        deadline = self.cleaned_data.get('betting_deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("A data limite para apostas não pode ser no passado")
        return deadline

class PoolJoinForm(forms.Form):
    """Formulário para usuários ingressarem em um bolão"""
    payment_method = forms.ChoiceField(
        choices=[
            ('pix', 'PIX'),
            ('credit_card', 'Cartão de Crédito'),
            ('bank_transfer', 'Transferência Bancária'),
            ('other', 'Outro')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
    )
    
    def __init__(self, *args, **kwargs):
        self.pool = kwargs.pop('pool', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Se o bolão for gratuito, não precisamos do método de pagamento
        if self.pool and self.pool.entry_fee <= 0:
            self.fields['payment_method'].required = False
            self.fields['payment_method'].widget = forms.HiddenInput()

class InvitationForm(forms.ModelForm):
    """Formulário para enviar convites para o bolão"""
    recipient_email = forms.EmailField(
        label='Email do convidado',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'})
    )
    message = forms.CharField(
        label='Mensagem (opcional)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3,
            'placeholder': 'Venha participar do meu bolão!'
        })
    )
    
    class Meta:
        model = Invitation
        fields = ['recipient_email', 'message']

class InvitationForm(forms.Form):
    """Formulário para convidar usuários para um bolão"""
    emails = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Digite um email por linha'
        }),
        help_text='Digite um email por linha'
    )
    
    custom_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Mensagem personalizada (opcional)'
        }),
        required=False
    )
    
    def clean_emails(self):
        emails_text = self.cleaned_data.get('emails', '')
        emails = [e.strip() for e in emails_text.split('\n') if e.strip()]
        
        # Validação básica de email
        invalid_emails = []
        for email in emails:
            if '@' not in email or '.' not in email:
                invalid_emails.append(email)
        
        if invalid_emails:
            raise forms.ValidationError(
                f"Os seguintes emails são inválidos: {', '.join(invalid_emails)}"
            )
        
        return emails

class BetForm(forms.ModelForm):
    """Formulário para apostas"""
    
    class Meta:
        model = Bet
        fields = ['home_score_bet', 'away_score_bet']
        widgets = {
            'home_score_bet': forms.NumberInput(attrs={
                'class': 'form-control score-input',
                'min': '0',  # String em vez de número
                'placeholder': '0'
            }),
            'away_score_bet': forms.NumberInput(attrs={
                'class': 'form-control score-input',
                'min': '0',  # String em vez de número
                'placeholder': '0'
            })
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair match e pool do kwargs
        self.match = kwargs.pop('match', None)
        self.pool = kwargs.pop('pool', None)
        super(BetForm, self).__init__(*args, **kwargs)
        
        # Personalizar os labels se o match estiver disponível
        if self.match:
            self.fields['home_score_bet'].label = f"{self.match.home_team}"
            self.fields['away_score_bet'].label = f"{self.match.away_team}"
        
        # Garantir que os atributos 'min' são strings
        self.fields['home_score_bet'].widget.attrs['min'] = '0'
        self.fields['away_score_bet'].widget.attrs['min'] = '0'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar se a partida já começou
        from django.utils import timezone
        if self.match and self.match.start_time <= timezone.now():
            raise forms.ValidationError("Não é possível apostar após o início da partida.")
        
        # Validar se o bolão está aberto para apostas
        if self.pool and not self.pool.is_open_for_betting():
            raise forms.ValidationError("Este bolão não está mais aberto para apostas.")
            
        return cleaned_data
    
    def clean_home_score_bet(self):
        home_score = self.cleaned_data.get('home_score_bet')
        if home_score is not None and home_score > 20:
            raise forms.ValidationError("O placar não pode ser maior que 20 gols.")
        return home_score
    
    def clean_away_score_bet(self):
        away_score = self.cleaned_data.get('away_score_bet')
        if away_score is not None and away_score > 20:
            raise forms.ValidationError("O placar não pode ser maior que 20 gols.")
        return away_score