from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")
    phone = forms.CharField(max_length=15, required=False, label="Telefone")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')
        labels = {
            'username': 'Nome de usuário',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionando classes Bootstrap para estilização
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
        
        # Traduzindo labels e mensagens de ajuda
        self.fields['username'].help_text = 'Obrigatório. 150 caracteres ou menos. Letras, números e @/./+/-/_ apenas.'
        self.fields['email'].help_text = 'Informe um e-mail válido.'
        self.fields['phone'].help_text = 'Formato: (00) 00000-0000'
        self.fields['password1'].label = 'Senha'
        self.fields['password1'].help_text = '<ul><li>Sua senha não pode ser muito semelhante às suas outras informações pessoais.</li><li>Sua senha deve conter pelo menos 8 caracteres.</li><li>Sua senha não pode ser uma senha comumente utilizada.</li><li>Sua senha não pode ser inteiramente numérica.</li></ul>'
        self.fields['password2'].label = 'Confirmar senha'
        self.fields['password2'].help_text = 'Digite a mesma senha novamente para verificação.'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        return password2

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'profile_picture')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'profile_picture', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
        self.fields['profile_picture'].widget.attrs['class'] = 'form-control-file'

class ProfileEditForm(forms.ModelForm):
    """
    Formulário para edição do perfil de usuário, combinando campos
    do modelo User e Profile.
    """
    # Campos do usuário
    first_name = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        max_length=150,
        disabled=True,  # Não permitir alteração do nome de usuário
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Campos do perfil
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    receive_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    public_profile = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User  # Usar o modelo de usuário obtido
        fields = ['first_name', 'last_name', 'email', 'username']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            try:
                user_profile = self.instance.profile
                self.fields['profile_pic'].initial = user_profile.profile_pic
                self.fields['receive_notifications'].initial = user_profile.receive_notifications
                self.fields['public_profile'].initial = user_profile.public_profile
            except Profile.DoesNotExist:
                pass
                
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # Garantir que o perfil existe
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Tratar corretamente a imagem do perfil
            if 'profile_pic' in self.cleaned_data and self.cleaned_data['profile_pic']:
                # Só atualiza se houver uma nova imagem
                profile.profile_pic = self.cleaned_data['profile_pic']
                print(f"Salvando nova imagem de perfil: {profile.profile_pic.name}")
            
            # Não use 'else' aqui para não apagar a imagem existente caso nenhuma nova seja enviada
            
            # Atualizar outras configurações do perfil
            profile.receive_notifications = self.cleaned_data.get('receive_notifications', False)
            profile.public_profile = self.cleaned_data.get('public_profile', False)
            
            # Salvar o perfil
            profile.save()
        
        return user