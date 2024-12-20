from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.paginations import ApiPagination
from .models import Follow, User
from .serializers import FollowSerializer, FollowUserSerializer


class CustomUserViewSet(UserViewSet):
    pagination_class = ApiPagination
    permission_classes = (AllowAny, )

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        serializer = FollowSerializer(
            data={'user': user, 'author': author},
            context={'request': request, 'author': author})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=author, user=user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        get_object_or_404(
            Follow, user=self.request.user, author__id=id
        ).delete()
        return Response('Успешная отписка',
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        follows = User.objects.filter(
            following__user=self.request.user)
        pages = self.paginate_queryset(follows)
        serializer = FollowUserSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
