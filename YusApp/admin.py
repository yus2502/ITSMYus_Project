from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Complaint  # Replace with your model
from .models import UserFeedback
from .models import ITSM_Ticket, KBA  # Correct the import

# Create or get the 'Administrators' group
admin_group, created = Group.objects.get_or_create(name='Administrators')

# Assign all permissions related to the Complaint model to this group
content_type = ContentType.objects.get_for_model(Complaint)
permissions = Permission.objects.filter(content_type=content_type)

admin_group.permissions.set(permissions)

# Register the Complaint model with the admin site
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_of_complain', 'description', 'date_logged')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(ITSM_Ticket)
admin.site.register(KBA)
admin.site.register(UserFeedback)

