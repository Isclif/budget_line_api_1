# budget_line/serializers.py

import requests
from rest_framework import serializers

from budget_line_api.constants import DIRECTION_END_POINT
from sub_lines.models import SubLines
from .models import BudgetLine

class SubLineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model  = SubLines
        fields = ['id','name', 'amount', 'balance', 'rate_line', 'rate_capital', 'description']

class CreateBudgetLineSerializer(serializers.ModelSerializer):

    # rate = serializers.CharField(required=True) 
    rate_capital = serializers.CharField(required=True)

    class Meta:
        model = BudgetLine
        fields = ['id', 'name', 'line_amount', 'balance', 'rate_capital', 'direction', 'description', 'year']

    def validate_direction(self, value):
        """ valide la direction sur l'url de création des lignes budgetaires """

        if BudgetLine.objects.filter(direction=value).exists():
            raise serializers.ValidationError("Cette direction à deja une ligne budgetaire.")
        
        return value

class UploadExcelSerializer(serializers.Serializer):

    excel_file = serializers.FileField(required=True)




class BudgetLineSerializer(serializers.ModelSerializer):
    id_departement = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = BudgetLine
        # fields = ['name', 'rate_capital', 'description', 'id_departement', 'direction']
        fields = ['id', 'name', 'line_amount', 'balance', 'rate_capital', 'direction', 'description', 'id_departement', 'year']
        read_only_fields = ['direction']
    
    def get_department_name(self, id_departement):
        if id_departement:
            url = f"{DIRECTION_END_POINT}/{id_departement}/"
            try:
                response = requests.get(url)
                response.raise_for_status()  # Vérifie les erreurs HTTP
                data = response.json()
                return data.get('name', '')  # Assurez-vous que la clé 'name' existe dans le JSON
            except requests.RequestException as e:
                raise serializers.ValidationError(f"Erreur lors de la requête HTTP : {e}")
            except ValueError as e:
                raise serializers.ValidationError(f"Erreur lors de la conversion du JSON : {e}")

    def create(self, validated_data):
        id_departement = validated_data.pop('id_departement')
        validated_data['direction'] = self.get_department_name(id_departement)
        
        return super().create(validated_data)



