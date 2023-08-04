from django.contrib import admin
from .models import User


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'wallet_address', 'sso_type')


admin.site.register(User, UserAdmin)
