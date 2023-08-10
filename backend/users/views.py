from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response

from .mixins import CreateDestroyViewSet
from users.models import Follow
from api.pagination import PageLimitPagination
from api.serializers import (UserSerializer, ShowFollowSerializer)
User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions, ]
    pagination_class = PageLimitPagination

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = ShowFollowSerializer(
            pages,
            many=True,
            context={'request': request},)
        return self.get_paginated_response(serializer.data)


class FollowViewSet(CreateDestroyViewSet):
    serializer_class = ShowFollowSerializer

    def get_queryset(self):
        return self.request.user.follower.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['following_id'] = self.kwargs.get('user_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            following=get_object_or_404(
                User,
                id=self.kwargs.get('user_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, user_id):
        get_object_or_404(User, id=user_id)
        if not Follow.objects.filter(
                user=request.user, following_id=user_id).exists():
            return Response({'errors': 'Вы не были подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Follow,
            user=request.user,
            following_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
