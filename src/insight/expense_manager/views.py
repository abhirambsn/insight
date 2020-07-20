from django.shortcuts import render, redirect
from passport.models import Passport, Profile, Income
from django.conf import settings
import os, uuid
# Create your views here.

BASE_CONTEXT = {
    "appname": settings.APP_NAME
}

def dashboard(request):
    if request.session.get("isAuthenticated", None):
        passportID = request.session.get("passport")
        print(passportID)
        try:
            passport = Passport.objects.get(passport_id=uuid.UUID(passportID))
            profile = Profile.objects.get(linked_passport=passport)
        except Exception as e:
            print(e)
            request.session.pop("passport", None)
            request.session.pop("isAuthenticated", None)
            return redirect('/passport/auth/login/')
        if passport is not None and profile is not None:
            BASE_CONTEXT['profile'] = profile
            BASE_CONTEXT['passport'] = passport
            return render(request, os.path.join("expense_manager", "dashboard.html"), BASE_CONTEXT)
        else:
            return redirect('/passport/auth/login/')
    else:
        return redirect('/passport/auth/login/')

def add(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        if request.method == "POST":
            pass
        else:
            return render(request, os.path.join("expense_manager", "addExpense.html"), BASE_CONTEXT)
    else:
        return redirect('/passport/auth/login/')