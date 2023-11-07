from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

User = get_user_model()

Group._meta.app_label = 'users'

admin.site.register(User, UserAdmin)
