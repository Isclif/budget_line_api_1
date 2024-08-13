from django.shortcuts import render

# Create your views here.

# sub_lines/views.py

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView

from budget_line.models import BudgetLine
from .models import SubLines
from rest_framework.decorators import action
from .serializers import CreateReadDeleteSubLineSerializer, UpdateSubLineAmountSerializer, UpdateSubLineSerializer

class SubLinesViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        """ Définit le serializer utilisé en fonction de l'action demandée """
        if self.action == 'create':
            return CreateReadDeleteSubLineSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateSubLineSerializer
        return super().get_serializer_class()
        

    queryset = SubLines.objects.all()
    
    serializer_class = CreateReadDeleteSubLineSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        remaining_instances = SubLines.objects.all()
        serializer = CreateReadDeleteSubLineSerializer(remaining_instances, many=True)
        return Response({"message": "Données supprimées", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({"message": "Données mises à jour", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    

    @action(detail=True, methods=['put'])
    def put(self, request, *args, **kwargs):
        """ Gère les requêtes PUT pour la mise à jour des données """
        # BudgetLine.update_subline_rates()
        # raise print("things went wrong !!")
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def patch(self, request, *args, **kwargs):
        """ Gère les requêtes PATCH pour la mise à jour partielle des données """
        return self.partial_update(request, *args, **kwargs)



class UpdateExpenseView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UpdateSubLineAmountSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            amount = serializer.validated_data['amount']
            
            try:
                sublines_to_update = SubLines.objects.get(id=id)
                if (sublines_to_update.balance >= amount):

                    budget_line = sublines_to_update.id_budget_line
                    budget_line.balance -= amount
                    budget_line.save()
                    
                    sublines_to_update.balance -= amount
                    sublines_to_update.save()

                else:
                    return Response({"error": "The amount of the expense must not exceed the amount of the sub-line or this subline has exceeded its amount to be spent."}, status=status.HTTP_200_OK)
                    # return Response({"error": "The amount of the expense must not exceed the amount of the sub-line or this subline has exceeded its amount to be spent."}, status=status.HTTP_400_BAD_REQUEST)
                
                remaning_instances = SubLines.objects.all()
                serializer = CreateReadDeleteSubLineSerializer(remaning_instances, many=True)
                return Response({"success": "Expense and budget line updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
            
            except SubLines.DoesNotExist:
                return Response({"error": "Subline not found."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateBalanceSubline(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UpdateSubLineAmountSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            amount = serializer.validated_data['amount']
            
            try:
                sublines_to_update = SubLines.objects.get(id=id)
                if (sublines_to_update.amount == amount):
                    budget_line = sublines_to_update.id_budget_line
                    budget_line.balance += amount
                    budget_line.save()

                    sublines_to_update.balance += amount
                    sublines_to_update.save()
                else:
                    return Response({"Error": "The sended amount must be equal to subline amount."}, status=status.HTTP_400_BAD_REQUEST)
                
                remaning_instances = SubLines.objects.all()
                serializer = CreateReadDeleteSubLineSerializer(remaning_instances, many=True)
                return Response({"success": "Balance and budget line updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
            
            except SubLines.DoesNotExist:
                return Response({"error": "Subline not found."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
