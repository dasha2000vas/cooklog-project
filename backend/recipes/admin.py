from django.contrib import admin

from .models import Tag, Ingredient, Recipe, IngredientRecipe


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 3


class UserAdmin(admin.ModelAdmin):
    list_filter = ('name', 'e-mail',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author__username', 'tags__name',)
    inlines = (IngredientRecipeInline,)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
