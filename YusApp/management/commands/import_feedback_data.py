import csv
from django.core.management.base import BaseCommand
from YusApp.models import UserFeedback  # Import your model
from datetime import datetime

class Command(BaseCommand):
    help = 'Import user feedback data from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        
        # Open the CSV file
        with open('./data/user_feedback.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse the date and time into a datetime object
                timestamp_str = row['timestamp']
                timestamp = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M')
                
                # Create and save the UserFeedback object
                feedback = UserFeedback(
                    ticket_id=row['ticket_id'],
                    helpfulness_rating=int(row['helpfulness_rating']),
                    comment=row['comment'],
                    timestamp=timestamp,
                    knowledge_article_id=row['knowledge_article_id']
                )
                feedback.save()

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
