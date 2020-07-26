"""insight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include("index.urls")),
    path('insight/expense/manager/admin/', admin.site.urls),
    path("passport/", include("passport.urls")),
    path('expense_manager/', include("expense_manager.urls")),
    path('payments/', include("payments.urls")),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
]

handler404 = 'index.views.handler404'
handler500 = 'index.views.handler500'
handler503 = 'index.views.handler503'

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)