from django.urls import path
from .views import register, login, logout, profile, activate, settings, change_color_accent, change_income, change_password, change_picture

urlpatterns = [
    path('auth/register/', register),
    path('auth/login/', login),
    path('auth/logout/', logout),
    path('profile/', profile),
    path('profile/change_picture/', change_picture),
    path('profile/change_color_accent/', change_color_accent),
    path('settings/', settings),
    path('settings/change_income/', change_income),
    path('settings/change_password/', change_password),
    path('activate/<uidb64>/<token>/', activate, name='activate')
]