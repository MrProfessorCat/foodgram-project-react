from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='get_queryset'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_queryset'
    )

    def get_queryset(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if name == 'is_favorited':
                list_of_recipes_ids = user.favourite.values('recipe_id')
            if name == 'is_in_shopping_cart':
                list_of_recipes_ids = user.shoppingcart.values('recipe_id')

            query_param = self.request.query_params.get(name)
            if query_param == '1':
                queryset = queryset.filter(id__in=list_of_recipes_ids)
            if query_param == '0':
                queryset = queryset.exclude(id__in=list_of_recipes_ids)
        return queryset

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart',)
