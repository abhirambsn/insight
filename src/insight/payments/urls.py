from django.urls import path
from .views import pricing_page, checkout, process_payment, renew, my_subscription, success, failed, payment_history

urlpatterns = [
    path("pricing/", pricing_page),
    path("checkout/", checkout),
    path('process_payment/', process_payment),
    path('success/<str:payment_id>/', success),
    path('failed/', failed),
    path('my_subscription/', my_subscription),
    path('renew/', renew),
    path('history/', payment_history)
]