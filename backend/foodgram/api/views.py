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


class CustomUserViewSet(UserViewSet):
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
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if author != request.user:
                follow, created = Follow.objects.get_or_create(
                    user=request.user,
                    author=author
                )
                if created:
                    serializer = UserWithRecipesSerializer(
                        follow.author, context=request
                    )
                    return Response(
                        serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response(
                        {'errors': (
                                        'Вы уже подписаны на '
                                        f'пользователя {author}'
                                    )},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            try:
                Follow.objects.get(user=request.user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    {'errors': (
                                    'Вы не были подписаны '
                                    f'на пользователя {author}'
                                )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as other_exception:
                return Response(
                    {'errors': str(other_exception)},
                    status=status.HTTP_400_BAD_REQUEST
                )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.order_by('pk')
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
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
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            _, created = Favourite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if created:
                serializer = SimpleRecipeSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'errors': (
                                    f'Рецепт "{recipe}" '
                                    'уже добавлен в Избранное'
                                )},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            try:
                Favourite.objects.get(
                    user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    {'errors': (
                                    f'Рецепт "{recipe}" не '
                                    'находился в Избранном'
                                )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as other_exception:
                return Response(
                    {'errors': str(other_exception)},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            _, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if created:
                serializer = SimpleRecipeSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'errors': (
                                    f'Рецепт "{recipe}" '
                                    'уже добавлен в список покупок'
                                )},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if request.method == 'DELETE':
            try:
                ShoppingCart.objects.get(
                    user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    {'errors': (
                                    f'Рецепт "{recipe}" не '
                                    'находился в Списке покупок'
                                )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as other_exception:
                return Response(
                    {'errors': str(other_exception)},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
