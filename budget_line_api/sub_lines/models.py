from django.db import models
from django.db.models import F
from django.core.validators import RegexValidator
from django.dispatch import receiver
from budget_line.models import BudgetLine
from budget_line_api.models import BaseUUIDModel
from rest_framework.response import Response
from rest_framework import serializers
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save


class SubLines(BaseUUIDModel):

    # unique=True
    name = models.CharField(max_length=20)
    amount = models.IntegerField(default=0)
    rate_line = models.CharField(max_length=18, default="0%")
    rate_capital = models.CharField(max_length=18, default="0%")
    description = models.CharField(max_length=50)
    balance = models.IntegerField(
        validators=[RegexValidator(regex=r'^\d+$', message='Seuls les chiffres sont autorisés.')],
        default=0
    )
    id_budget_line = models.ForeignKey(BudgetLine, on_delete=models.PROTECT, related_name='sublines')

    def save(self, *args, **kwargs):
        if self.balance == 0:
            self.balance = self.amount
        
        self.name = self.name.upper().strip()
        self.description = self.description.upper().strip()
        super().save(*args, **kwargs)
    
    # def save(self, *args, **kwargs):
    #     if not SubLines.objects.filter(name=self.name.upper().strip()).exists():
    #         if self.balance == 0:
    #             self.balance = self.amount
            
    #         self.name = self.name.upper().strip()
    #         self.description = self.description.upper().strip()
    #         super().save(*args, **kwargs)
    #     else:
    #         return Response({f'Un enregistrement avec le nom {self.name} existe déjà. Enregistrement annulé.'})

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    
    @property
    def calculate_rate_line(self):
        if self.id_budget_line.line_amount > 0:
            return f"{(self.amount / self.id_budget_line.line_amount) * 100}%"
        else:
            return 0
    
    @property
    def calculate_rate_capital(self):
        int_rate_capital = 0
        if type(float(self.id_budget_line.rate_capital[:-1])) == float:
            int_rate_capital += float(self.id_budget_line.rate_capital[:-1])
        elif type(int(self.id_budget_line.rate_capital[:-1])) == int:
            int_rate_capital += int(self.id_budget_line.rate_capital[:-1])

        if self.id_budget_line.line_amount > 0 and int_rate_capital > 0:
            capital = (self.id_budget_line.line_amount / int_rate_capital) * 100
            return f"{(self.amount / capital) * 100}%"
        else:
            return 0
    
    

@receiver(post_save, sender=SubLines)
def update_budget_amount_on_save(sender, instance, created, **kwargs):
    budget_line = instance.id_budget_line
    if created:
        budget_line.line_amount = sum(sous_ligne.amount for sous_ligne in budget_line.sublines.all())
        budget_line.balance = sum(sous_ligne.balance for sous_ligne in budget_line.sublines.all())
        
        instance.rate_line = instance.calculate_rate_line
        instance.rate_capital = instance.calculate_rate_capital
        instance.save()

        budget_line.update_subline_rates()
        budget_line.save()
    # else:
    #     instance.rate_line = instance.calculate_rate_line
    #     instance.rate_capital = instance.calculate_rate_capital

    #     budget_line.update_subline_rates()
    #     budget_line.save()

    
    return print(f"L'instance {instance} de sublines a été mise à jour avec succès.")




@receiver(post_delete, sender=SubLines)
def update_parent_montant_on_delete(sender, instance, **kwargs):

    budget_line = instance.id_budget_line

    budget_line.balance = sum(sous_ligne.balance for sous_ligne in budget_line.sublines.all())

    budget_line.line_amount = sum(sous_ligne.amount for sous_ligne in budget_line.sublines.all())
    
    budget_line.update_subline_rates()

    budget_line.save()
