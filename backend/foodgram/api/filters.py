from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='get_queryset_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_queryset_shopping_cart'
    )

    def get_queryset_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            is_favorited = self.request.query_params.get(name)
            if is_favorited is not None and is_favorited == '1':
                queryset = queryset.filter(
                    favourite__user=self.request.user
                )
            if is_favorited is not None and is_favorited == '0':
                queryset = queryset.exclude(
                    favourite__user=self.request.user
                )
        return queryset

    def get_queryset_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            is_in_shopping_cart = self.request.query_params.get(name)
            if is_in_shopping_cart is not None and is_in_shopping_cart == '1':
                queryset = queryset.filter(
                    shoppingcart__user=self.request.user
                )
            if is_in_shopping_cart is not None and is_in_shopping_cart == '0':
                queryset = queryset.exclude(
                    shoppingcart__user=self.request.user
                )
        return queryset

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart',)
