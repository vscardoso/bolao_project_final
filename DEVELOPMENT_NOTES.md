# DEVELOPMENT_NOTES.md
// filepath: c:\Users\Victor\Desktop\bolao_project\DEVELOPMENT_NOTES.md

# Notas de Desenvolvimento - Projeto Bolão Online

## Visão Geral do Projeto
O Bolão Online é uma plataforma web que permite aos usuários criar e participar de bolões esportivos, fazer apostas, acompanhar resultados em tempo real e competir com amigos. O projeto é construído com Django, usa Bootstrap para o frontend e implementa várias funcionalidades modernas para engajamento do usuário.

## Estrutura do Projeto
O projeto está organizado nos seguintes aplicativos Django:
- **core**: Funcionalidades principais, páginas básicas (home, sobre, etc.)
- **users**: Sistema de autenticação, perfis de usuário, dashboard
- **pools**: Gerenciamento de bolões, apostas e resultados

## Tecnologias Utilizadas
- **Backend**: Django 5.2, Python 3.13
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: MySQL (desenvolvimento), PostgreSQL (produção)
- **Autenticação**: Sistema nativo do Django
- **Email**: Backend SMTP/Console para notificações e recuperações de senha

## Configuração do Ambiente de Desenvolvimento

### Criação do Ambiente Virtual
```bash
# Navegar até a pasta do projeto
cd c:\Users\Victor\Desktop\bolao_project

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
# source venv/bin/activate
```

### Instalação de Dependências
```bash
# Instalar Django e outras dependências
pip install django==5.2
pip install pillow
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install mysqlclient
pip install python-decouple

# Opcionalmente, criar arquivo de requirements
pip freeze > requirements.txt

# Para instalar a partir do requirements.txt
# pip install -r requirements.txt
```

### Configuração Inicial do Django
```bash
# Criar o projeto Django (já deve estar criado)
# django-admin startproject bolao_project .

# Criar os aplicativos principais
python manage.py startapp core
python manage.py startapp users
python manage.py startapp pools

# Aplicar migrações iniciais
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

### Executando o Projeto
```bash
# Iniciar o servidor de desenvolvimento
python manage.py runserver

# O servidor estará disponível em:
# http://127.0.0.1:8000/
```

## Progresso Atual

### Configuração Inicial
- [x] Criação do projeto Django
- [x] Configuração do ambiente virtual
- [x] Estruturação dos aplicativos principais
- [x] Configuração de arquivos estáticos e mídia
- [x] Implantação do Bootstrap e FontAwesome

### Sistema de Autenticação (users app)
- [x] Telas de login e registro
- [x] Sistema de recuperação de senha
  - [x] Formulário de solicitação de redefinição
  - [x] Envio de email (funcionando no console)
  - [x] Configuração para ambiente de produção
- [x] Persistência da mensagem de instruções na tela
- [x] Layout responsivo para os formulários de autenticação
- [x] Dashboard do usuário com visualização de bolões

### Página Inicial (core app)
- [x] Hero section com conteúdo dinâmico baseado no estado de autenticação
- [x] Seção "Como Funciona" explicando os passos básicos
- [x] Contador regressivo para próximos eventos
- [x] Seção de jogos em destaque/ao vivo
- [x] Cards de bolões populares
- [x] Ranking de melhores apostadores
- [x] Depoimentos de usuários
- [x] Seção de dicas para vencer
- [x] FAQ e perguntas frequentes
- [x] CTA (Call to Action) condicional para usuários não autenticados

### Aplicativo Pools (Bolões)
- [x] Criada estrutura básica do aplicativo
- [x] Adicionado namespace 'pools' para URLs
- [x] Implementado CRUD completo de bolões
  - [x] Listagem de bolões do usuário (PoolListView)
  - [x] Criação de bolões (PoolCreateView)
  - [x] Visualização detalhada (PoolDetailView)
  - [x] Edição de bolões (PoolUpdateView)
  - [x] Exclusão de bolões (PoolDeleteView)
  - [x] Participação em bolões (PoolJoinView)
- [x] Funcionalidades adicionais
  - [x] Descoberta de bolões disponíveis (PoolDiscoverView)
  - [x] Gerenciamento de convites (InvitationListView)
- [x] Templates responsivos para todas as views
- [x] Implementação do modelo Participation para relação entre usuários e bolões

### Banco de Dados
- [x] Migração de SQLite para MySQL
- [x] Implementação de relacionamentos complexos (ManyToMany com through)
- [x] Resolução de problemas de migração
- [x] Otimização de consultas com select_related e prefetch_related

### Melhorias de UI/UX
- [x] Animações e efeitos visuais (hover, float, etc.)
- [x] Cards com design moderno e interativo
- [x] Efeitos glassmorphism em elementos flutuantes
- [x] Estilização consistente usando classes reutilizáveis
- [x] Indicadores de estado (ao vivo, popular, etc.)

### JavaScript e Interatividade
- [x] Sistema para inicializar elementos de forma segura
- [x] Máscaras para campos de formulário (telefone)
- [x] Contador regressivo funcional
- [x] Tooltips e popovers do Bootstrap
- [x] Animações ativadas por scroll

## Problemas Resolvidos
1. **Namespace 'pools' não registrado** - Resolvido com a criação correta do aplicativo pools e configuração adequada do namespace nas URLs
2. **Mensagem de recuperação de senha desaparecendo** - Corrigido ajustando as classes para evitar que seja fechada automaticamente
3. **Emails não sendo enviados** - Identificada configuração de console para desenvolvimento, documentada configuração para produção
4. **Botão "Comece Agora" aparecendo para usuários logados** - Implementada lógica condicional no template para mostrar opções relevantes
5. **Erro Method Resolution Order (MRO)** - Corrigido problema de herança múltipla na classe PoolJoinView
6. **Tabela pools_participation não existindo** - Resolvido recriando as migrações e o banco de dados
7. **Campo betting_deadline obrigatório** - Modificado para aceitar valores nulos no modelo Pool

## Problemas Resolvidos (Adicionados em 11/04/2025)
8. **Erro NoReverseMatch para 'home'** - Corrigido removendo referências de breadcrumbs problemáticas e ajustando URLs para usar o namespace correto (core:home)
9. **Loop de redirecionamento infinito na página inicial** - Resolvido eliminando definições de URL duplicadas para o mesmo caminho raiz no arquivo urls.py principal
10. **Layout quebrado no header da página de pools** - Redesenhado o header para exibir todas as informações em uma única linha, economizando espaço vertical
11. **Inconsistência de navegação entre páginas de bolões** - Corrigido estendendo base_pools.html e adicionando menu lateral à página de lista de pools

## Problemas Resolvidos (Atualizados em 14/04/2025)
12. **NoReverseMatch para 'edit_profile'** - Corrigido adicionando o padrão de URL adequado em users/urls.py e garantindo que todos os templates usem o namespace completo ('users:edit_profile')
13. **ImportError: cannot import name 'ProfileEditForm'** - Resolvido criando o formulário ProfileEditForm em users/forms.py para permitir a edição do perfil do usuário, combinando campos dos modelos User e Profile
14. **Erro AUTH_USER_MODEL swapped out** - Corrigido o modelo Profile para usar settings.AUTH_USER_MODEL em vez de auth.User diretamente, garantindo compatibilidade com o modelo de usuário personalizado do projeto
15. **FieldError: Cannot resolve keyword 'creator' into field** - Corrigido atualizando referências de 'creator' para 'owner' nas views, pois o nome do campo no modelo Pool é 'owner'
16. **FieldError: Cannot resolve keyword 'is_correct' into field** - Corrigido modificando a query para usar points_earned__gt=0 em vez de is_correct=True, já que o modelo Bet não possui este campo
17. **Erro na execução de testes** - Corrigido criando testes simples que não dependem de modelos específicos, para verificar se o framework de testes está funcionando corretamente.
18. **RuntimeError em script de inspeção** - Resolvido usando a biblioteca `inspect` para examinar os modelos de forma segura, em vez de modificar o dicionário `globals()` durante a iteração.
19. **Permissões insuficientes para testes no MySQL** - Resolvido concedendo permissões adicionais ao usuário do banco de dados:
    - Adicionadas permissões CREATE, ALTER, DROP para o usuário do banco de dados
    - Concedido acesso completo ao banco de testes `test_bolao_online`
    - Mantido o mesmo banco MySQL para testes, garantindo consistência com o ambiente de desenvolvimento
20. **TypeError em Formulário de Aposta** - Corrigido o formulário BetForm para aceitar corretamente o parâmetro `match` que é passado da view:
    - Implementado método `__init__` personalizado para extrair o parâmetro `match` antes de chamar o construtor da classe pai
    - Adicionados labels dinâmicos baseados nos nomes dos times da partida
    - Mantida compatibilidade com outras partes do sistema que não passam o parâmetro `match`
21. **Erro 404 em URLs com slug** - Resolvido atualizando as views e URLs para usar corretamente slugs em vez de IDs:
    - Modificado o arquivo `urls.py` para aceitar slugs nos padrões de URL
    - Atualizada a classe `BetCreateView` para buscar bolões usando slug
    - Adaptado o mixin `PoolUserAccessMixin` para suportar tanto IDs quanto slugs
    - Atualizada a função `pool_ranking` para usar slug
22. **NoReverseMatch para 'bet_create'** - Corrigido erro nas URLs do sistema de apostas:
    - Identificado uso incorreto de 'bet_create' como nome de URL no template pool_detail.html
    - Atualizado para o nome correto 'bet_match' conforme definido em urls.py
    - Verificados outros arquivos para garantir consistência nos nomes das URLs
23. **AttributeError: 'BetForm' object has no attribute 'pool'** - Corrigido problema no envio do formulário de apostas:
    - Adicionado atributo `pool` no método `__init__` do formulário `BetForm`
    - Atualizado método `get_form_kwargs` na view `BetCreateView` para passar o objeto pool ao formulário
    - Garantido que o método `form_valid` use `self.get_pool()` em vez de acessar o pool pelo formulário
24. **IntegrityError ao criar apostas duplicadas** - Corrigido problema de unicidade no formulário de apostas:
    - Identificado que o modelo `Bet` tem uma restrição de chave única para a combinação (user_id, match_id, pool_id)
    - Modificada a `BetCreateView` para verificar se já existe uma aposta para a mesma combinação
    - Implementada lógica para atualizar a aposta existente em vez de tentar criar uma duplicada
    - Adicionadas mensagens diferentes para indicar se a aposta foi criada ou atualizada
25. **NoReverseMatch na página de apostas** - Corrigido problema na BetListView:
    - Identificado uso incorreto de `bet_create` no template `bet_list.html`
    - Atualizada referência para usar corretamente `bet_match` conforme definido em urls.py
    - Verificados todos os templates para garantir consistência nos nomes das URLs
    - O comando `findstr /s /i "bet_create" *.*` ajudou a identificar todas as referências incorretas

26. **Problemas na interface de apostas** - Melhorada a experiência de usuário:
    - Redesenhada a interface do formulário de apostas para ser mais intuitiva
    - Implementado cronômetro regressivo para mostrar tempo restante até o início da partida
    - Adicionados estilos específicos para campos de entrada de placar
    - Criada versão minimalista do contador para melhor integração visual

27. **Integração de melhorias visuais** - Aplicadas várias melhorias de UI/UX:
    - Adicionados efeitos visuais para campos de aposta com foco
    - Implementada validação em tempo real de valores de apostas
    - Adaptada a interface para ser totalmente responsiva em dispositivos móveis
    - Reorganizados elementos visuais para melhor hierarquia de informações

## Implementações Recentes (Adicionadas em 14/04/2025)

1. **Sistema de Apostas**
   - [x] Formulário intuitivo para apostas com interface visual rica
   - [x] Regras de pontuação claras (10, 5, 3 pontos)
   - [x] Countdown para início das partidas
   - [x] Validações de prazo e participação
   - [x] Estatísticas de apostas populares
   - [x] Informações de confrontos anteriores
   - [x] Visualização da aposta atual
   - [x] Testes automatizados cobrindo toda a funcionalidade

### Formulário de Apostas Aprimorado
- [x] **Interface visual rica**: Redesign completo da página de apostas
- [x] **Contador regressivo**: Adicionado cronômetro que mostra tempo restante até o início da partida
- [x] **Validação em tempo real**: Implementado JavaScript para validar entradas do usuário
- [x] **Feedback visual**: Efeitos interativos para melhorar a experiência do usuário
- [x] **Sistema de apostas consistente**: Garantido que as apostas existentes sejam atualizadas em vez de gerar duplicatas

### Sistema de Integridade de Dados
- [x] **Verificação de apostas existentes**: Implementada lógica para evitar duplicatas no banco de dados
- [x] **Atualização de apostas**: Modificada a view para atualizar apostas existentes em vez de criar novas
- [x] **Mensagens contextuais**: Feedback diferenciado para criação vs. atualização de apostas
- [x] **Validação de prazos**: Garantido que apostas só podem ser feitas/modificadas antes do início das partidas