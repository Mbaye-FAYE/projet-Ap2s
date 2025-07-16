from django.apps import AppConfig

class FacturationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestiondesfactures.facturations'

    def ready(self):
        import facturations.signals
