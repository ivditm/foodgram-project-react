from django.contrib import admin

from .models import (Cart, Favorites, Ingredients, RecipeIngridient, Recipes,
                     RecipeTag, Tag)


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


@admin.register(Ingredients)
class AdminIngredient(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ['name']
    search_fields = ('name',)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngridient


class RecipeTagsInline(admin.TabularInline):
    model = RecipeTag


@admin.register(Recipes)
class AdminRecipe(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites')
    list_filter = ['name', 'author', 'tags']
    inlines = (RecipeIngredientsInline, RecipeTagsInline)

    def favorites(self, obj):
        return obj.favorites.all().count()


@admin.register(Favorites)
class AdminFavorite(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(Cart)
class AdminCart(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
