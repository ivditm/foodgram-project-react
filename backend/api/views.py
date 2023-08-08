from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (Cart, Favorites, Ingredients, RecipeIngridient,
                            Recipes, Tag)
from users.models import Follow
from .filters import IngredientsFilter, RecipeFilterSet
from .pagination import PageLimitPagination
from .permissions import AdminOrReadOnly, AuthorStaffOrReadOnly
from .serializers import (AddRecipeSerializer, FavouriteSerializer,
                          IngredientSerializer, ShoppingListSerializer,
                          ShowRecipeFullSerializer, TagSerializer,
                          CustomUserSerializer, ShowFollowSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny, ]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('id', None)
        following = get_object_or_404(User, pk=pk)
        user = request.user

        if following == user:
            return Response(
                {'errors': 'Вы не можете подписываться на себя'},
                status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(following=following, user=user).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST)

        obj = Follow(following=following, user=user)
        obj.save()

        serializer = ShowFollowSerializer(
            following, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)
        try:
            subscription = get_object_or_404(Follow, user=user,
                                             following=following)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(
                'Ошибка отписки',
                status=status.HTTP_400_BAD_REQUEST,
            )


class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = ShowFollowSerializer
    pagination_class = PageLimitPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(followings__user=user)


class TagViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
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
