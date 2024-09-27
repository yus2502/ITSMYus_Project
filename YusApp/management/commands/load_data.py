 # myapp/management/commands/load_data.py

import csv
from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from YusApp.models import ITSM_Ticket, KBA

class Command(BaseCommand):
    help = 'Load data from CSV files into the database'

    def handle(self, *args, **kwargs):
        # Load ITSM_Tickets.csv
        with open('./data/ITSM_Tickets.csv', 'r', encoding='utf-8') as file:  # Specify encoding
            reader = csv.DictReader(file)
            for row in reader:
                # Convert 'created_on' to the correct format if necessary
                if 'created_on' in row and row['created_on']:
                    try:
                        # Convert from DD.MM.YYYY to YYYY-MM-DD and make it timezone-aware
                        naive_created_on = datetime.strptime(row['created_on'], '%d.%m.%Y')
                        row['created_on'] = timezone.make_aware(naive_created_on, timezone.get_current_timezone())
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f"Date format error in 'created_on' for row {row}: {e}"))
                        continue  # Skip rows with invalid date formats

                # Convert 'last_changed_on' to the correct format if necessary
                if 'last_changed_on' in row and row['last_changed_on']:
                    try:
                        # Convert from DD.MM.YYYY to YYYY-MM-DD and make it timezone-aware
                        naive_last_changed_on = datetime.strptime(row['last_changed_on'], '%d.%m.%Y')
                        row['last_changed_on'] = timezone.make_aware(naive_last_changed_on, timezone.get_current_timezone())
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f"Date format error in 'last_changed_on' for row {row}: {e}"))
                        continue  # Skip rows with invalid date formats
                
                # Create ITSMTicket object
                ITSM_Ticket.objects.create(**row)

        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))

         # Load KBA.csv (if necessary)
        with open('./data/KBA.csv', 'r', encoding='ISO-8859-1') as file:  # Apply 'ISO-8859-1' encoding here too
            reader = csv.DictReader(file)
            for row in reader:
                # Assume we are processing KBA fields here, adjust as necessary
                KBA.objects.create(**row)

        self.stdout.write(self.style.SUCCESS('KBA data loaded successfully'))



