from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from passport.models import Passport, Profile, Income
from .models import Expense, RecurringExpense
from django.conf import settings
import os, uuid, datetime, calendar, xlwt
# Create your views here.

BASE_CONTEXT = {
    "appname": settings.APP_NAME
}

def dashboard(request):
    if request.session.get("isAuthenticated", None):
        passportID = request.session.get("passport")
        try:
            passport = Passport.objects.get(passport_id=uuid.UUID(passportID))
            profile = Profile.objects.get(linked_passport=passport)
            income = Income.objects.get(linked_passport=passport)
        except Exception as e:
            print(e)
            request.session.pop("passport", None)
            request.session.pop("isAuthenticated", None)
            return redirect('/passport/auth/login/')
        if passport is not None and profile is not None:
            CTX = {"profile": profile, "passport": passport, 'income': income}
            CTX.update(BASE_CONTEXT)
            return render(request, os.path.join("expense_manager", "dashboard.html"), CTX)
        else:
            return redirect('/passport/auth/login/')
    else:
        return redirect('/passport/auth/login/')

def add(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        passportID = request.session.get("passport")
        passport = Passport.objects.get(passport_id=passportID)
        profile = Profile.objects.get(linked_passport=passport)
        if request.method == "POST":
            data = request.POST
            income = Income.objects.get(linked_passport=passport)
            money_left = income.money_left
            expense_type = data.get("expense_type")
            expense_cost = data.get("expense_cost")
            money_left -= int(expense_cost)
            if (money_left <= 0):
                savings = income.savings
                savings -= int(expense_cost)
                if (savings <= 0):
                    return redirect('/expense_manager/dashboard/')
                expense_name = data.get("expense_name")
                newExpense = Expense(expense_name=expense_name, expense_type=expense_type, expense_cost=expense_cost)
                newExpense.save()
                newExpense.linked_passport.set([passport])
                if expense_type == "M":
                    recExpense = RecurringExpense(expense=newExpense, date=newExpense.expense_created_on)
                    recExpense.save()
                income.savings = savings
                income.save()
                print("Expense Added {}".format(newExpense.expense_id))
                return redirect('/expense_manager/dashboard/')
            else:
                expense_name = data.get("expense_name")
                newExpense = Expense(linked_passport=passport, expense_name=expense_name, expense_type=expense_type, expense_cost=expense_cost)
                newExpense.save()
                if expense_type == "M":
                    recExpense = RecurringExpense(expense=newExpense, date=newExpense.expense_created_on)
                    recExpense.save()
                income.money_left = int(money_left)
                income.save()
                print("Expense Added {}".format(newExpense.expense_id))
                return redirect('/expense_manager/dashboard/')
        else:
            CTX = {
                'passport': passport,
                'profile': profile
            }
            CTX.update(BASE_CONTEXT)
            return render(request, os.path.join("expense_manager", "addExpense.html"), CTX)
    else:
        return redirect('/passport/auth/login/')

def all(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        passportID = request.session.get("passport")
        passport = Passport.objects.get(passport_id=passportID)
        profile = Profile.objects.get(linked_passport=passport)
        expenses = Expense.objects.filter(linked_passport=passport)
        CTX = {"expenses": expenses[::-1], 'passport': passport, 'profile': profile}
        CTX.update(BASE_CONTEXT)
        return render(request, os.path.join("expense_manager", "allExpenses.html"), CTX)
    else:
        return redirect('/passport/auth/login')

def get_expense(request, expense_id):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        passport = Passport.objects.get(passport_id=request.session.get("passport")) 
        expense = Expense.objects.get(linked_passport=passport, expense_id=expense_id)
        if expense is not None:
            profile = Profile.objects.get(linked_passport=passport)
            CTX = {"expense": expense, 'passport': passport, 'profile': profile}
            CTX.update(BASE_CONTEXT)
            return render(request, os.path.join("expense_manager", "viewExpense.html"), CTX)
        else:
            return redirect('/expense_manager/dashboard')
    else:
        return redirect('/passport/auth/login')

def email_report(request):
    if request.session.get("isAuthenticated", None) and request.session.get("passport", None):
        passportID = request.session.get("passport") 
        passport = Passport.objects.get(passport_id=passportID)
        profile = Profile.objects.get(linked_passport=passport)
        if request.method == "POST":
            data = request.POST
            year = int(data.get("year"))
            month = int(data.get("month"))
            expenses = Expense.objects.filter(linked_passport=passport).filter(expense_created_on__year=year, expense_created_on__month=month).values_list('expense_id', 'expense_name', 'expense_cost', 'expense_created_on')
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ["Expense ID", "Expense Name", "Expense Cost", "Date"]
            for col in range(len(columns)):
                ws.write(row, col, columns[col], font_style)
            font_style = xlwt.XFStyle()
            for expense in expenses:
                row += 1
                for col in range(len(expense)):
                    ws.write(row, col, str(expense[col]), font_style)
            if data.get("ed") == "email":
                wb.save(os.path.join(settings.BASE_DIR, "media", "report_"+str(passportID)+".xls"))
                emails = data.get("emails").split(",")
                message = EmailMessage(
                    "Monthly Expense Report for Month {}".format(calendar.month_name[month]),
                    "PFA the Expense Report of {} for the month of {}".format(profile.first_name, calendar.month_name[month]),
                    'elflord.computers@gmail.com',
                    emails,
                    reply_to=["elflord.computers@gmail.com"]
                )
                message.attach_file(os.path.join(settings.BASE_DIR, "media", "report_"+str(passportID)+".xls"))
                message.send(fail_silently=True)
                return redirect('/expense_manager/dashboard')
            elif data.get("ed") == "download":
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.join(settings.BASE_DIR, "media", "report_"+str(passportID)+".xls"))
                wb.save(response)
                return response
        else:
            passportID = request.session.get("passport")
            passport = Passport.objects.get(passport_id=passportID)
            profile = Profile.objects.get(linked_passport=passport)
            expenses = Expense.objects.all().values('expense_created_on').distinct()
            years = [expense['expense_created_on'].year for expense in expenses]
            months = [(i, calendar.month_name[i]) for i in range(1, 13)]
            CTX = {"passport": passport, "profile": profile, "years": years, "months": months}
            CTX.update(BASE_CONTEXT)
            return render(request, os.path.join("expense_manager", "email_download_reports.html"), CTX)
    else:
        return redirect('/passport/auth/login')

