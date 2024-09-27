from django.db import models
from django.utils import timezone
import random
import string

class KBA(models.Model):
    knowledge_article_id = models.CharField(max_length=10)
    description = models.TextField()
    module = models.TextField()
    keywords = models.TextField()
    category_1 = models.TextField()
    category_2 = models.TextField()
    category_3 = models.TextField()
    issue = models.TextField()
    resolution = models.TextField()

class ITSM_Ticket(models.Model):
    ticket_id = models.CharField(max_length=10)
    description = models.TextField()
    priority = models.TextField()
    status = models.TextField()
    created_on = models.DateTimeField()
    message_processor = models.TextField()
    support_team_id = models.IntegerField()
    support_team = models.TextField()
    category_1 = models.TextField()
    category_2 = models.TextField()
    category_3 = models.TextField()
    ministry = models.TextField()
    control_officer = models.TextField()
    code_ptj = models.CharField(max_length=8)
    last_changed_on = models.DateTimeField()
    type_of_complain = models.TextField()

class Complaint(models.Model):
    user = models.CharField(max_length=255)
    type_of_complain = models.CharField(max_length=255)
    description = models.TextField()
    date_logged = models.DateTimeField(auto_now_add=True)

def generate_ticket_id():
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return timezone.now().strftime("%Y%m%d") + random_str

class UserFeedback(models.Model):
    ticket_id = models.CharField(max_length=14) 
    helpfulness_rating = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    knowledge_article_id = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Feedback {self.ticket_id} - {self.helpfulness_rating} Stars at {self.timestamp}"
    
#========================================================================
# ===========================ADMIN============================================

class Employee(models.Model):
    pass


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)  # Added password field

    def __str__(self):
        return f"{self.first_name} {self.last_name}"