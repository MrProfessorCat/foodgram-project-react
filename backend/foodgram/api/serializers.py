from django.contrib.auth import get_user_model
from rest_framework import serializers, validators
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Tag, Recipe, Ingredient, IngredientAmount

User = get_user_model()


class SimpleRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        user_made_request = self.context.get('request').user
        return (
            user_made_request.is_authenticated
            and user_made_request.followers.filter(author=obj).exists()
        )


class UserWithRecipesSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        if hasattr(self.context, 'query_params'):
            recipes_limit = self.context.query_params.get('recipes_limit')
            if (
                recipes_limit and recipes_limit.isdigit()
                and int(recipes_limit) >= 0
            ):
                recipes = recipes[:int(recipes_limit)]
        return SimpleRecipeSerializer(
            recipes,
            many=True).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        validators = (
            validators.UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'measurement_unit'),
                message=(
                    'Ингредиенты с одним названием и одной '
                    'единицей измерения не должны повторяться'
                )
            ),
        )


class IngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    tags = TagSerializer(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user_made_request = self.context.get('request').user
        return (
            user_made_request.is_authenticated
            and user_made_request.favourite.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user_made_request = self.context.get('request').user
        return (
            user_made_request.is_authenticated
            and user_made_request.shoppingcart.filter(recipe=obj).exists()
        )


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = IngredientPostSerializer(many=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    image = Base64ImageField(required=False, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    @staticmethod
    def insert_ingredients(ingredients, recipe):
        ingregients_amounts = [
            IngredientAmount(
                ingredient_id=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ]
        IngredientAmount.objects.bulk_create(ingregients_amounts)

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                (
                    'В рецепте должен быть указан '
                    'хотя бы один ингредиент'
                )
            )
        if not all(
            [
                Ingredient.objects.filter(id=ingredient.get('id'))
                for ingredient in ingredients
            ]
        ):
            raise serializers.ValidationError(
                (
                    'Вы пытаетесь добавить в рецепт '
                    'несуществующий ингредиент'
                )
            )

        if len(ingredients) != len(
            set([item['id'] for item in ingredients])
        ):
            raise serializers.ValidationError(
                (
                    'Не может быть несколько одинаковых '
                    'ингредиентов в одном рецепте'
                )
            )

        if any([True for item in ingredients if item.get('amount') < 1]):
            raise serializers.ValidationError(
                (
                    'Кол-во каждого ингредиента в рецепте '
                    'не может быть меньше 1'
                )
            )

        tags = data.get('tags')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                (
                    'Для одного рецепта не может быть '
                    'назначено несколько одинаковых тегов'
                )
            )

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.insert_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.set(validated_data.get('tags', instance.tags))
        ingredients = validated_data.pop('ingredients')

        if ingredients:
            instance.ingredients.get_queryset().delete()
            self.insert_ingredients(ingredients, instance)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
