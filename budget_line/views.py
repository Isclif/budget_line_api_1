import uuid
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework import serializers

from sub_lines.models import SubLines
from .models import BudgetLine
from .serializers import CreateBudgetLineSerializer, SubLineSerializer, UploadExcelSerializer, BudgetLineSerializer
from rest_framework.views import APIView

# import for upload excel_file
from openpyxl import Workbook
import pandas as pd

class LigneViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        """ Définit le serializer utilisé en fonction de l'action demandée """
        if self.action == 'create':
            return CreateBudgetLineSerializer
        
        return super().get_serializer_class()
        

    queryset = BudgetLine.objects.all()
    
    serializer_class = CreateBudgetLineSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        remaining_instances = BudgetLine.objects.all()
        serializer = CreateBudgetLineSerializer(remaining_instances, many=True)
        return Response({"message": "données supprimées", "data": serializer.data}, status=status.HTTP_200_OK)

class UploadExcelViewSet(APIView):

    def post(self, request, *args, **kwargs):
        serialiser = UploadExcelSerializer(data=request.data)
        if serialiser.is_valid():
            file = serialiser.validated_data['excel_file']
            xls = pd.ExcelFile(file)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                self.proceed_data_frame(df)
            get_all_datas1 = BudgetLine.objects.all()
            serializer1 = CreateBudgetLineSerializer(get_all_datas1, many=True)

            get_all_datas2 = SubLines.objects.all()
            serializer2 = SubLineSerializer(get_all_datas2, many=True)

            return Response({"success": "Data processed and saved successfully", "Budget Lines": serializer1.data, "Sublines": serializer2.data}, status=status.HTTP_200_OK)
            # try:
                # xls = pd.ExcelFile(file)
                # for sheet_name in xls.sheet_names:
                #     df = pd.read_excel(xls, sheet_name=sheet_name)
                #     self.proceed_data_frame(df)
                # get_all_datas = BudgetLine.objects.all()
                # serializer = CreateBudgetLineSerializer(get_all_datas, many=True)
                # return Response({"success": "Data processed and saved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            # except Exception as e:
            #     return Response({"error": str(e)}, status.HTTP_400_BAD_REQUEST)
        return Response(serialiser.errors, status.HTTP_400_BAD_REQUEST)


    def proceed_data_frame(self, df):
        for index, row in df.iterrows():
            if 'id_budget_line' not in df.columns and 'amount' not in df.columns:
                if not BudgetLine.objects.filter(direction=row['direction'].upper().strip()):
                    budget_line = BudgetLine(
                        name=row['name'],
                        rate_capital=row['rate_capital'],
                        direction=row['direction'],
                        description=row['description']
                    )
                    budget_line.save()
                else:
                    raise serializers.ValidationError("The budget Line direction already exist !!!")
            elif 'id_budget_line' in df.columns and 'amount' in df.columns:
                budget_line = BudgetLine.objects.get(id=row['id_budget_line'])
                if not SubLines.objects.filter(name=row['name'].upper().strip()):
                    sub_line = SubLines(
                        amount=int(row['amount']),
                        description=row['description'],
                        name=row['name'],
                        id_budget_line=budget_line
                    )
                    sub_line.save()
                else:
                    raise serializers.ValidationError("the subline name passed already exist !")
    
    def convert_to_int(self, value):
        try:
            return int(float(value))
        except ValueError:
            raise Exception(f"Cannot convert value to int: {value}")


class GetAllSublines(APIView):
    def get(self, request, parent_id, *args, **kwargs):
        try:
            parent_id = parent_id
            parent_line = BudgetLine.objects.get(id=parent_id)
            sub_lines = parent_line.sublines.all()
            serializer = SubLineSerializer(sub_lines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BudgetLine.DoesNotExist:
            return Response({"error": "Parent line not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)


class ExportBudgetLines(APIView):

    def get(self, request, *args, **kwargs):
        wb = Workbook()
        ws = wb.active
        ws.title = "Lignes Budgetaires"

        # Ajouter des en-têtes
        headers = ['name', 'rate_capital', 'direction', 'description']  # Remplacez par les champs de votre modèle
        ws.append(headers)

        # Ajouter les données
        for item in BudgetLine.objects.all():
            ws.append([item.name, item.rate_capital, item.direction, item.description])
        
        # Créer la réponse HTTP
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="LignesBudgetaire.xlsx"'
        
        # Sauvegarder le classeur dans la réponse
        wb.save(response)

        return response
    

class ExportSublinesLines(APIView):

    def get(self, request, *args, **kwargs):
        wb = Workbook()
        ws = wb.active
        ws.title = "Sous Lignes"

        # Ajouter des en-têtes
        headers = ['name', 'rate_capital', 'description', 'id_budget_line']  # Remplacez par les champs de votre modèle
        ws.append(headers)

        # Ajouter les données
        for item in SubLines.objects.all():
            ws.append([item.name, item.rate_capital, item.description, str(item.id_budget_line.id)])
        
        # Créer la réponse HTTP
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="SousLignes.xlsx"'
        
        # Sauvegarder le classeur dans la réponse
        wb.save(response)

        return response



