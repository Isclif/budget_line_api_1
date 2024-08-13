from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from sub_lines.models import SubLines
# from django.db import transaction

@receiver(post_save, sender=SubLines)
# @transaction.atomic
def update_budgetLine_line_amount_on_save(sender, instance, **kwargs):
    budget_line_to_update = instance.id_budget_line
    budget_line_to_update.update_line_amount_and_balance()
    budget_line_to_update.update_capital()
    for sub_lines in budget_line_to_update.sublines.all():
        sub_lines.update_rate_capital_and_rate_line()