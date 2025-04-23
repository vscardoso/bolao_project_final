from django.core.management.base import BaseCommand
from pools.models import Partida, Match
import requests
from datetime import datetime

class Command(BaseCommand):
    help = 'Atualiza os resultados das partidas a partir de uma API externa'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando atualização de resultados...')
        
        # Exemplo com API fictícia - substitua pela API real escolhida
        url = "https://api.brasileirao.com/jogos/resultados"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Processar cada resultado
            for resultado in data['resultados']:
                try:
                    # Identificar partida pelo ID externo ou por times/data
                    partida = Partida.objects.get(
                        time_casa__sigla=resultado['time_casa'], 
                        time_visitante__sigla=resultado['time_visitante'],
                        data_hora__date=datetime.strptime(resultado['data'], '%Y-%m-%d').date()
                    )
                    
                    # Atualizar resultado
                    if resultado['encerrada']:
                        partida.gols_casa = resultado['gols_casa']
                        partida.gols_visitante = resultado['gols_visitante']
                        partida.encerrada = True
                        partida.save()
                        
                        # Atualizar todos os jogos relacionados em bolões
                        jogos_relacionados = Match.objects.filter(partida_relacionada=partida)
                        for jogo in jogos_relacionados:
                            jogo.atualizar_resultado_automatico()
                            
                        self.stdout.write(self.style.SUCCESS(
                            f'Resultado atualizado: {partida.time_casa} {partida.gols_casa} x {partida.gols_visitante} {partida.time_visitante}'
                        ))
                    
                except Partida.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Partida não encontrada: {resultado["time_casa"]} x {resultado["time_visitante"]}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao processar resultado: {e}'))
            
            self.stdout.write(self.style.SUCCESS('Atualização concluída!'))
        else:
            self.stdout.write(self.style.ERROR(f'Erro ao buscar resultados: {response.status_code}'))