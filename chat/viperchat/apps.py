from django.apps import AppConfig


class ViperchatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'viperchat'

    def ready(self):
        import viperchat.signals