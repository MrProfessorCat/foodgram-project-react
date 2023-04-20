from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin
)
from django.contrib.auth.forms import (
    UserCreationForm as DjangoCreationForm
)

from .models import User



@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                        'first_name', 'last_name', 'username',
                        'email', 'password1', 'password2'
            ),
        }),
    )
    username_field = 'email'
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    list_filter = (
        'username',
        'email'
    )
    search_fields = (
        'username',
        'email'
    )
