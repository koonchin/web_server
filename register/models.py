from django.db import models
from django.contrib.auth.models import User

# Create your models here.
ROLE = (
    ('stock', 'STOCK'),
    ('admin','ADMIN'),
)

DEPARTMENT = (
    ('muslin','MUSLIN'),
    ('maruay','MARUAY'),
)
class Employee(models.Model):
    user = models.CharField(User,max_length=200)
    role = models.CharField(max_length=6, choices=ROLE, default='stock')
    department = models.CharField(max_length=20, choices=DEPARTMENT, default='muslin')
    apikey = models.CharField(max_length=100,default=None)
    apisecret = models.CharField(max_length=100,default=None)
    vrich_user = models.CharField(max_length=100,default=None)
    vrich_password = models.CharField(max_length=100,default=None)
    storename = models.CharField(max_length=100,default=None)
    databasename = models.CharField(max_length=100,default=None)
