from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.pagination import CustomPagination
from .models import Subscribe
from .serializers import (
    CustomUserSerializer,
    SubscribeSerializer,
    AvatarUpdateSerializer
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
        methods=['put', 'patch', 'delete'],  # Добавляем 'delete'
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        parser_classes=[MultiPartParser]
    )
    def update_avatar(self, request):
        user = request.user

        if request.method in ['PUT', 'PATCH']:
            if 'avatar' not in request.data:
                return Response(
                    {'error': 'No avatar file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.avatar:  # Удаляем старый аватар, если он есть
                user.avatar.delete()

            user.avatar = request.data['avatar']
            user.save()
            serializer = AvatarUpdateSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            if not user.avatar:  # Если аватара нет, возвращаем 404
                return Response(
                    {'error': 'Avatar does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

            user.avatar.delete()  # Удаляем файл аватара
            user.avatar = None    # Очищаем поле в БД
            user.save()
            # Успешный ответ без тела
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
            serializer = SubscribeSerializer(author,
                                             data=request.data,
                                             context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
