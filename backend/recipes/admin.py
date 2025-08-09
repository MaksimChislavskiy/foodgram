from django.contrib import admin
from .models import Recipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
        'ingredients',
        'tags'
    )
    search_fields = ('name', 'tags')


admin.site.register(Recipe, RecipeAdmin)
