from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'название',
        max_length=settings.OTHER_NAME_LIMIT,
        db_index=True,
        unique=True,
        help_text='Введите название',
    )
    color = models.CharField(
        'цветовой HEX-код',
        max_length=settings.COLOR_LIMIT,
        unique=True,
        help_text='Введите HEX-код',
    )
    slug = models.SlugField(
        'ссылка',
        max_length=settings.OTHER_NAME_LIMIT,
        unique=True,
        help_text='Введите ссылкy',
    )

    class Meta:
        verbose_name_plural = 'теги'
        default_related_name = 'tegs'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'название',
        max_length=settings.OTHER_NAME_LIMIT,
        db_index=True,
        help_text='Введите название',
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=settings.OTHER_NAME_LIMIT,
        help_text='Введите единицу измерения',
    )

    class Meta:
        verbose_name_plural = 'ингредиенты'
        default_related_name = 'ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredients_units')]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipe',
    )
    name = models.CharField(
        'название',
        max_length=settings.OTHER_NAME_LIMIT,
        db_index=True,
        unique=True,
        help_text='Введите название',
    )
    image = models.ImageField(
        upload_to='static/images/',
        verbose_name='картинкa',
        help_text='Добавьте картинку',
    )
    text = models.TextField(
        'описание',
        help_text='Введите описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        help_text='Выберете ингредиенты',
        verbose_name='ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Название тега',
        help_text='Выберите тег')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, 'Минимальное время приготовления')],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe')]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        help_text='Укажите ингредиенты')
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Минимальное количество ингредиентов 1')],
        verbose_name='Количество',
        help_text='Укажите количество ингредиента')

    class Meta:
        verbose_name = 'Cостав рецепта'
        verbose_name_plural = 'Состав рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients')]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='покупатель',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='лист покупок',
    )

    class Meta:
        verbose_name_plural = 'список покупок'
        default_related_name = 'shopping_cart'
        constraints = [
            models.UniqueConstraint(
                name='unique_shopping_cart',
                fields=["user", "recipe"],)
        ]

    def __str__(self):
        return (f'Пользователь {self.user.username}'
                f'хочет собирается {self.recipe.name}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='покупатель',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='лист покупок',
    )

    class Meta:
        verbose_name_plural = 'список избранных'
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite',
                fields=["user", "recipe"],)
        ]

    def __str__(self):
        return (f'Пользователю {self.user.username}'
                f'нравится рецепт "{self.recipe.name}"')
