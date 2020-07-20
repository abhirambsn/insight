from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid, os
# Create your models here.

colorChoices = [
    ("Blue", "blue"),
    ("Green", "green"),
    ("Pink", "pink"),
    ("Red", "red")
]

planChoices = [
    ("Monthly", "monthly"),
    ("Annual", "annual"),
    ("Trial", "trial")
]


class Passport(models.Model):
    passport_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    passport_holder_name = models.CharField(max_length=45, null=False, blank=False)
    passport_access_token = models.CharField(max_length=655, null=False, blank=False)
    passport_address = models.CharField(max_length=70, null=False, blank=False)
    passport_created_on = models.DateTimeField(auto_now_add=True)
    passport_updated_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.passport_access_token = make_password(self.passport_access_token)
        super(Passport, self).save(*args, **kwargs)
    
    def verify_access_token(self, password):
        return check_password(password, self.passport_access_token)

def get_upload_path(instance, filename):
    return os.path.join(str(instance.profile_id) + "_" + filename)

class Profile(models.Model):
    linked_passport = models.OneToOneField(Passport, on_delete=models.CASCADE)
    profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=60, null=False, blank=False)
    last_name = models.CharField(max_length=60, null=False, blank=False)
    color_accent = models.CharField(max_length=10, null=False, blank=False, default="blue", choices=colorChoices)
    plan = models.CharField(max_length=15, null=False, blank=False, choices=planChoices)
    isTrial = models.BooleanField(blank=False, null=False)
    validity = models.IntegerField(blank=False, null=False)
    profile_picture = models.FileField(upload_to=get_upload_path, null=False, blank=False)

def get_def_money_left(instance):
    return instance.income

class Income(models.Model):
    linked_passport = models.OneToOneField(Passport, on_delete=models.CASCADE, primary_key=True)
    income = models.IntegerField(null=False, blank=False, default=0)
    money_left = models.IntegerField(null=False, blank=False, default=get_def_money_left)