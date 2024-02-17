from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Customer)     
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name','current_debt') 

@admin.register(Loan)     
class LoanAdmin(admin.ModelAdmin):
    list_display = ('customer','loan_amount')     