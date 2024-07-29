from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from sub_lines.models import SubLines

@receiver(post_save, sender=SubLines)
def update_budgetLine_line_amount_on_save(sender, instance, **kwargs):
    instance.update_rate_capital_and_rate_line()
