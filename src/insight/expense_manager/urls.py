from django.urls import path
from .views import dashboard, add, all, get_expense, email_report
urlpatterns = [
    path('dashboard/', dashboard),
    path('add/', add),
    path('all/', all),
    path('expense/<uuid:expense_id>/', get_expense),
    path('report/', email_report),
]