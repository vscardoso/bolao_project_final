from django.shortcuts import render
from pools.models import Pool

def home(request):
    # Buscar alguns bolões para exibir na página inicial
    featured_pools = Pool.objects.all().order_by('-created_at')[:6]
    
    context = {
        'featured_pools': featured_pools,
    }
    
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')
