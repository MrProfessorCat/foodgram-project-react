from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from django.db import models

from .validators import validate_tag_color


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        help_text='Введите название тега'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цветовой hex-код',
        help_text='Введите цветовой код в 16-ричном формате',
        validators=(validate_tag_color,)
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='slug',
        help_text='Введите slug'
    )

    def __str__(self) -> str:
        return self.name

    def clean(self):
        self.color = self.color.lower()
        return super().clean()

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Укажите единицу измерения'
    )

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'),
        )


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(MinValueValidator(1),),
    )

    class Meta:
        verbose_name = 'Кол-во ингредиентов'
        verbose_name_plural = 'Кол-во ингредиентов'
        # constraints = (
        #     models.UniqueConstraint(
        #         fields=('recipe', 'ingredient'),
        #         name='unique_ingredients_in_recipe'),
        # )


class Recipe(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        help_text='Укажите дату создания'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название рецепта'
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Напишите рецепт'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        help_text='Выберите автора рецепта',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        IngredientAmount,
        verbose_name='Ингредиенты',
        help_text='Укажите ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Добавьте теги'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка к рецепту',
        help_text='Добавьте картинку к посту'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Укажите время приготовления блюда',
        validators=(MinValueValidator(1), MaxValueValidator(300))
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favourite'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favourite'
    )

    class Meta:
        verbose_name = 'Избранная подписка'
        verbose_name_plural = 'Избранные подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='favourite_unique'
            ),
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        help_text='Укажите пользователя',
        on_delete=models.CASCADE,
        related_name='shoppingcart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        help_text='Выберите рецепт, который хотите добавить в список',
        on_delete=models.CASCADE,
        related_name='shoppingcart'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
