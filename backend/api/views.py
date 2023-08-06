from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (Cart, Favorites, Ingredients, RecipeIngridient,
                            Recipes, Tag)
from users.models import Follow
from .filters import IngredientsFilter, RecipeFilterSet
from .mixins import AddDelViewMixin, RetriveAndListViewSet
from .pagination import PageLimitPagination
from .permissions import AdminOrReadOnly, AuthorStaffOrReadOnly
from .serializers import (AddRecipeSerializer, FavouriteSerializer,
                          IngredientSerializer, ShoppingListSerializer,
                          ShowRecipeFullSerializer, TagSerializer,
                          UserSubscribeSerializer)

User = get_user_model()


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):

    pagination_class = PageLimitPagination
    permission_classes = (DjangoModelPermissions,)
    add_serializer = UserSubscribeSerializer
    link_model = Follow

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Создаёт/удалет связь между пользователями."""

    @subscribe.mapping.post
    def create_subscribe(self, request, id):
        return self._create_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        return self._delete_relation(Q(following__id=id))

    @action(
        methods=("get",), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            User.objects.filter(followings__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientsViewSet(RetriveAndListViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    pagination_class = None


def download_file_response(ingredients_list):
    shop_list = []
    for item in ingredients_list:
        shop_list.append(f'{item["ingredient__name"]} - {item["amount"]} '
                         f'{item["ingredient__measurement_unit"]} \n')

    response = HttpResponse(shop_list, 'Content-Type: text/plain')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="buylist.txt"')
    return response


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all().order_by('-id')
    serializer_class = ShowRecipeFullSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeFullSerializer
        return AddRecipeSerializer

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=(AuthorStaffOrReadOnly,),
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipes, id=pk)
        if request.method == "POST":
            if Favorites.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": "Этот рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite = Favorites.objects.create(user=user, recipe=recipe)
            serializer = FavouriteSerializer(favorite,
                                             context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            favorite = Favorites.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        permission_classes=(AuthorStaffOrReadOnly,),
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipes, id=pk)
        if request.method == "POST":
            if Cart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": "Этот рецепт уже в корзине покупок"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            shoping_cart = Cart.objects.create(user=user,
                                               recipe=recipe)
            serializer = ShoppingListSerializer(
                shoping_cart, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            delete_shoping_cart = Cart.objects.filter(user=user,
                                                      recipe=recipe)
            if delete_shoping_cart.exists():
                delete_shoping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["GET"],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients_list = RecipeIngridient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return download_file_response(ingredients_list)
