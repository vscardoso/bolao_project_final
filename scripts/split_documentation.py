import os
import re

def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    # Definir caminhos
    source_file = "c:\\Users\\Victor\\Desktop\\bolao_project\\DEVELOPMENT_NOTES.md"
    docs_dir = "c:\\Users\\Victor\\Desktop\\bolao_project\\docs"
    
    # Criar diretório de documentação
    create_directory_if_not_exists(docs_dir)
    
    # Ler o conteúdo do arquivo original
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrair seções principais
    sections = {
        "overview.md": re.search(r"## Visão Geral do Projeto.*?(?=##)", content, re.DOTALL),
        "structure.md": re.search(r"## Estrutura do Projeto.*?(?=##)", content, re.DOTALL),
        "setup.md": re.search(r"## Configuração do Ambiente.*?(?=##)", content, re.DOTALL),
        "issues-solved.md": re.search(r"## Problemas Resolvidos.*?(?=## Implementações Recentes)", content, re.DOTALL),
        "recent-implementations.md": re.search(r"## Implementações Recentes.*", content, re.DOTALL)
    }
    
    # Criar arquivo README principal
    with open(os.path.join(docs_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write("""# Documentação do Projeto Bolão Online

Este diretório contém a documentação organizada do projeto.

## Estrutura de Documentação

- [Visão Geral](overview.md) - Descrição do projeto e tecnologias
- [Configuração](setup.md) - Instruções de instalação e configuração
- [Estrutura do Projeto](structure.md) - Organização dos aplicativos e componentes
- [Changelog](changelog.md) - Histórico de mudanças e atualizações
- [Problemas Resolvidos](issues-solved.md) - Lista de problemas enfrentados e soluções
- [Implementações Recentes](recent-implementations.md) - Novas funcionalidades adicionadas

## Desenvolvimento Atual

Para ver as tarefas em andamento e próximos passos, consulte nosso [quadro de tarefas](tasks.md).
""")
    
    # Criar arquivos de seção
    for filename, section_match in sections.items():
        if section_match:
            content = section_match.group(0)
        else:
            content = f"# {filename.replace('.md', '').title()}\n\nConteúdo pendente de migração."
            
        with open(os.path.join(docs_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Criar arquivo de changelog vazio
    with open(os.path.join(docs_dir, "changelog.md"), 'w', encoding='utf-8') as f:
        f.write("""# Changelog

## Versão 0.1.0 (15/04/2025)
- Reorganizada a documentação para melhor gerenciamento
- Implementado sistema de logout por inatividade
- Melhoradas as páginas de login e registro
- Corrigidos problemas no sistema de apostas
""")
    
    # Criar arquivo de tarefas vazio
    with open(os.path.join(docs_dir, "tasks.md"), 'w', encoding='utf-8') as f:
        f.write("""# Quadro de Tarefas

## Em Andamento
- [ ] Melhorias no sistema de apostas
- [ ] Implementação de notificações por email
- [ ] Desenvolvimento da funcionalidade de convites

## Próximos Passos
- [ ] Sistema de pagamentos
- [ ] Integração com APIs de resultados esportivos
- [ ] Desenvolvimento de aplicativo móvel
""")

    print("Documentação dividida com sucesso!")

if __name__ == "__main__":
    main()