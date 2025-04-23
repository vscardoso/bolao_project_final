# Plano de Testes e Avanço do Projeto Bolão Online

## Visão Geral do Projeto
O Bolão Online é uma plataforma de apostas esportivas colaborativas desenvolvida com Django/Python. Permite aos usuários criar bolões, convidar participantes, fazer apostas em eventos esportivos e acompanhar rankings.

## Status Atual (17/04/2025)

### Funcionalidades Implementadas

#### Sistema de Usuários
- ✅ Registro de usuários com interface moderna
- ✅ Login com recursos de segurança
- ✅ Sistema de logout por inatividade
- ✅ Recuperação de senha

#### Sistema de Bolões
- ✅ Criação e gestão de bolões
- ✅ Descoberta de bolões públicos
- ✅ Participação via convite
- ✅ Visualização de bolões criados/participados

#### Sistema de Apostas
- ✅ Interface moderna para apostas
- ✅ Contador regressivo para início de partidas
- ✅ Sistema de pontuação (10, 5, 3 pontos)
- ✅ Integridade de dados nas apostas
- ✅ Ranking de participantes

#### Melhorias Recentes
- ✅ Correção de problemas de duplicação de apostas
- ✅ Padronização de URLs em templates
- ✅ Validação em tempo real de formulários
- ✅ Redesign das páginas de login e registro
- ✅ Filtros personalizados para simplificação de templates
- ✅ Sistema de geração de dados de teste
- ✅ Correções na visualização de barras de progresso

## I. Testes de Funcionalidade

### 1. Testes de Autenticação
| Teste | Procedimento | Resultado Esperado | Status |
|-------|-------------|-------------------|--------|
| Registro | Criar nova conta com email válido | Conta criada e redirecionado | ✅ |
| Login | Entrar com credenciais válidas | Login bem-sucedido | ✅ |
| Recuperação de senha | Solicitar reset de senha | Email enviado com instruções | ✅ |
| Logout manual | Clicar em "Sair" | Sessão encerrada | ✅ |
| Logout por inatividade | Aguardar tempo de inatividade | Alerta e logout automático | ✅ |
| Acesso protegido | Tentar acessar área restrita sem login | Redirecionado para login | ✅ |

### 2. Testes do Sistema de Bolões
| Teste | Procedimento | Resultado Esperado | Status |
|-------|-------------|-------------------|--------|
| Criar bolão | Preencher formulário de novo bolão | Bolão criado com sucesso | ✅ |
| Editar bolão | Modificar informações de um bolão | Alterações salvas | ⬜ |
| Excluir bolão | Remover um bolão existente | Bolão removido do sistema | ⬜ |
| Listar bolões | Acessar página de descoberta | Lista de bolões disponíveis | ✅ |
| Filtrar bolões | Usar filtros de pesquisa | Resultados filtrados corretamente | ✅ |
| Entrar em bolão | Acessar bolão público e participar | Adicionado como participante | ⬜ |
| Convites | Aceitar convite recebido | Adicionado ao bolão | ⬜ |

### 3. Testes do Sistema de Apostas
| Teste | Procedimento | Resultado Esperado | Status |
|-------|-------------|-------------------|--------|
| Criar aposta | Apostar em partida futura | Aposta registrada | ⬜ |
| Editar aposta | Modificar aposta existente | Aposta atualizada | ⬜ |
| Visualizar apostas | Ver histórico de apostas | Lista de apostas exibida | ⬜ |
| Verificar pontuação | Checar pontos após resultado | Pontuação calculada corretamente | ⬜ |

### 4. Testes do Sistema de Ranking
| Teste | Procedimento | Resultado Esperado | Status |
|-------|-------------|-------------------|--------|
| Visualização de ranking | Acessar a página de ranking do bolão | Tabela de classificação exibida corretamente | ⬜ |
| Ordenação por pontos | Verificar ordem dos participantes | Participantes ordenados por pontuação decrescente | ⬜ |
| Visualização detalhada | Clicar no nome de um participante | Histórico de apostas e estatísticas detalhadas | ⬜ |
| Cálculo correto de posições | Verificar posição com empate de pontos | Mesma posição para participantes com mesma pontuação | ⬜ |
| Indicadores visuais | Verificar ícones e cores de posição | Top 3 com destaque visual diferenciado | ⬜ |

## II. Testes de Interface

### 1. Dashboard do Usuário
| Elemento | Teste | Status |
|----------|-------|--------|
| Cabeçalho de boas-vindas | Verificar exibição do nome do usuário | ✅ |
| Cards de informações | Verificar contadores e links funcionais | ✅ |
| Seção "Meus Bolões" | Verificar lista de bolões participantes | ✅ |
| Seção "Bolões que você criou" | Verificar layout de 3 colunas | ✅ |
| Barra de rolagem vertical | Verificar rolagem sem barra horizontal | ✅ |
| Filtro de pesquisa | Verificar filtragem por nome de bolão | ✅ |
| Botões de ações | Verificar funcionalidade Ver e Editar | ✅ |

### 2. Descoberta de Bolões
| Elemento | Teste | Status |
|----------|-------|--------|
| Filtros por esporte | Verificar filtragem visual | ✅ |
| Cards de bolão | Verificar cores específicas por esporte | ✅ |
| Barra de progresso | Verificar exibição correta de ocupação | ✅ |
| Indicadores visuais | Verificar ícones de esporte e status | ✅ |
| Responsividade | Testar em diferentes tamanhos de tela | ✅ |

### 3. Otimizações de Interface Implementadas
- Layout de 3 colunas para exibir mais bolões com menos rolagem
- Campo de pesquisa no cabeçalho para filtragem rápida de bolões
- Rolagem vertical limitada com max-height para melhor navegação
- Layout responsivo que adapta de 3 para 2 e 1 coluna em dispositivos menores
- Contador de bolões visíveis durante filtragem
- Prevenção de rolagem horizontal com overflow-x: hidden
- Badges visuais para status público/privado do bolão
- Cores específicas por esporte para melhor identificação visual
- Barra de progresso com variação de cores baseada na ocupação

## III. Plano de Testes Detalhado (Pendentes)

### 1. Edição de Bolão

| Passo | Ação | Verificação Esperada |
|-------|------|----------------------|
| 1 | Acessar a lista de bolões criados pelo usuário | Lista exibida corretamente |
| 2 | Clicar no botão "Editar" em um bolão específico | Página de edição carregada com dados preenchidos |
| 3 | Modificar nome, descrição e limite de participantes | Campos aceitam alterações |
| 4 | Salvar as alterações | Redirecionamento para detalhes do bolão |
| 5 | Verificar se as alterações foram aplicadas | Dados atualizados exibidos corretamente |

**Casos especiais para testar:**
- Tentar deixar campos obrigatórios em branco
- Alterar de bolão público para privado (verificar visibilidade na descoberta)
- Editar bolão com apostas já existentes (não deve permitir alterações críticas)

### 2. Exclusão de Bolão

| Passo | Ação | Verificação Esperada |
|-------|------|----------------------|
| 1 | Acessar detalhes de um bolão criado pelo usuário | Detalhes exibidos |
| 2 | Clicar no botão "Excluir" | Modal de confirmação exibido |
| 3 | Confirmar a exclusão | Redirecionamento para lista de bolões |
| 4 | Verificar se o bolão foi removido da lista | Bolão não aparece mais na listagem |

### 3. Sistema de Apostas

| Passo | Ação | Verificação Esperada |
|-------|------|----------------------|
| 1 | Acessar bolão com partidas disponíveis | Lista de partidas exibida |
| 2 | Selecionar uma partida futura | Formulário de aposta carregado |
| 3 | Preencher placares para ambos os times | Valores aceitos corretamente |
| 4 | Enviar aposta | Confirmação de aposta registrada |
| 5 | Verificar na lista de apostas | Aposta aparece com valores corretos |
| 6 | Editar aposta existente | Formulário preenchido com valores atuais |
| 7 | Modificar valores e salvar | Aposta atualizada sem duplicação |
| 8 | Verificar pontuação após resultado | Pontos calculados conforme regras |

## IV. Bugs e Problemas Identificados

1. **Problema na Barra de Progresso**: Erro CSS quando pool.max_participants é zero ou nulo
   - **Solução**: Implementada verificação de max_participants > 0 antes do cálculo de porcentagem
   - **Status**: ✅ Corrigido

2. **Limitações no Código de Templates**: Condicionais aninhados para cores e ícones por esporte
   - **Solução**: Implementados filtros personalizados em pools/templatetags/pool_filters.py
   - **Status**: ✅ Corrigido

3. **URLs para sistema de ranking avançado não implementadas**: Erro ao tentar iniciar o servidor
   - **Solução**: Comentadas as URLs que apontam para views não implementadas
   - **Status**: ✅ Corrigido temporariamente
   - **Próximos passos**: Implementar as views de ranking avançado quando necessário

4. **Template pool_update.html não encontrado**: Erro ao tentar editar bolão
   - **Solução**: Criado template base para edição de bolões
   - **Status**: ✅ Corrigido

## V. Próximos Passos

1. Implementar funcionalidades avançadas de ranking (weekly, monthly, statistics, etc.)
2. Completar testes pendentes do sistema de apostas
3. Implementar testes automatizados para funcionalidades críticas
4. Expandir o sistema de geração de dados para incluir apostas e resultados
5. Desenvolver documentação de usuário final
6. Preparar ambiente de produção para lançamento

Este documento será continuamente atualizado conforme o progresso dos testes.