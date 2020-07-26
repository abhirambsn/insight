from django.db import models
from passport.models import Passport
import uuid
# Create your models here.
class Payment(models.Model):
    payment_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    linked_passport = models.ForeignKey(Passport, default=None, on_delete=models.CASCADE)
    payment_amount = models.IntegerField(null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)