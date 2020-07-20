from django.db import models
from passport.models import Passport
import uuid, os
# Create your models here.

class Expense(models.Model):
    linked_passport = models.OneToOneField(Passport, on_delete=models.CASCADE)
    expense_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    expense_name = models.CharField(max_length=40, null=False, blank=False)
    expense_cost = models.IntegerField(null=False, blank=False)
    expense_created_on = models.DateTimeField(auto_now_add=True)
