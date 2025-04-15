from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  # Importar settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return self.username

class Profile(models.Model):
    # Substituir a referência direta por settings.AUTH_USER_MODEL
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    receive_notifications = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=True)
    # Outros campos do perfil...

    def __str__(self):
        return f'{self.user.username} Profile'

# Criar um perfil automaticamente quando um usuário é criado
@receiver(post_save, sender=settings.AUTH_USER_MODEL)  # Também corrigir aqui
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)  # E aqui
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()
