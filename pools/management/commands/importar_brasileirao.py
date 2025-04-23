from django.core.management.base import BaseCommand
from pools.models import Campeonato, Time, Partida, Sport
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa dados do Campeonato Brasileiro 2025'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando importação do Campeonato Brasileiro 2025...')
        
        # Criar ou obter o esporte Futebol
        futebol, created = Sport.objects.get_or_create(name='Futebol')
        
        # Criar campeonato
        brasileirao, created = Campeonato.objects.get_or_create(
            nome='Campeonato Brasileiro',
            temporada='2025',
            defaults={
                'esporte': futebol,
                'inicio': datetime(2025, 4, 20).date(),
                'fim': datetime(2025, 12, 8).date(),
            }
        )
        
        if not created:
            self.stdout.write(self.style.WARNING(f'Campeonato Brasileiro 2025 já existe.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Campeonato criado: {brasileirao}'))
            
        # Lista de times da Série A 2025
        times = [
            ('Flamengo', 'FLA'),
            ('Palmeiras', 'PAL'),
            ('São Paulo', 'SPO'),
            ('Atlético-MG', 'CAM'),
            ('Fluminense', 'FLU'),
            ('Botafogo', 'BOT'),
            ('Corinthians', 'COR'),
            ('Internacional', 'INT'),
            ('Grêmio', 'GRE'),
            ('Cruzeiro', 'CRU'),
            ('Vasco', 'VAS'),
            ('Athletico-PR', 'CAP'),
            ('Bahia', 'BAH'),
            ('Santos', 'SAN'),
            ('Fortaleza', 'FOR'),
            ('Red Bull Bragantino', 'RBB'),
            ('Cuiabá', 'CUI'),
            ('Juventude', 'JUV'),
            ('Vitória', 'VIT'),
            ('Atlético-GO', 'ACG'),
        ]
        
        # Criar times
        times_obj = {}
        for nome, sigla in times:
            time, created = Time.objects.get_or_create(
                nome=nome,
                sigla=sigla,
                campeonato=brasileirao
            )
            times_obj[sigla] = time
            if created:
                self.stdout.write(f'Time criado: {time}')
        
        # Gerar jogos da primeira rodada
        rodada = 1
        jogos = [
            ('FLA', 'PAL', '2025-04-20 16:00'),
            ('SPO', 'CAM', '2025-04-20 18:30'),
            ('FLU', 'BOT', '2025-04-20 20:00'),
            ('COR', 'INT', '2025-04-21 19:00'),
            ('GRE', 'CRU', '2025-04-21 21:30'),
            ('VAS', 'CAP', '2025-04-22 19:00'),
            ('BAH', 'SAN', '2025-04-22 20:00'),
            ('FOR', 'RBB', '2025-04-22 21:00'),
            ('CUI', 'JUV', '2025-04-23 19:00'),
            ('VIT', 'ACG', '2025-04-23 21:00'),
        ]
        
        # Criar jogos
        for casa, visitante, data_hora in jogos:
            data_obj = datetime.strptime(data_hora, '%Y-%m-%d %H:%M')
            partida, created = Partida.objects.get_or_create(
                campeonato=brasileirao,
                rodada=rodada,
                time_casa=times_obj[casa],
                time_visitante=times_obj[visitante],
                defaults={
                    'data_hora': data_obj,
                    'encerrada': False
                }
            )
            if created:
                self.stdout.write(f'Jogo criado: {partida}')
        
        self.stdout.write(self.style.SUCCESS('Importação concluída!'))