from apscheduler.schedulers.background import BackgroundScheduler
from insight.passport.models import Subscription, Income, Passport, ExpiredPassport
from insight.expense_manager.models import RecurringExpense, Expense
import datetime

sched = BackgroundScheduler()

@sched.interval_schedule(days=1)
def check_recurring():
    r_expenses = RecurringExpense.objects.all()
    for r_expense in r_expenses:
        if r_expense.date == datetime.datetime.now():
            expense = r_expense.expense
            nExpense = Expense(expense_name=expense.expense_name, expense_cost=expense.expense_cost, expense_type=expense.expense_type, expense_created_on=datetime.datetime.now())
            nExpense.save()
            recExpense = RecurringExpense(expense=nExpense, date=datetime.datetime.now() + datetime.timedelta(days=30))
            recExpense.save()
            income = Income.objects.get(linked_passport=expense.linked_passport.passport_id)
            money_left = income.money_left
            money_left -= recExpense.expense.expense_cost
            income.money_left = money_left
            income.save()
            r_expense.delete()
@sched.interval_schedule(days=1)
def check_validity():
    all_users = Passport.objects.all()
    for user in all_users:
        subscription_data = Subscription.objects.get(linked_passport=user)
        if subscription_data.validity == datetime.datetime.now():
            expired = ExpiredPassport(passport=user)
            expired.save()

@sched.interval_schedule(months=1)
def reset_money_left():
    incomes = Income.objects.all()
    for income in incomes:
        if (income.money_left > 0):
            savings = income.savings
            savings += income.money_left
            income.savings = savings
        income.money_left = income.income
        income.save()

sched.start()