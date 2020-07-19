from django.shortcuts import render, redirect
from django.conf import settings
from .models import Passport, Profile
import os

BASE_CONTEXT = {
    "appname": settings.APP_NAME
}

# Create your views here.
def register(request):
    if request.method == "POST":
        data = request.POST
        # Please put these stmts in try/except
        username = data.get("username")
        password = data.get("password")
        password2 = data.get("password2")
        if (not (password == password2) and not len(password) > 6):
            request.session['mtype'] = "error"
            request.session['message'] = "Password Mismatch or Length is less than 6 characters."
            return redirect('/passport/auth/register')
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        plan = data.get("plan")
        color_accent = data.get("color_accent")
        validity = 0
        isTrial = False
        if (plan == "trial"):
            isTrial = True
            validity = 30
        elif (plan == "monthly"):
            validity = 30
        elif (plan == "annual"):
            validity = 365
        newPassport = Passport(passport_holder_name=username, passport_access_token=password, passport_address=email)
        newPassport.save()
        newProfile = Profile(linked_passport=newPassport, first_name=first_name, last_name=last_name, color_accent=color_accent, plan=plan, isTrial=isTrial, validity=validity)
        newProfile.save()
        request.session['mtype'] = "success"
        request.session['message'] = "Registration Successful"
        return redirect('/passport/auth/login')
    else:
        return render(request, os.path.join("passport", "register.html"), BASE_CONTEXT)

def login(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        passport = Passport.objects.get(passport_holder_name=username)
        if passport is not None:
            credCheck = passport.verify_access_token(password)
            if credCheck:
                profile = Profile.objects.get(linked_passport=passport)
                request.session['isAuthenticated'] = True
                print(passport.passport_id)
                request.session['passport'] = str(passport.passport_id)
                return redirect('/expense_manager/dashboard/')
            BASE_CONTEXT['errors'] = {'msg': "Wrong Password"}
            return render(request, os.path.join("passport", "login.html"), BASE_CONTEXT)
        BASE_CONTEXT['errors'] = {'msg': "Invalid User"}
        return render(request, os.path.join("passport", "login.html"), BASE_CONTEXT)
    else:
        if request.session.get('isAuthenticated', None) and request.session.get("passport", None):
            return redirect('/expense_manager/dashboard/')
        return render(request, os.path.join("passport", "login.html"), BASE_CONTEXT)

def logout(request):
    request.session.pop('isAuthenticated', None)
    request.session.pop('passport', None)
    return redirect('/passport/auth/login/')