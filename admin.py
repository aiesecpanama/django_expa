from django.contrib import admin
from .models import LoginData

# Register your models here.o

@admin.register(LoginData)
class LoginDataAdmin(admin.ModelAdmin):
    pass
