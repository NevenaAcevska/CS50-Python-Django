from django.contrib import admin

# Register your models here.
from Math.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'level', 'score')
    list_filter = ('username', 'level', 'score')