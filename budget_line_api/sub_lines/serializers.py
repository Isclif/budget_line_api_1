# sub_lines/serializers.py

from rest_framework import serializers
from .models import BudgetLine
from .models import SubLines

class BudgetLineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model  = BudgetLine
        fields = ['id','direction','name', 'line_amount', 'balance', 'description']

class CreateReadDeleteSubLineSerializer(serializers.ModelSerializer):

    budget_line = serializers.SerializerMethodField(read_only=True)
    id_budget_line = serializers.CharField(write_only=True)
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = SubLines
        fields = ['id','name','amount','rate_line','rate_capital','description','budget_line','id_budget_line', 'balance']
    
    def get_budget_line(self, instance):
        return {
            "id": instance.id_budget_line.id,
            "name": instance.id_budget_line.name,
            "direction": instance.id_budget_line.direction,
            "line_amount": instance.id_budget_line.line_amount,
            "balance": instance.id_budget_line.balance,
            "year": instance.id_budget_line.year,
            "description": instance.id_budget_line.description,
        }
    
    def validate_name(self, value):
        """Valide le nom de la sous-ligne."""
        if SubLines.objects.filter(name=value.upper().strip()).exists():
            print(f"Validation du nom: {value}")
            raise serializers.ValidationError("Cette sous-ligne existe déjà.")
        return value
    
    def create(self, validated_data):
        id_budget_line = BudgetLine.readByToken(token=validated_data.pop('id_budget_line', None))

        subligne = SubLines.objects.create(**validated_data, id_budget_line=id_budget_line)

        return subligne


class UpdateSubLineAmountSerializer(serializers.Serializer):
    id = serializers.CharField()
    # amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount = serializers.IntegerField()

class UpdateSubLineSerializer(serializers.ModelSerializer):
    budget_line = BudgetLineSerializer()

    class Meta:
        model = SubLines
        fields = ['id','name','amount','rate_line','rate_capital','description','budget_line']



