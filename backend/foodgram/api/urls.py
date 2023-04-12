from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, RecipeViewSet, IngredientViewSet,
    SubscribtionsView, SubscribeView
)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(r'users/<int:id>/subscribe/', SubscribeView.as_view()),
    path(r'users/subscriptions/', SubscribtionsView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
