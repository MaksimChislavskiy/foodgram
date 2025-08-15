from django.urls import include, path
from ingredients.views import IngredientViewSet
from recipes.views import RecipeViewSet
from rest_framework import routers
from tags.views import TagViewSet
from users.views import CustomUserViewSet


router = routers.DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/',
         CustomUserViewSet.as_view({'get': 'me'}),
         name='user-me'),
    path('users/me/avatar/',
         CustomUserViewSet.as_view({
             'put': 'update_avatar',
             'patch': 'update_avatar',
             'delete': 'update_avatar',
         }),
         name='user-avatar'),
    path('users/set_password/',
         CustomUserViewSet.as_view({'post': 'set_password'}),
         name='user-set-password'),
    path('', include(router.urls)),
]
