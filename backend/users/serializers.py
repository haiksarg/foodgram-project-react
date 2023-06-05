from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
from .models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'password',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and request.user.follower.filter(author=obj).exists())


class MiniRecipeSerialzer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields

    def get_image(self, recipe):
        return recipe.image.url


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='author.recipe.all().count()')

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        model = Follow

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and request.user.follower.filter(
                    author=self.context.get('author')).exists())

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.author.recipe.all()
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return MiniRecipeSerialzer(recipes, many=True).data

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        if user.follower.filter(author=author).exists():
            raise ValidationError(
                {'error': 'Вы уже подписаны на этого пользователя!'},
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(
                {'error': 'Невозможно подписаться на себя!'},
                code=status.HTTP_400_BAD_REQUEST)
        return data
