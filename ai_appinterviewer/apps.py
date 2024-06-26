from django.apps import AppConfig


class AiAppinterviewerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_appinterviewer'

class InterviewConfig(AppConfig):
    name  = 'ai_appinterviewer'
    def ready(self):
        import ai_appinterviewer.signals   