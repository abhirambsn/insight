from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_text
from .tokens import account_activation_token
from django.core.mail import send_mail, EmailMessage
from .models import Passport, Profile, Income, ExpiredPassport
import os

BASE_CONTEXT = {
    "appname": settings.APP_NAME
}

colorChoices = [
    ("bg", "Blue and Green"),
    ("bg2", "Blue and Violet"),
    ("bg3", "Pure Blue"),
    ("bg4", "Yellow and Violet"),
    ("bg5", "Red and Pink")
]

# Create your views here.
def register(request):
    if request.method == "POST":
        data = request.POST
        files = request.FILES
        # Please put these stmts in try/except
        try:
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
            income = int(data.get("income"))
            colorAccent = data.get("color_accent")
            newPassport = Passport(passport_holder_name=username, passport_access_token=password, passport_address=email)
            newPassport.save_password()
            newProfile = Profile(linked_passport=newPassport, first_name=first_name, last_name=last_name, color_accent=colorAccent, profile_picture=files['profile_picture'])
            newProfile.save()
            newIncome = Income(linked_passport=newPassport, money_left=income, income=income)
            newIncome.save()
            request.session['mtype'] = "success"
            request.session['message'] = "Registration Successful"
            request.session['passport'] = str(newPassport.passport_id)
            current_site = get_current_site(request)
            subject = 'Activate Your Insight Account'
            message = render_to_string('base/activation_email.html', {
                    'user': newPassport,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(str(newPassport.passport_id))),
                    'token': account_activation_token.make_token(newPassport),
                })
            emailMessage = EmailMessage(subject, message, 'elflord.computers@gmail.com', [email])
            emailMessage.send()
            return redirect('/payments/pricing/')
        except Exception as e:
            print(str(e))
    else:
        CTX = {
            'color_accent': colorChoices
        }
        CTX.update(BASE_CONTEXT)
        return render(request, os.path.join("passport", "register.html"), CTX)

def activate(request, uidb64, token, *args, **kwargs):
    passportID = force_text(urlsafe_base64_decode(uidb64))
    passport = Passport.objects.get(passport_id=passportID)
    if passport is not None and account_activation_token.check_token(passport, token):
        passport.passport_is_verified = True
        passport.save()
    return redirect('/passport/auth/login/')

def login(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        passport = Passport.objects.get(passport_holder_name=username)
        if passport is not None:
            credCheck = passport.verify_access_token(password)
            if credCheck:
                try:
                    expiryChk = ExpiredPassport.objects.get(passport=passport)
                    if expiryChk is not None:
                        request.session['passport'] = str(passport.passport_id)
                        request.session['renewal'] = True
                        return redirect('/payments/pricing/')
                except:
                    verified = passport.passport_is_verified
                    if not verified:
                        print(verified)
                        return redirect('/passport/auth/login/')
                profile = Profile.objects.get(linked_passport=passport)
                request.session['isAuthenticated'] = True
                request.session['renewal'] = False
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

def profile(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        passportID = request.session.get("passport")
        passport = Passport.objects.get(passport_id=passportID)
        profile = Profile.objects.get(linked_passport=passport)
        income = Income.objects.get(linked_passport=passport)
        ml = income.money_left
        income_ic = income.income
        status = ml / income_ic
        s_status  = 1 - status
        status_pct = s_status*100
        CTX = {
            'passport': passport,
            'profile': profile,
            'income': income,
            'status': s_status,
            'status_pct': status_pct,
            'color_accent': colorChoices
        }
        CTX.update(BASE_CONTEXT)
        return render(request, os.path.join("expense_manager", "profile.html"), CTX)
    else:
        return redirect('/passport/auth/login/')


def change_color_accent(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        if request.method == "POST":
            data = request.POST
            color_accent = data.get("color_accent")
            passportID = request.session.get("passport")
            passport = Passport.objects.get(passport_id=passportID)
            profile = Profile.objects.get(linked_passport=passport)
            profile.color_accent = color_accent
            profile.save()
            return redirect('/passport/profile/')
    else:
        return redirect('/passport/auth/login/')

def change_picture(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        if request.method == "POST":
            pic = request.FILES.get('profile_picture')
            profile = Profile.objects.get(linked_passport=Passport.objects.get(passport_id=request.session.get("passport")))
            profile.profile_picture = pic
            profile.save()
            return redirect('/passport/profile/')
    else:
        return redirect('/passport/auth/login/')

def settings(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        passportID = request.session.get("passport")
        passport = Passport.objects.get(passport_id=passportID)
        profile = Profile.objects.get(linked_passport=passport)
        income = Income.objects.get(linked_passport=passport)
        CTX = {
            'passport': passport,
            'profile': profile,
            'income': income
        }
        CTX.update(BASE_CONTEXT)
        return render(request, os.path.join("expense_manager", "settings.html"), CTX)
    else:
        return redirect('/passport/auth/login/')

def change_password(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        if request.method == "POST":
            data = request.POST
            oldPassword = data.get("old_password")
            passportID = request.session.get("passport")
            passport = Passport.objects.get(passport_id=passportID)
            check = passport.verify_access_token(oldPassword)
            if check:
                newPassword = data.get("password")
                reNewPassword = data.get("password2")
                if (newPassword == reNewPassword):
                    passport.passport_access_token = newPassword
                    passport.save()
                    return redirect('/passport/settings/')
                else:
                    return redirect('/passport/settings/')
            else:
                return redirect('/passport/settings/')
    else:
        return redirect('/passport/auth/login/')

def change_income(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        if request.method == "POST":
            data = request.POST
            passportID = request.session.get("passport")
            passport = Passport.objects.get(passport_id=passportID)
            income = Income.objects.get(linked_passport=passport)
            newIncome = int(data.get("newIncome"))
            income.income = newIncome
            income.save()
            return redirect('/passport/settings/')
    else:
        return redirect('/passport/auth/login/')

def logout(request):
    request.session.flush()
    return redirect('/passport/auth/login/')