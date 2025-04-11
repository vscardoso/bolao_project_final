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

## Melhorias de UI/UX (Atualizadas em 11/04/2025)
- [x] Redesign do header de lista de bolões
  - [x] Formato compacto em linha única com estatísticas
  - [x] Badges coloridos para diferentes tipos de estatísticas
  - [x] Efeitos visuais sutis nos elementos interativos
- [x] Navegação lateral consistente
  - [x] Mesmo menu lateral em todas as páginas de bolões
  - [x] Extensão correta do template base_pools.html
- [x] Padronização visual
  - [x] Headers de cards com cores consistentes
  - [x] Badges de contagem nos títulos de seção
  - [x] Espaçamento otimizado em todo o layout
- [x] Otimização de espaço
  - [x] Redução de padding e margins excessivos
  - [x] Melhor uso do espaço horizontal e vertical
  - [x] Elementos compactos sem perder legibilidade

## Estrutura de Templates (Adicionada em 11/04/2025)
- **Hierarquia de Templates Atualizada**
  - `base/base.html` - Template base do site inteiro
  - `pools/base_pools.html` - Extensão com menu lateral para módulo de bolões
  - Templates específicos que estendem os templates base

- **Blocos Principais**
  - `content` - Conteúdo principal em base.html
  - `pool_content` - Conteúdo específico em base_pools.html
  - `extra_css` - Para estilos CSS específicos de página
  - `title` - Título da página

## Próximos Passos

### Curto Prazo
- [ ] Implementar o sistema de apostas completo
  - [ ] Criar formulário para realizar apostas
  - [ ] Implementar lógica de pontuação
  - [ ] Validar apostas com base no prazo
- [ ] Implementar sistema de notificações
  - [ ] Notificações de resultados
  - [ ] Lembretes para apostas pendentes
  - [ ] Alertas de movimentação no ranking
- [ ] Revisar todos os templates para remover referências incorretas a URLs (ex: 'home' → 'core:home')
- [ ] Testar responsividade do novo header compacto em dispositivos móveis
- [ ] Verificar se o menu lateral funciona corretamente em todas as páginas relacionadas a bolões
- [ ] Completar a página de edit_profile.html usando o mesmo padrão visual
- [ ] Implementar feedback visual após ações importantes (criar/excluir bolão)

### Médio Prazo
- [ ] Sistema de gerenciamento de pagamentos
  - [ ] Integração com gateway de pagamentos
  - [ ] Confirmação automática de participação após pagamento
- [ ] API REST para futura integração com aplicativo móvel
- [ ] Sistema de convites e compartilhamento
  - [ ] Convites por email com tokens únicos
  - [ ] Compartilhamento em redes sociais
- [ ] Estatísticas e gráficos para bolões
- [ ] Implementar sistema de temas claro/escuro
- [ ] Melhorar a acessibilidade dos formulários e elementos interativos
- [ ] Otimizar carregamento de imagens para melhor desempenho
- [ ] Criar componentes reutilizáveis para badges, cards e outros elementos recorrentes

### Longo Prazo
- [ ] Aplicativo móvel (React Native)
- [ ] Integração com APIs externas para resultados em tempo real
- [ ] Recursos de gamificação (conquistas, níveis, etc.)
- [ ] Monetização (planos premium, recursos adicionais)

## Decisões de Design (Nova seção)

### Escolhas de Design UI/UX
1. **Header Compacto** - Optamos por um header em linha única que economiza espaço vertical enquanto mantém todas as informações essenciais visíveis
2. **Menu Lateral** - Mantido consistente em todas as páginas de bolões para facilitar navegação entre funcionalidades relacionadas
3. **Badges Coloridos** - Sistema visual de cores para diferentes tipos de informação: 
   - Azul (primary): elementos principais/criados pelo usuário
   - Verde (success): participação/elementos ativos
   - Azul-claro (info): informações adicionais/totais

### Padrões de Codificação
1. **Extensão de Templates** - Seguimos uma hierarquia clara: template base → template específico do módulo → template da página
2. **Nomeação de Classes CSS** - Convenções baseadas em função (.stat-badge, .header-content) em vez de aparência
3. **Blocos de Template** - Uso consistente de blocos nomeados para substituição em templates filhos

## Registro da Sessão de Desenvolvimento

### Sessão 11/04/2025
- Identificados e corrigidos problemas críticos de URLs e redirecionamentos
- Redesenhado o header da página de lista de bolões
- Padronizado o layout dos cards e seções
- Corrigida a extensão do template base para incluir menu lateral
- Documentado o progresso e próximos passos

### Plano para Próxima Sessão
1. Completar a implementação da página de edição de perfil de usuário
2. Revisar e corrigir problemas de responsividade em dispositivos móveis
3. Implementar sistema de feedback para ações do usuário
4. Começar a implementação do sistema de apostas

### Estrutura do Banco de Dados
A estrutura principal do banco de dados inclui:
- **User**: Modelo personalizado extendendo AbstractUser
- **Pool**: Bolões com configurações, visibilidade e regras
- **Participation**: Relação entre usuários e bolões, com status de pagamento
- **Match**: Partidas esportivas com detalhes e resultados
- **Bet**: Apostas dos usuários para cada partida

### Relacionamentos importantes:
- User --< Pools (dono)
- User --< Participation >-- Pool (participação)
- User --< Bet >-- Match (apostas)
- Competition >-- Matches (partidas de uma competição)
- Pool -- Competition (bolão de uma competição)

### Configuração de Email
Para ambiente de produção, será necessário configurar um servidor SMTP real:
```python
# Configurações de email para produção
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou outro provedor
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'
DEFAULT_FROM_EMAIL = 'Bolão Online <naoresponda@bolaoonline.com>'
```

## Ideias para Novas Funcionalidades

### Engajamento e Gamificação
1. **Sistema de conquistas e troféus**:
   - Troféus por criar bolões, participar de X bolões, acertar placar exato
   - Medalhas por sequências de acertos (3, 5, 10 acertos consecutivos)
   - Distintivos especiais para momentos raros (acertar todos os jogos de uma rodada)
   - Perfil do usuário com vitrine de troféus e conquistas
   - Notificações quando conquistas são desbloqueadas

2. **Sistema de níveis e experiência**:
   - Pontos de experiência por atividades (apostas, criação de bolões, convites)
   - Níveis que desbloqueiam recursos e personalização (emblemas, cores, avatares)
   - Progressão visual de nível no perfil e dashboard
   - Benefícios por nível (mais bolões simultâneos, recursos premium)

3. **Desafios semanais/mensais**:
   - Objetivos temporários (acerte 3 placares exatos, participe de 2 bolões)
   - Recompensas exclusivas por completar desafios
   - Desafios em grupo para bolões específicos

4. **Competições sazonais**:
   - Torneios especiais entre amigos ou globais
   - Ranking sazonal (melhor do mês, da temporada)
   - Premiações virtuais para os melhores da temporada

### Social e Comunitário
1. **Feed de atividades**:
   - Timeline com apostas de amigos, resultados, conquistas
   - Possibilidade de comentar e reagir (like, haha, uau)
   - Filtros de relevância e personalização

2. **Grupos e comunidades**:
   - Criar grupos além de bolões (ex: torcedores de um time)
   - Fóruns de discussão por competição/esporte
   - Integração com redes sociais para encontrar amigos

3. **Recursos de compartilhamento avançados**:
   - Cards personalizados para compartilhar apostas antes dos jogos
   - Imagens comemorativas para acertos importantes
   - Recursos de "provocação amigável" entre participantes

### Melhorias na Experiência de Apostas
1. **Sugestões inteligentes**:
   - IA que sugere apostas com base no histórico e estatísticas
   - Indicadores de confiança por sugestão
   - Opção de apostar rápido usando sugestões

2. **Modo rascunho de apostas**:
   - Salvar apostas provisórias para alterar depois
   - Comparar diferentes cenários de apostas
   - Lembrete para confirmar antes do prazo final

3. **Visualização avançada de resultados**:
   - Replay animado de como sua posição mudou conforme resultados saíam
   - Gráficos de desempenho por rodada
   - Estatísticas detalhadas sobre seus padrões de apostas

4. **Apostas em grupo**:
   - Criar times dentro de bolões para somar pontuação
   - Competição entre equipes no mesmo bolão
   - Estratégia colaborativa para apostar

### Notificações e Alertas
1. **Sistema de push notifications**:
   - Alertas para jogos prestes a começar (15min, 1h, 24h)
   - Notificações imediatas de resultados de seus jogos
   - Lembretes personalizáveis para apostas pendentes
   - Alertas de mudança significativa no ranking

2. **Central de notificações**:
   - Hub centralizado para todas as mensagens
   - Filtros e categorização (apostas, resultados, social)
   - Opções de assinatura por tipo de notificação

3. **Resumos periódicos**:
   - Email/notificação semanal com desempenho
   - Resumo após rodadas importantes
   - Análise comparativa do seu desempenho vs. média

### Análise e Estatísticas
1. **Dashboard analítico pessoal**:
   - Gráficos de desempenho ao longo do tempo
   - Análise de padrões (times que você acerta mais, horários)
   - Comparativo com média dos participantes

2. **Estatísticas avançadas**:
   - "Calor" das apostas (onde a maioria está apostando)
   - Probabilidades baseadas em histórico
   - Análise de sentimento da comunidade

3. **Histórico detalhado**:
   - Todas suas apostas anteriores com filtros
   - Evolução do seu desempenho por competição/time
   - Exportação de dados pessoais

### Personalização e Customização
1. **Temas e aparência**:
   - Modo claro/escuro
   - Temas por time favorito
   - Personalização de cores da interface

2. **Bolões customizados**:
   - Regras alternativas de pontuação
   - Sistemas de handicap para equilibrar jogadores
   - Categorias personalizadas de apostas

3. **Recursos de acessibilidade**:
   - Alto contraste
   - Compatibilidade com leitores de tela
   - Tamanhos de fonte ajustáveis

### Monetização e Sustentabilidade
1. **Planos premium**:
   - Recursos avançados de estatísticas
   - Limite aumentado de bolões simultâneos
   - Personalização exclusiva
   - Sem anúncios

2. **Microtransações**:
   - Itens cosméticos (avatares, molduras)
   - Moeda virtual para usar em recursos especiais
   - Desbloqueio de conquistas estéticas

3. **Parcerias e patrocínios**:
   - Bolões temáticos patrocinados
   - Prêmios de parceiros para vencedores
   - Integração com programas de fidelidade de sites de apostas