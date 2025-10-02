#!/bin/bash

# ========================================
# CHECKLIST DE DEPLOY - BOLÃO ONLINE
# ========================================

echo "========================================="
echo "  CHECKLIST DE DEPLOY - BOLÃO ONLINE"
echo "========================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar
check_item() {
    if [ "$2" = "ok" ]; then
        echo -e "${GREEN}✓${NC} $1"
    elif [ "$2" = "warning" ]; then
        echo -e "${YELLOW}⚠${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
    fi
}

# 1. Verificar arquivos de ambiente
echo "1. ARQUIVOS DE AMBIENTE"
if [ -f ".env.example" ]; then
    check_item ".env.example existe" "ok"
else
    check_item ".env.example NÃO encontrado" "error"
fi

if [ -f ".env.production.example" ]; then
    check_item ".env.production.example existe" "ok"
else
    check_item ".env.production.example NÃO encontrado" "error"
fi

if [ -f ".env" ]; then
    check_item ".env existe (local)" "ok"
    # Verificar se .env está no .gitignore
    if grep -q "^\.env$" .gitignore; then
        check_item ".env está no .gitignore" "ok"
    else
        check_item ".env NÃO está no .gitignore" "error"
    fi
else
    check_item ".env NÃO encontrado" "warning"
fi

echo ""

# 2. Verificar settings de produção
echo "2. CONFIGURAÇÕES DE PRODUÇÃO"
if [ -f "bolao_config/settings_production.py" ]; then
    check_item "settings_production.py existe" "ok"
else
    check_item "settings_production.py NÃO encontrado" "error"
fi

echo ""

# 3. Verificar dependências
echo "3. DEPENDÊNCIAS"
if [ -f "requirements.txt" ]; then
    check_item "requirements.txt existe" "ok"
    
    # Verificar se whitenoise está instalado
    if grep -q "whitenoise" requirements.txt; then
        check_item "whitenoise instalado (estáticos)" "ok"
    else
        check_item "whitenoise NÃO encontrado - ADICIONAR" "warning"
    fi
    
    # Verificar se gunicorn está instalado
    if grep -q "gunicorn" requirements.txt; then
        check_item "gunicorn instalado (servidor)" "ok"
    else
        check_item "gunicorn NÃO encontrado - ADICIONAR" "warning"
    fi
else
    check_item "requirements.txt NÃO encontrado" "error"
fi

echo ""

# 4. Verificar estrutura de diretórios
echo "4. ESTRUTURA DE DIRETÓRIOS"
if [ -d "static" ]; then
    check_item "Diretório static/ existe" "ok"
else
    check_item "Diretório static/ NÃO existe" "error"
fi

if [ -d "templates" ]; then
    check_item "Diretório templates/ existe" "ok"
else
    check_item "Diretório templates/ NÃO existe" "error"
fi

if [ ! -d "logs" ]; then
    echo -e "${YELLOW}⚠${NC} Criando diretório logs/"
    mkdir -p logs
fi
check_item "Diretório logs/ existe" "ok"

echo ""

# 5. Git status
echo "5. CONTROLE DE VERSÃO"
if git rev-parse --git-dir > /dev/null 2>&1; then
    check_item "Repositório Git inicializado" "ok"
    
    # Verificar se há arquivos .env commitados
    if git ls-files | grep -q "\.env$"; then
        check_item "ATENÇÃO: .env está commitado no Git!" "error"
        echo "   Execute: git rm --cached .env"
    else
        check_item ".env NÃO está no Git" "ok"
    fi
else
    check_item "Git NÃO inicializado" "warning"
fi

echo ""

# 6. Próximos passos
echo "========================================="
echo "  PRÓXIMOS PASSOS PARA DEPLOY"
echo "========================================="
echo ""
echo "1. CONFIGURAR AMBIENTE DE PRODUÇÃO:"
echo "   - Copie .env.production.example para .env (no servidor)"
echo "   - Preencha TODAS as variáveis de ambiente"
echo "   - Gere nova SECRET_KEY:"
echo "     python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
echo ""
echo "2. ADICIONAR DEPENDÊNCIAS DE PRODUÇÃO:"
echo "   pip install whitenoise gunicorn"
echo "   pip freeze > requirements.txt"
echo ""
echo "3. TESTAR SETTINGS DE PRODUÇÃO:"
echo "   python manage.py check --deploy --settings=bolao_config.settings_production"
echo ""
echo "4. COLETAR ARQUIVOS ESTÁTICOS:"
echo "   python manage.py collectstatic --noinput --settings=bolao_config.settings_production"
echo ""
echo "5. RODAR MIGRATIONS:"
echo "   python manage.py migrate --settings=bolao_config.settings_production"
echo ""
echo "6. INICIAR COM GUNICORN:"
echo "   gunicorn bolao_config.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=bolao_config.settings_production"
echo ""
echo "========================================="
