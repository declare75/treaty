from django.apps import AppConfig

class Catalog2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog2'

    def ready(self):
        import catalog2.signals