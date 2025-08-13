from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'favorites_count', 'products_list', 'tags_list', 'image_tag'
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('author', 'tags', 'cooking_time')
    list_select_related = ('author',)
    readonly_fields = ('favorites_count',)
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _favorites_count=Count('favorites', distinct=True)
        ).select_related('author').prefetch_related(
            'tags',
            'ingredients_in_recipe__ingredient'
        )

    @admin.display(description='В избранном', ordering='_favorites_count')
    def favorites_count(self, recipe):
        return getattr(recipe, '_favorites_count', 0)

    @admin.display(description='Продукты')
    def products_list(self, recipe):
        try:
            return mark_safe(
                '<br>'.join([
                    f'{ri.ingredient.name} - '
                    f'{ri.amount} {ri.ingredient.measurement_unit}'
                    for ri in recipe.ingredients_in_recipe.select_related(
                        'ingredient').all()
                ]))
        except (AttributeError, ObjectDoesNotExist):
            return "Нет данных"

    @admin.display(description='Теги')
    def tags_list(self, recipe):
        try:
            return mark_safe('<br>'.join([tag.name for tag in recipe.tags.all()]))
        except (AttributeError, ObjectDoesNotExist):
            return "Нет тегов"

    @admin.display(description='Изображение')
    def image_tag(self, recipe):
        if not recipe.image:
            return "Нет изображения"
        return mark_safe(
            f'<img src="{recipe.image.url}" '
            f'style="height: 50px; object-fit: cover; border-radius: 4px;" />'
        )