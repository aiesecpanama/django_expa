#coding:utf-8
from __future__ import unicode_literals
import base64
from django.utils.encoding import python_2_unicode_compatible
from django.db import models

@python_2_unicode_compatible
class LoginData(models.Model):
    email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=64)
    def __str__(self):
        return self.email
    def save(self, *args, **kwargs):
        self.password = base64.b64encode(self.password.encode())
        super(LoginData, self).save(*args, **kwargs)
        
        

# Create your models here.
