from django.apps import AppConfig

class YusAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'YusApp'

    # Avoid database queries here
    def ready(self):
        pass  # Do not perform DB operations here