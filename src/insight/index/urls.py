from django.urls import path
from .views import home, contact_us

urlpatterns = [
    path('', home),
    path('contact_us/', contact_us)
]