from datetime import datetime
from django.db import models

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

# from django.http import Http404
from rest_framework import serializers

# from django.core.exceptions import ValidationError
from budget_line_api.models import BaseUUIDModel
from django.core.validators import RegexValidator
from budget_line_api.constants import DIRECTIONS    
# Create your models here.

from django.db import transaction

from budget_line_api.utils import get_and_delete_last_uuid

class BudgetLine(BaseUUIDModel):
    
    name = models.CharField(max_length=30)
    line_amount = models.IntegerField(
        validators=[RegexValidator(regex=r'^\d+$', message='Seuls les chiffres sont autorisés.')],
        default=0
    )
    balance = models.IntegerField(
        validators=[RegexValidator(regex=r'^\d+$', message='Seuls les chiffres sont autorisés.')],
        default=0
    )
    rate_capital = models.CharField(max_length=18, default="0%")
    debt = models.CharField(max_length=10)
    loan = models.CharField(max_length=10)
    direction = models.CharField(choices=DIRECTIONS, max_length=30)
    description = models.CharField(max_length=50)
    year = models.IntegerField(default=datetime.now().year)


 
    def update_subline_rates(self):
        other_sublines = self.sublines.all()
        for subline in other_sublines:
            subline.rate_line = subline.calculate_rate_line
            subline.rate_capital = subline.calculate_rate_capital
            subline.save()
    
    # def update_subline_rates(self):
    #     sublines_to_save = []
    #     for subline in self.sublines.all():
    #         subline.rate_line = subline.calculate_rate_line
    #         subline.rate_capital = subline.calculate_rate_capital
    #         sublines_to_save.append(subline)

    #     for subline in sublines_to_save:
    #         subline.save()

    def save(self,*args, **kwargs):
        setter = self.rate_capital
        setter_int = str(setter)
        if '%' not in setter_int:
            # f"{self.rate_capital}%"
            calc = self.rate_capital * 100
            calc_int = float(calc)
            self.rate_capital = str(calc_int) + '%'
        
        self.name = self.name.upper()
        self.direction = self.direction.upper()
        self.description = self.description.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name 
    
    class Meta:
        ordering = ['name']

@transaction.atomic
@receiver(post_save, sender=BudgetLine)
def update_budget_amount_on_save(sender, instance, created, **kwargs):
    all_budget_lines = BudgetLine.objects.all()
    if created:
        sum_cap = 0
        for line in all_budget_lines:
            if type(float(line.rate_capital[:-1])) == float:
                sum_cap += float(line.rate_capital[:-1])
            elif type(int(line.rate_capital[:-1])) == int:
                sum_cap += int(line.rate_capital[:-1])
        # sum_rate_capital = sum(float(line.rate_capital[:-1]) for line in all_budget_lines)
        print(sum_cap)

        if sum_cap > 100:
            get_and_delete_last_uuid(BudgetLine)
            # raise ValidationError({'errors': "Le total des pourcentages ne doit pas exceder 100%"})
            raise serializers.ValidationError("Total de lignes budgetaires déjà ateind !")

    
# dette = dept;
# taux = rate;
# solde = balance;
# montant = line_amount;
# pret = loan;

# Étape 3 : Ajouter le symbole '%' au résultat
# resultat_multiplication = f"{multiplication} %"

# pourcentage_str = "10%"

# # Séparer la partie numérique et le symbole de pourcentage
# partie_numerique = pourcentage_str[:-1]  # Tout sauf le dernier caractère
# symbole_pourcentage = pourcentage_str[-1]  # Le dernier caractère
