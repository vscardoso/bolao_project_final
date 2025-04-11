from django.urls import path
from . import views

app_name = 'pools'

urlpatterns = [
    # Listar bolões
    path('', views.PoolListView.as_view(), name='list'),
    
    # Criar bolão
    path('create/', views.PoolCreateView.as_view(), name='create'),
    
    # Descobrir bolões
    path('discover/', views.PoolDiscoverView.as_view(), name='discover'),
    
    # Convites
    path('invitations/', views.InvitationListView.as_view(), name='invitations'),
    
    # Detalhes, editar, excluir e participar de bolão
    path('<slug:slug>/', views.PoolDetailView.as_view(), name='detail'),
    path('<slug:slug>/update/', views.PoolUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', views.PoolDeleteView.as_view(), name='delete'),
    path('<slug:slug>/join/', views.PoolJoinView.as_view(), name='join'),
    
    # Apostas
    path('<slug:slug>/apostas/', views.BetListView.as_view(), name='bet_list'),
    path('<slug:slug>/apostar/<int:match_id>/', views.BetCreateView.as_view(), name='bet_create'),

    # Meus bolões criados e participados
    path('my-created/', views.MyCreatedPoolsView.as_view(), name='my_created'),
    path('my-joined/', views.MyJoinedPoolsView.as_view(), name='my_joined'),
    path('discover/', views.DiscoverPoolsView.as_view(), name='discover'),
]