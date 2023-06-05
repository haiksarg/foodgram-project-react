from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'get_recipes',
                    'get_followers', 'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'

    @admin.display(description='recipes')
    def get_recipes(self, obj):
        return obj.recipe.all().count()

    @admin.display(description='followers')
    def get_followers(self, obj):
        return obj.following.all().count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('author',)
    search_fields = ('user',)
