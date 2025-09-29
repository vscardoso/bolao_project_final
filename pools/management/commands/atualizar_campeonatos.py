from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pools.models import Championship
from pools.services import get_api_service
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update championship data from external APIs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Update all championships, not just those that need updating',
        )
        parser.add_argument(
            '--championship',
            type=str,
            help='Slug of a specific championship to update',
        )
    
    def handle(self, *args, **options):
        if options['championship']:
            # Update specific championship
            try:
                championship = Championship.objects.get(slug=options['championship'])
                self.update_championship(championship)
            except Championship.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Championship '{options['championship']}' not found."))
            return
        
        # Filter championships that need updating
        championships = Championship.objects.filter(auto_update=True)
        
        if not options['all']:
            # Only championships that haven't been updated recently
            championships = championships.filter(
                last_update__lte=timezone.now() - timedelta(hours=24)
            )
        
        if not championships.exists():
            self.stdout.write("No championships to update.")
            return
            
        for championship in championships:
            self.update_championship(championship)
    
    def update_championship(self, championship):
        self.stdout.write(f"Updating championship: {championship.name}")
        
        service = get_api_service(championship)
        if not service:
            self.stdout.write(self.style.ERROR(
                f"API provider '{championship.api_provider}' not supported."
            ))
            return
            
        try:
            success = service.execute_update()
            if success:
                self.stdout.write(self.style.SUCCESS(
                    f"Championship '{championship.name}' updated successfully."
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"Error updating championship '{championship.name}'."
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Exception updating championship '{championship.name}': {str(e)}"
            ))