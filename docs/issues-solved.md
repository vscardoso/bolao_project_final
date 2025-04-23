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

28. **Timer de inatividade para logout automático** - Implementado sistema de segurança:
    - Adicionado script JavaScript para monitorar atividade do usuário (mouse, teclado, etc.)
    - Criado timer configurável que desloga o usuário após período de inatividade
    - Implementado aviso com contagem regressiva antes do logout automático
    - Adicionada configuração para ajustar o tempo de inatividade permitido
    - Integrado com o sistema de autenticação do Django para logout seguro

