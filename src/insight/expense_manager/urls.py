from django.urls import path
from .views import dashboard, add
urlpatterns = [
    path('dashboard/', dashboard),
    path('add/', add)
]