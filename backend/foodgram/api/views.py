from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.conf import settings

from djoser.views import UserViewSet
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
)
from rest_framework.response import Response

from users.models import Follow
from recipes.models import Tag, Recipe, Ingredient, Favourite, ShoppingCart
from .serializers import (
    TagSerializer, RecipePostSerializer, RecipeGetSerializer,
    IngredientSerializer, SimpleRecipeSerializer, CustomUserSerializer,
    UserWithRecipesSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsAdminAuthorOrReadOnly
)


User = get_user_model()


class ExtraAction:
    """
    Класс для реализации дополнительных ендпоинтов
    subscribe, favorite, shopping_cart
    """
    ERRORS_TEXTS = {
        Follow: {
            'already_exists': (
                'Вы уже подписаны на '
                'пользователя {}'
            ),
            'not_exists': (
                'Вы не были подписаны '
                'на пользователя {}'
            )
        },
        Favourite: {
            'already_exists': (
                'Рецепт {} '
                'уже добавлен в Избранное'
            ),
            'not_exists': (
                'Рецепт {} не '
                'находился в Избранном'
            )
        },
        ShoppingCart: {
            'already_exists': (
                'Рецепт {} '
                'уже добавлен в список покупок'
            ),
            'not_exists': (
                'Рецепт {} не '
                'находился в списке покупок'
            )
        },
    }

    def extra_action(self, request, model, bind_model, id):
        obj = get_object_or_404(model, id=id)
        if model == User and obj == request.user:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            if model == Recipe:
                _, created = bind_model.objects.get_or_create(
                    recipe=obj, user=request.user
                )
            if model == User:
                _, created = bind_model.objects.get_or_create(
                    author=obj, user=request.user
                )
            if created:
                if model == Recipe:
                    serializer = SimpleRecipeSerializer(obj)
                if model == User:
                    serializer = UserWithRecipesSerializer(
                        obj, context=request
                    )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'errors': self.ERRORS_TEXTS[
                        bind_model]['already_exists'].format(obj)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            try:
                if model == Recipe:
                    bind_model.objects.get(
                        user=request.user, recipe=obj
                    ).delete()
                if model == User:
                    bind_model.objects.get(
                        user=request.user, author=obj
                    ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    {'errors': self.ERRORS_TEXTS[
                        bind_model]['not_exists'].format(obj)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as other_exception:
                return Response(
                    {'errors': str(other_exception)},
                    status=status.HTTP_400_BAD_REQUEST
                )


class CustomUserViewSet(UserViewSet, ExtraAction):
    queryset = User.objects.order_by('pk')
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination

    @action(
            detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        limit = request.query_params.get('limit')
        if limit and limit.isdigit() and int(limit) > 0:
            PageNumberPagination.page_size = limit
        page = self.paginate_queryset(
            User.objects.prefetch_related('recipes').filter(
                followings__user=self.request.user).order_by('pk')
        )
        PageNumberPagination.page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        serializer = UserWithRecipesSerializer(
            page, many=True, context=request
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        return self.extra_action(request, User, Follow, id)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.order_by('pk')
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet, ExtraAction):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminAuthorOrReadOnly)

    def get_queryset(self):
        queryset = Recipe.objects.select_related('author').order_by('created')

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        if self.request.user.is_authenticated:
            is_favorited = self.request.query_params.get('is_favorited')
            if is_favorited is not None and is_favorited == '1':
                queryset = queryset.filter(favourite__user=self.request.user)
            if is_favorited is not None and is_favorited == '0':
                queryset = queryset.exclude(favourite__user=self.request.user)

            is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart'
            )
            if is_in_shopping_cart is not None and is_in_shopping_cart == '1':
                queryset = queryset.filter(
                    shoppingcart__user=self.request.user
                )
            if is_in_shopping_cart is not None and is_in_shopping_cart == '0':
                queryset = queryset.exclude(
                    shoppingcart__user=self.request.user
                )

        return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.extra_action(request, Recipe, Favourite, pk)

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.extra_action(request, Recipe, ShoppingCart, pk)

    @action(
        detail=False, methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        short_names = {
            'name': 'recipe__ingredient_amount__ingredient__name',
            'measurement_unit':
            'recipe__ingredient_amount__ingredient__measurement_unit',
            'amount': 'recipe__ingredient_amount__amount',
            'sum_amount': 'recipe__ingredient_amount__amount__sum'
        }

        shopping_carts = request.user.shoppingcart.select_related(
            'recipe'
        ).values(
            short_names['name'],
            short_names['measurement_unit']
        ).annotate(Sum(short_names['amount']))

        ingredients_list = ''
        for ingredient in shopping_carts:
            ingredients_list += (
                f'{ingredient.get(short_names["name"])}: '
                f'{ingredient.get(short_names["sum_amount"])} '
                f'{ingredient.get(short_names["measurement_unit"])}\n'
            )
        response = HttpResponse(ingredients_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.order_by('pk')
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
