# Generated by Django 3.2.18 on 2023-04-16 19:35

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import recipes.validators
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favourite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранная подписка',
                'verbose_name_plural': 'Избранные подписки',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название ингредиента', max_length=200, validators=[recipes.validators.validate_ingredient], verbose_name='Название')),
                ('measurement_unit', models.CharField(help_text='Укажите единицу измерения', max_length=200, validators=[recipes.validators.validate_ingredient], verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Укажите дату создания', verbose_name='Дата создания')),
                ('name', models.CharField(help_text='Введите название рецепта', max_length=200, validators=[users.validators.only_letters_validator], verbose_name='Название')),
                ('text', models.TextField(help_text='Напишите рецепт', verbose_name='Текст рецепта')),
                ('image', models.ImageField(blank=True, help_text='Добавьте картинку к посту', upload_to='posts/', verbose_name='Картинка к рецепту')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='Укажите время приготовления блюда', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(300)], verbose_name='Время приготовления (в минутах)')),
                ('author', models.ForeignKey(help_text='Выберите автора рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(error_messages={'unique': 'Тег с таким названием уже есть'}, help_text='Введите название тега', max_length=200, unique=True, validators=[users.validators.only_letters_validator], verbose_name='Название')),
                ('color', models.CharField(help_text='Введите цветовой код в 16-ричном формате', max_length=7, validators=[recipes.validators.validate_tag_color], verbose_name='Цветовой hex-код')),
                ('slug', models.SlugField(help_text='Введите slug', max_length=200, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Выберите рецепт, который хотите добавить в список', on_delete=django.db.models.deletion.CASCADE, related_name='+', to='recipes.recipe', verbose_name='Рецепт')),
                ('user', models.ForeignKey(help_text='Укажите пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Покупка',
                'verbose_name_plural': 'Покупки',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Добавьте теги', to='recipes.Tag', verbose_name='Теги'),
        ),
        migrations.CreateModel(
            name='IngredientAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='recipes.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Кол-во ингредиентов',
                'verbose_name_plural': 'Кол-во ингредиентов',
            },
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient'),
        ),
        migrations.AddField(
            model_name='favourite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favourite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourite', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_ingredients_in_recipe'),
        ),
        migrations.AddConstraint(
            model_name='favourite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='favourite_unique'),
        ),
    ]
