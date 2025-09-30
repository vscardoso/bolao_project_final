from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Pool, Competition, Bet, Match

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

class BetWizardForm(forms.Form):
    """Formulário wizard para seleção de múltiplas partidas"""
    
    def __init__(self, *args, **kwargs):
        self.pool = kwargs.pop('pool', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.pool:
            # Buscar partidas disponíveis para apostas
            available_matches = Match.objects.filter(
                pool=self.pool,
                finished=False,
                start_time__gte=timezone.now()
            ).select_related('home_team', 'away_team').order_by('start_time')
            
            # Buscar apostas existentes do usuário
            existing_bets = {}
            if self.user:
                user_bets = Bet.objects.filter(
                    user=self.user,
                    match__in=available_matches
                )
                existing_bets = {bet.match_id: bet for bet in user_bets}
            
            # Criar campos dinamicamente para cada partida
            for match in available_matches:
                match_prefix = f'match_{match.id}'
                
                # Campo de seleção da partida
                self.fields[f'{match_prefix}_selected'] = forms.BooleanField(
                    required=False,
                    initial=match.id in existing_bets,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input match-selector',
                        'data-match-id': match.id,
                        'onchange': 'toggleMatchCard(this)'
                    })
                )
                
                # Campos de placar
                existing_bet = existing_bets.get(match.id)
                
                self.fields[f'{match_prefix}_home_score'] = forms.IntegerField(
                    min_value=0,
                    max_value=20,
                    required=False,
                    initial=existing_bet.home_score_bet if existing_bet else None,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-lg text-center score-input',
                        'placeholder': '0',
                        'data-match-id': match.id,
                        'data-team': 'home',
                        'oninput': 'validateScore(this); calculatePoints(this)',
                        'disabled': match.id not in existing_bets
                    })
                )
                
                self.fields[f'{match_prefix}_away_score'] = forms.IntegerField(
                    min_value=0,
                    max_value=20,
                    required=False,
                    initial=existing_bet.away_score_bet if existing_bet else None,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-lg text-center score-input',
                        'placeholder': '0',
                        'data-match-id': match.id,
                        'data-team': 'away',
                        'oninput': 'validateScore(this); calculatePoints(this)',
                        'disabled': match.id not in existing_bets
                    })
                )
    
    def get_selected_matches_data(self):
        """Retorna dados das partidas selecionadas"""
        selected_data = []
        
        for field_name, value in self.cleaned_data.items():
            if field_name.endswith('_selected') and value:
                match_id = field_name.replace('match_', '').replace('_selected', '')
                match_prefix = f'match_{match_id}'
                
                home_score = self.cleaned_data.get(f'{match_prefix}_home_score')
                away_score = self.cleaned_data.get(f'{match_prefix}_away_score')
                
                if home_score is not None and away_score is not None:
                    selected_data.append({
                        'match_id': int(match_id),
                        'home_score': home_score,
                        'away_score': away_score
                    })
        
        return selected_data
    
    def clean(self):
        cleaned_data = super().clean()
        selected_matches = self.get_selected_matches_data()
        
        if not selected_matches:
            raise ValidationError("Você deve selecionar pelo menos uma partida para apostar.")
        
        # Validar se todas as partidas selecionadas têm placares válidos
        for match_data in selected_matches:
            if match_data['home_score'] is None or match_data['away_score'] is None:
                raise ValidationError("Todas as partidas selecionadas devem ter placares preenchidos.")
        
        return cleaned_data

# Wizard Forms for Pool Creation
class PoolWizardStepOneForm(forms.Form):
    """Step 1: Basic Information"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Bolão Copa do Mundo 2026'
        }),
        label='Nome do Bolão'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Descreva as regras do seu bolão, premiações, etc.'
        }),
        label='Descrição',
        required=False
    )
    
    competition = forms.ModelChoiceField(
        queryset=Competition.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Competição',
        empty_label='Selecione uma competição'
    )
    
    pool_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Imagem do Bolão'
    )

class PoolWizardStepTwoForm(forms.Form):
    """Step 2: Settings and Rules"""
    entry_fee = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'step': 0.01
        }),
        label='Taxa de Participação (R$)'
    )
    
    max_participants = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'placeholder': 'Ilimitado se vazio'
        }),
        label='Máximo de Participantes'
    )
    
    betting_deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Data Limite para Apostas'
    )
    
    visibility = forms.ChoiceField(
        choices=[
            ('public', 'Público - Qualquer pessoa pode encontrar'),
            ('private', 'Privado - Somente por convite')
        ],
        widget=forms.RadioSelect(),
        label='Visibilidade'
    )
    
    exact_score_points = forms.IntegerField(
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Pontos por Placar Exato'
    )
    
    correct_difference_points = forms.IntegerField(
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Pontos por Diferença de Gols'
    )
    
    correct_winner_points = forms.IntegerField(
        initial=3,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Pontos por Vencedor'
    )

class PoolWizardStepThreeForm(forms.Form):
    """Step 3: Invitations"""
    invite_emails = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Digite os emails separados por vírgula\nex: joao@email.com, maria@email.com'
        }),
        label='Emails para Convite'
    )
    
    send_whatsapp_link = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Gerar link para WhatsApp'
    )
    
    custom_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Mensagem personalizada para os convites...'
        }),
        label='Mensagem Personalizada'
    )

class BetForm(forms.ModelForm):
    """Formulário individual para uma aposta específica"""
    
    class Meta:
        model = Bet
        fields = ['home_score_bet', 'away_score_bet']
        widgets = {
            'home_score_bet': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-center score-input',
                'min': 0,
                'max': 20,
                'step': 1,
                'placeholder': '0',
                'data-bs-toggle': 'tooltip',
                'data-bs-placement': 'top',
                'title': 'Digite o número de gols do time da casa',
                'autocomplete': 'off'
            }),
            'away_score_bet': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-center score-input',
                'min': 0,
                'max': 20,
                'step': 1,
                'placeholder': '0',
                'data-bs-toggle': 'tooltip',
                'data-bs-placement': 'top',
                'title': 'Digite o número de gols do time visitante',
                'autocomplete': 'off'
            }),
        }
        labels = {
            'home_score_bet': 'Placar Casa',
            'away_score_bet': 'Placar Visitante',
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair match e pool do kwargs
        self.match = kwargs.pop('match', None)
        self.pool = kwargs.pop('pool', None)
        self.user = kwargs.pop('user', None)
        super(BetForm, self).__init__(*args, **kwargs)
        
        # Personalizar os labels com os nomes dos times se disponível
        if self.match:
            self.fields['home_score_bet'].label = f"⚽ {self.match.home_team.name}"
            self.fields['away_score_bet'].label = f"⚽ {self.match.away_team.name}"
            
            # Adicionar informações dos times nos tooltips
            self.fields['home_score_bet'].widget.attrs['title'] = f'Gols do {self.match.home_team.name}'
            self.fields['away_score_bet'].widget.attrs['title'] = f'Gols do {self.match.away_team.name}'
            
            # Adicionar classes CSS específicas para styling
            self.fields['home_score_bet'].widget.attrs['data-team'] = 'home'
            self.fields['away_score_bet'].widget.attrs['data-team'] = 'away'
        
        # Adicionar validação visual em tempo real
        for field_name in ['home_score_bet', 'away_score_bet']:
            self.fields[field_name].widget.attrs.update({
                'oninput': 'validateScore(this)',
                'onblur': 'finalizeScore(this)',
                'onfocus': 'highlightField(this)'
            })
    
    def clean(self):
        cleaned_data = super().clean()
        home_score = cleaned_data.get('home_score_bet')
        away_score = cleaned_data.get('away_score_bet')
        
        # Validar se ambos os campos foram preenchidos
        if home_score is None or away_score is None:
            raise forms.ValidationError("Você deve preencher o placar para ambos os times.")
        
        # Validar valores negativos
        if home_score < 0 or away_score < 0:
            raise forms.ValidationError("O placar não pode ser negativo.")
        
        # Validar se a partida já começou
        from django.utils import timezone
        if self.match and self.match.start_time <= timezone.now():
            raise forms.ValidationError("⚠️ Não é possível apostar após o início da partida.")
        
        # Validar se o bolão está aberto para apostas
        if self.pool and hasattr(self.pool, 'is_open_for_betting') and not self.pool.is_open_for_betting():
            raise forms.ValidationError("⚠️ Este bolão não está mais aberto para apostas.")
        
        # Validar valores razoáveis (mais restritivo)
        if home_score > 15 or away_score > 15:
            raise forms.ValidationError("🚫 Placar muito alto! Máximo 15 gols por time.")
        
        # Validar se é um placar muito improvável
        total_goals = home_score + away_score
        if total_goals > 20:
            raise forms.ValidationError("🤔 Total de gols muito alto! Revise sua aposta.")
        
        # Aviso para placares altos mas válidos
        if total_goals > 10:
            # Esta seria uma validação soft - apenas aviso, não erro
            pass  # Poderia adicionar uma mensagem de warning no futuro
            
        return cleaned_data
    
    def clean_home_score_bet(self):
        home_score = self.cleaned_data.get('home_score_bet')
        
        if home_score is None:
            raise forms.ValidationError("Este campo é obrigatório.")
            
        if home_score < 0:
            raise forms.ValidationError("O placar não pode ser negativo.")
            
        if home_score > 20:
            raise forms.ValidationError("Placar máximo é 20 gols.")
            
        return home_score
    
    def clean_away_score_bet(self):
        away_score = self.cleaned_data.get('away_score_bet')
        
        if away_score is None:
            raise forms.ValidationError("Este campo é obrigatório.")
            
        if away_score < 0:
            raise forms.ValidationError("O placar não pode ser negativo.")
            
        if away_score > 20:
            raise forms.ValidationError("Placar máximo é 20 gols.")
            
        return away_score
    
    def save(self, commit=True):
        """Salva a aposta com informações adicionais"""
        bet = super().save(commit=False)
        
        # Adicionar informações contextuais se disponível
        if self.match:
            bet.match = self.match
        if self.user:
            bet.user = self.user
            
        # Adicionar timestamp de criação da aposta
        from django.utils import timezone
        if not bet.pk:  # Nova aposta
            bet.created_at = timezone.now()
            
        if commit:
            bet.save()
        return bet