from django.contrib import admin
from .models import Passport, Profile, Income, Subscription, ExpiredPassport

# Register your models here.
admin.site.register(Passport)
admin.site.register(Profile)
admin.site.register(Income)
admin.site.register(Subscription)
admin.site.register(ExpiredPassport)