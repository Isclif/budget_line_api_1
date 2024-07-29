from django.apps import AppConfig


class SubLinesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sub_lines'

    # def ready(self):
    #     import sub_lines.signals
