from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from info.models import User

@admin.register(User)
class UserAdmin(UserAdmin):
    pass
# Register your models here.


# admin.register(User, User)