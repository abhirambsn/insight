from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from passport.models import Passport
import random
import datetime
import os
# Create your views here.

BASE_CONTEXT = {
    "appname": settings.APP_NAME
}

def home(request):
    return render(request, os.path.join("index", "home.html"), BASE_CONTEXT)

def contact_us(request):
    if request.method == "POST":
        user = None
        email = None
        data = request.POST
        if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
            passport = Passport.objects.get(passport_id=request.session.get("passport"))
            user = passport.passport_holder_name
            email = passport.passport_address
        else:
            user = data.get("name")
            email = data.get("email")
        content = render_to_string(os.path.join("base", "contact_us_email.html"), {
            "content": data.get("message"),
            "username": user,
            'date': datetime.datetime.now(),
            'replyto': email,
            'title': data.get("title")
        })
        subject = "Query No: " + str(random.randint(1, 99999999)) + " - " + data.get("title")
        message = EmailMessage(subject, content, "elflord.computers@gmail.com", ["elflord.computers@gmail.com"], reply_to=[email, "elflord.computers@gmail.com"])
        message.send()
        if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
            return redirect('/expense_manager/dashboard/')
        else:
            return redirect('/')

def handler404(request, exception):
    return render(request, os.path.join("errors", "404.html"), status=404)

def handler500(request):
    return render(request, os.path.join("errors", "500.html"), status=500)

def handler503(request):
    return render(request, os.path.join("errors", "maintenance.html"), status=503)