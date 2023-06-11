from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core import constants
from core.validators import validate_hexname
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'название',
        max_length=constants.OTHER_NAME_LIMIT,
        db_index=True,
        unique=True,
        help_text='Введите название',
    )
    color = models.CharField(
        'цветовой HEX-код',
        validators=(validate_hexname, ),
        max_length=constants.COLOR_LIMIT,
        unique=True,
        help_text='Введите HEX-код',
    )
    slug = models.SlugField(
        'ссылка',
        max_length=constants.OTHER_NAME_LIMIT,
        unique=True,
        help_text='Введите ссылкy',
    )

    class Meta:
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'название',
        max_length=constants.OTHER_NAME_LIMIT,
        db_index=True,
        help_text='Введите название',
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=constants.OTHER_NAME_LIMIT,
        help_text='Введите единицу измерения',
    )

    class Meta:
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredients_units')]

    def __str__(self):
        return self.name


class RecipeQuerySet(models.QuerySet):
    def annotate_is_fav_and_is_in_shop_cart(self, user):
        if user.is_authenticated:
            return self.annotate(
                is_favorited=models.Exists(
                    user.favorite.filter(
                        recipe__pk=models.OuterRef('pk'))),
                is_in_shopping_cart=models.Exists(
                    user.shopping_cart.filter(
                        recipe__pk=models.OuterRef('pk')))
            )


class Recipe(models.Model):
    objects = RecipeQuerySet.as_manager()

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipe',
    )
    name = models.CharField(
        'название',
        max_length=constants.OTHER_NAME_LIMIT,
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
        blank=False,
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
        validators=[
            MinValueValidator(1, 'Минимальное время приготовления'),
            MaxValueValidator(99999, 'Максимальное время приготовления')],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ('-pub_date', )
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
            MinValueValidator(1, 'Минимальное количество ингредиентов 1'),
            MaxValueValidator(99999, 'Максимальное количество ингредиентов')],
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


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='покупатель',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='лист покупок',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return (f'Пользователь {self.user.username}'
                f'добавил рецепт "{self.recipe.name}"'
                f'в {self.__class__.__name__}')


class ShoppingCart(UserRecipe):

    class Meta(UserRecipe.Meta):
        abstract = False
        verbose_name_plural = 'список покупок'
        default_related_name = 'shopping_cart'
        constraints = [
            models.UniqueConstraint(
                name='unique_shopping_cart',
                fields=['user', 'recipe'],)
        ]


class Favorite(UserRecipe):

    class Meta(UserRecipe.Meta):
        abstract = False
        verbose_name_plural = 'список избранных'
        default_related_name = 'favorite'
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite',
                fields=['user', 'recipe'],)
        ]
