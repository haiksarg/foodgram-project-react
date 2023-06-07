from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .paginations import ApiPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          ReadRecipeSerialzer, ShoppingCartSerializer,
                          TagSerializer, WriteRecipeSerialzer)
from core.mixins import RetrieveListViewSet
from core.utils import shopping_cart
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.serializers import MiniRecipeSerialzer


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, )
    permission_classes = (AllowAny, )
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly, )
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend, )
    pagination_class = ApiPagination
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.select_related(
            'author').prefetch_related(
                'tegs', 'ingredient').all(
                    ).annotate_is_fav_and_is_in_shop_cart(
                        self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerialzer
        return WriteRecipeSerialzer

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        if user.shopping_cart.exists():
            sum_ingredients_in_recipes = IngredientRecipe.objects.filter(
                    recipe__shopping_cart__user=user
                ).values(
                    'ingredient__name', 'ingredient__measurement_unit'
                ).annotate(
                    amounts=Sum('amount')).order_by('ingredient__name')
            return shopping_cart(self, request, sum_ingredients_in_recipes)
        return Response('Список покупок пуст.',
                        status=status.HTTP_404_NOT_FOUND)

    def shopping_cart_favorite_create(self, request, pk, serializer_class):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        serializer = serializer_class(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MiniRecipeSerialzer(recipe).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.shopping_cart_favorite_create(
            request, pk, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(ShoppingCart,
                          user=self.request.user,
                          recipe__pk=pk).delete()
        return Response('Рецепт успешно удалён из списка покупок.',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.shopping_cart_favorite_create(
            request, pk, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(Favorite,
                          user=self.request.user,
                          recipe__pk=pk).delete()
        return Response('Рецепт успешно удалён из избранного.',
                        status=status.HTTP_204_NO_CONTENT)
