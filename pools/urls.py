from django.urls import path
from . import views

app_name = 'pools'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Teste do formulário de apostas aprimorado
    path('test-bet-form/', views.test_bet_form, name='test_bet_form'),
    path('test-bet-form/<int:match_id>/', views.test_bet_form, name='test_bet_form_match'),
    path('test-bet-form/<int:match_id>/<int:pool_id>/', views.test_bet_form, name='test_bet_form_full'),
    
    # Listar bolões
    path('', views.PoolListView.as_view(), name='list'),
    
    # Criar bolão
    path('create/', views.PoolCreateView.as_view(), name='create'),
    path('create/wizard/', views.PoolCreateWizardView.as_view(), name='create_wizard'),
    path('create/success/<slug:slug>/', views.PoolCreateSuccessView.as_view(), name='create_success'),
    path('create/brasileirao/', views.criar_bolao_brasileirao, name='criar_bolao_brasileirao'),
    
    # Descobrir bolões (usando uma única view para esta rota)
    path('discover/', views.PoolDiscoverView.as_view(), name='discover'),
    
    # Convites
    path('invitations/', views.InvitationListView.as_view(), name='all_invitations'), 
    
    # Meus bolões criados e participados - MOVA ESTAS ROTAS PARA ANTES DO PADRÃO GENÉRICO
    path('my-created/', views.MyCreatedPoolsView.as_view(), name='my_created'),
    path('my-joined/', views.MyJoinedPoolsView.as_view(), name='my_joined'),
    
    # Seção de Ranking - Melhorada
    path('<slug:slug>/ranking/', views.pool_ranking, name='ranking'),  # Ranking geral
    
    # Apostas
    path('<slug:slug>/apostas/', views.BetListView.as_view(), name='bet_list'),
    path('<slug:slug>/apostar/<int:match_id>/', views.bet_match, name='bet_match'),
    
    # Convites específicos para bolões
    path('<slug:slug>/convites/', views.InvitationListView.as_view(), name='invitations'),
    path('<slug:slug>/convidar/', views.InvitationCreateView.as_view(), name='send_invitation'),
    path('convite/<str:code>/aceitar/', views.accept_invitation, name='accept_invitation'),
    path('convite/<str:code>/recusar/', views.decline_invitation, name='decline_invitation'),
    
    # Detalhes, editar, excluir e participar de bolão - ESTAS ROTAS PRECISAM VIR DEPOIS DAS ROTAS ESPECÍFICAS
    path('<slug:slug>/update/', views.PoolUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', views.PoolDeleteView.as_view(), name='delete'),
    path('<slug:slug>/join/', views.PoolJoinView.as_view(), name='join'),
    
    # ESTA ROTA GENÉRICA DEVE SER A ÚLTIMA
    path('<slug:slug>/', views.PoolDetailView.as_view(), name='detail'),
]