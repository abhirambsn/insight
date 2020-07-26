from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from passport.models import Subscription, Passport, Profile, ExpiredPassport
from .models import Payment
import stripe
import os
import json
import datetime
import uuid
from django.utils.timezone import timezone, timedelta, now

stripe.api_key = "sk_test_3pralRee6fRxOVB12RWEEtE2"

BASE_CONTEXT = {
    "appname": settings.APP_NAME
}

# Create your views here.

PRICINGS = {
    "monthly": 99,
    "annual": 999
}

def pricing_page(request):
    return render(request, os.path.join("payments", "pricing_page.html"), BASE_CONTEXT)

def checkout(request):
    data = request.POST
    plan = data.get("plan_type")
    request.session['plan'] = plan
    time_period = ""
    if plan == "monthly":
        time_period = " / month"
    else:
        time_period = " / year"
    return render(request, os.path.join("payments", "payment.html"), {'plan': plan, 'price': str(PRICINGS[plan])+ time_period})

@csrf_exempt
def process_payment(request):
    try:
        data = request.POST
        intent = stripe.PaymentIntent.create(
            amount=PRICINGS.get(request.session.get('plan'))*100,
            currency='inr'
        )
        return HttpResponse(json.dumps({
          'clientSecret': intent['client_secret']
        }))
    except Exception as e:
        print(str(e))
        return HttpResponse(json.dumps({'error': str(e)}), 403)

def success(request, payment_id):
    try:
        chkPayment = stripe.PaymentIntent.retrieve(payment_id)
    except Exception as e:
        return render(request, os.path.join("errors", "403.html"))

    plan = request.session.get('plan', None)
    isRenewal = request.session.get("renewal", False)
    if isRenewal:
        user = request.session.get("passport")
        passport = Passport.objects.get(passport_id=user)
        subscription = Subscription.objects.get(linked_passport=passport)
        validity = subscription.validity
        if plan == "monthly":
            validity += timedelta(days=30)
        else:
            validity += timedelta(days=365)
        subscription.validity = validity
        subscription.plan = plan
        subscription.save()
        expiredPassport = ExpiredPassport.objects.get(passport=passport)
        expiredPassport.delete()
    else:
        passportID = request.session.get("passport")
        passport = Passport.objects.get(passport_id=passportID)
        if plan == "monthly":
            validity = now() + timedelta(days=30)
        else:
            validity = now() + timedelta(days=365)
        newSubscription = Subscription(linked_passport=passport, plan=plan, validity=validity)
        newSubscription.save()
    payment = Payment(linked_passport=passport, payment_amount=PRICINGS[plan])
    payment.save()
    request.session.pop("passport", None)
    request.session.pop("renewal", None)
    request.session.pop("plan", None)
    request.session.pop("isAuthenticated", None)
    return render(request, os.path.join("payments", "success.html"))

def failed(request):
    
    return render(request, os.path.join("payments", "failed.html"))

def my_subscription(request):
    passport = Passport.objects.get(passport_id=uuid.UUID(request.session.get("passport")))
    subscription = Subscription.objects.get(linked_passport=passport)
    profile = Profile.objects.get(linked_passport=passport)
    if (subscription.validity - now()).days <= 3:
        isexp = True
    else:
        isexp = False
    CTX = {'subscription': subscription, 'days_left':(subscription.validity - now()).days, 'isexp': isexp, 'passport': passport, 'profile': profile}
    CTX.update(BASE_CONTEXT)
    return render(request, os.path.join("expense_manager", "mySubscription.html"), CTX)

def renew(request):
    request.session['renewal'] = True
    return redirect('/payments/pricing/')

def payment_history(request):
    passport = Passport.objects.get(passport_id=uuid.UUID(request.session.get("passport")))
    payments = Payment.objects.filter(linked_passport=passport)
    profile = Profile.objects.get(linked_passport=passport)
    CTX = {'payments': payments, 'passport': passport, 'profile': profile}
    CTX.update(BASE_CONTEXT)
    return render(request, os.path.join("expense_manager", "payment_history.html"), CTX)