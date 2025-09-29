#!/usr/bin/env python3
"""
Script para testar a API Football-Data.org
Verifica se a chave está funcionando e mostra informações da conta
"""

import requests
import json
from django.conf import settings
import os
import sys
from pathlib import Path

# Configurar Django
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')

import django
django.setup()

def test_football_api():
    """Testa a API Football-Data.org"""
    
    api_key = settings.FOOTBALL_DATA_API_KEY
    base_url = "https://api.football-data.org/v4"
    
    headers = {
        'X-Auth-Token': api_key,
        'User-Agent': 'BolaoPython/1.0'
    }
    
    print("🏈 TESTE DA API FOOTBALL-DATA.ORG")
    print("=" * 60)
    print(f"🔑 API Key: {api_key}")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    # Teste 1: Informações da conta
    print("📊 1. INFORMAÇÕES DA CONTA")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando!")
            print(f"Dados: {json.dumps(data, indent=2)}")
        elif response.status_code == 403:
            print("❌ Chave inválida ou sem permissão")
        elif response.status_code == 429:
            print("⚠️ Limite de requisições atingido")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    
    print()
    
    # Teste 2: Listar competições
    print("🏆 2. COMPETIÇÕES DISPONÍVEIS")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/competitions", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            competitions = data.get('competitions', [])
            
            print(f"✅ {len(competitions)} competições encontradas!")
            print("\n📋 Principais competições:")
            
            # Mostrar as primeiras 5 competições
            for comp in competitions[:5]:
                area = comp.get('area', {}).get('name', 'N/A')
                name = comp.get('name', 'N/A')
                code = comp.get('code', 'N/A')
                print(f"   • {name} ({code}) - {area}")
                
            if len(competitions) > 5:
                print(f"   ... e mais {len(competitions) - 5} competições")
                
        elif response.status_code == 403:
            print("❌ Sem permissão para acessar competições")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    
    print()
    
    # Teste 3: Premier League (se disponível)
    print("⚽ 3. TESTE PREMIER LEAGUE")
    print("-" * 30)
    try:
        # Premier League ID: 2021
        response = requests.get(f"{base_url}/competitions/PL", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Premier League acessível!")
            print(f"Nome: {data.get('name', 'N/A')}")
            print(f"Área: {data.get('area', {}).get('name', 'N/A')}")
            print(f"Temporada atual: {data.get('currentSeason', {}).get('startDate', 'N/A')}")
            
        elif response.status_code == 403:
            print("❌ Premier League não disponível no plano atual")
        elif response.status_code == 404:
            print("❌ Premier League não encontrada")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    
    print()
    
    # Informações sobre limites
    print("📈 4. INFORMAÇÕES DE LIMITE")
    print("-" * 30)
    print("ℹ️ Plano gratuito Football-Data.org:")
    print("   • 10 requisições por minuto")
    print("   • Competições limitadas")
    print("   • Dados básicos disponíveis")
    print()
    print("💡 Para mais recursos:")
    print("   • https://www.football-data.org/pricing")
    
    print()
    print("=" * 60)
    print("🎯 Teste da API concluído!")

if __name__ == "__main__":
    test_football_api()