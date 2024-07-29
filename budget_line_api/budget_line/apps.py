from django.apps import AppConfig


class BudgetLineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budget_line'

    # def ready(self):
    #     import budget_line.signals