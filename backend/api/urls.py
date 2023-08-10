from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientsViewSet,
    RecipeViewSet,
    TagViewSet
)
from users.views import UserViewSet, FollowViewSet
app_name = "api"

router = DefaultRouter()
router.register("tags", TagViewSet, "tags")
router.register("ingredients", IngredientsViewSet, "ingredients")
router.register("recipes", RecipeViewSet, "recipes")
router.register("users", UserViewSet, "users")
router.register(
    r'users/(?P<user_id>\d+)/subscribe', FollowViewSet,
    basename='subscribe')


urlpatterns = [
    # path('users/<int:id>/subscribe/',
    #      FollowApiView.as_view(),
    #      name='subscribe'
    #      ),
    # path('users/subscriptions/', ListFollowViewSet.as_view(),
    #      name='subscription'
    #      ),
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
