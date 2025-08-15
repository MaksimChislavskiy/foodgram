from api.pagination import CustomPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Subscribe
from .serializers import (
    AvatarUpdateSerializer,
    CustomUserSerializer,
    SubscribeSerializer,
)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy', 'me']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'patch', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def update_avatar(self, request):
        user = request.user
        serializer = AvatarUpdateSerializer(user,
                                            data=request.data,
                                            partial=True)
        if request.method in ['PUT', 'PATCH']:
            if 'avatar' not in request.data:
                return Response(
                    {'error': 'No avatar data provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user.avatar:
                user.avatar.delete()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            if not user.avatar:
                return Response(
                    {'error': 'Avatar does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            if Subscribe.objects.filter(user=user, author=author).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'error': 'Вы не можете подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                subscription = Subscribe.objects.get(user=user, author=author)
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscribe.DoesNotExist:
                return Response(
                    {'errors': 'Подписка не существует!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)
