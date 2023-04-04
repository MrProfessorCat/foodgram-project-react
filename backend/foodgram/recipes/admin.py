from django.contrib import admin

from .models import (
    Tag, Ingredient, Recipe, IngredientAmount, Favourite,
    ShoppingCart
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientAmountAdmin(admin.TabularInline):
    model = IngredientAmount
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientAmountAdmin,)
    list_display = (
        'id', 'name', 'author', 'text', 'created', 'num_favourite'
    )
    search_fields = ('name', 'author__username', 'tags')
    list_filter = ('name', 'author__username', 'tags')
    filter_vertical = ('tags',)

    def num_favourite(self, obj):
        return obj.favourite.count()


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
