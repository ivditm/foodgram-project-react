from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'username', 'email', 'first_name', 'last_name', 'password'
    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '--hz--'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')
    list_filter = ('user', 'following')
    empty_value_display = '--hz--'
