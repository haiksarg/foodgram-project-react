from django.core.validators import MaxValueValidator, MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from core.serializers import Hex2NameColor
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = fields


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = fields


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(1, 'Минимальное количество ингредиентов 1'),
            MaxValueValidator(99999, 'Максимальное количество ингредиентов')],
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class WriteRecipeSerialzer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(
        many=True,
        write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(1, 'Минимальное время приготовления'),
            MaxValueValidator(99999, 'Максимальное время приготовления')],
    )

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'author',
                  'image', 'name', 'text', 'cooking_time')
        read_only_fields = ('author', )

    def to_representation(self, instance):
        return ReadRecipeSerialzer(instance).data

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Нужно выбрать хотя бы один ингредиент!'})
        inrgedient_id_list = [item['id'] for item in ingredients]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise ValidationError(
                {'ingredients': 'Ингридиенты повторяются!'})
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError(
                {'tags': 'Нужно выбрать хотя бы один тег!'})
        tags_list = set(tags)
        if len(tags) != len(tags_list):
            raise ValidationError(
                {'tags': 'Теги повторяются!'})
        return value

    def add_tags_ingredients(self, ingredients, tags, model):
        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(IngredientRecipe(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount']))
        IngredientRecipe.objects.bulk_create(
            ingredients_list,
            ignore_conflicts=True)
        model.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author_id=self.context.get('request').user.id,
            **validated_data)
        self.add_tags_ingredients(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.add_tags_ingredients(ingredients, tags, instance)
        return super().update(instance, validated_data)


class ReadRecipeSerialzer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    ingredients = IngredientRecipeSerializer(
        many=True, source='recipe_ingredients')
    tags = TagSerializer(many=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author', 'tags', 'ingredients', )

    def get_image(self, recipe):
        return recipe.image.url


class SelectRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'coocking_time')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        return SelectRecipeSerializer(instance).data

    def validate(self, data):
        user = self.context.get('request').user
        if user.favorite.filter(recipe=data.get('recipe')).exists():
            raise ValidationError(
                {'error': 'Вы уже добавили этот рецепт!'},
                code=status.HTTP_400_BAD_REQUEST)
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def to_representation(self, instance):
        return SelectRecipeSerializer(instance).data

    def validate(self, data):
        user = self.context.get('request').user
        if user.shopping_cart.filter(recipe=data.get('recipe')).exists():
            raise ValidationError(
                {'error': 'Вы уже добавили этот рецепт!'},
                code=status.HTTP_400_BAD_REQUEST)
        return data
