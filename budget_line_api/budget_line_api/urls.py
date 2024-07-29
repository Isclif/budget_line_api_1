from django.urls import include, path

from budget_line_api.router import OptionalSlashRouter
from budget_line import views as bviews
from sub_lines import views as sviews

router = OptionalSlashRouter()
router.register(r'budget_line', bviews.LigneViewSet, basename="budget_line")
router.register(r'sub_lines', sviews.SubLinesViewSet, basename="sub_lines")

urlpatterns = [
    path('', include(router.urls)),
    path('upload-excel/', bviews.UploadExcelViewSet.as_view(), name='upload-excel'),
    path('export-sub-line-excel/', bviews.ExportSublinesLines.as_view(), name='export-sub-line-excel'),
    path('export-budget-line-excel/', bviews.ExportBudgetLines.as_view(), name='export-budget-excel'),
    path('update-expense/', sviews.UpdateExpenseView.as_view(), name='update-expense'),
    path('update-balance/', sviews.UpdateBalanceSubline.as_view(), name='update-balance'),
    path('get_all_sublines/<uuid:parent_id>', bviews.GetAllSublines.as_view(), name='get-all-sublines'),
]

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
