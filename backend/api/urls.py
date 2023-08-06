from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientsViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("tags", TagViewSet, "tags")
router.register("ingredients", IngredientsViewSet, "ingredients")
router.register("recipes", RecipeViewSet, "recipes")
router.register("users", UserViewSet, "users")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
