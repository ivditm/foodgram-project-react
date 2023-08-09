from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        ReadOnlyField)

from recipes.models import (Cart, Favorites, Ingredients, RecipeIngridient,
                            Recipes, Tag)
from users.models import Follow


User = get_user_model()


class ShortRecipeSerializer(ModelSerializer):

    class Meta:
        model = Recipes
        fields = "id", "name", "image", "cooking_time"
        read_only_fields = ("__all__",)


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta():
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=self.context['request'].user,
                                     following=obj).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ShowFollowSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        return Follow.objects.filter(
            following=obj, user=self.context['request'].user).exists()

    def get_recipes(self, obj):
        recipes_limit = int(self.context['request'].GET.get(
            'recipes_limit', 10))
        user = get_object_or_404(User, pk=obj.pk)
        recipes = Recipes.objects.filter(author=user)[:recipes_limit]

        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        user = get_object_or_404(User, pk=obj.pk)
        return Recipes.objects.filter(author=user).count()


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredients
        fields = "__all__"
        read_only_fields = ("__all__",)


class ShowRecipeIngredientsSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        source='ingredient'
    )
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngridient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ShowRecipeFullSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngridient.objects.filter(recipe=obj)
        return ShowRecipeIngredientsSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Cart.objects.filter(recipe=obj,
                                   user=request.user).exists()


class AddRecipeIngredientsSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = RecipeIngridient
        fields = ('id', 'amount')


class AddRecipeSerializer(ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = AddRecipeIngredientsSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = IntegerField()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate_ingridients(self, value):
        ingredients_set = []
        for ingredient in value:
            if ingredient['id'] in ingredients_set:
                raise ValidationError(
                    'Каждый ингредиент может быть упомянут только один раз'
                )
            elif ingredient['amount'] < 1:
                raise ValidationError(
                    'Количество ингредиентов должно быть'
                    ' положительным числом'
                )
            else:
                ingredients_set.append(ingredient)
        return value

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise ValidationError(
                'Каждый тег может быть упомянут только один раз'
            )
        return value

    def validate_cooking_time(self, value):
        if value <= 0:
            raise ValidationError('Время готовки должно быть положительным'
                                  ' числом, не менее 1 минуты!')
        return value

    def add_recipe_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if RecipeIngridient.objects.filter(
                    recipe=recipe,
                    ingredient=ingredient_id,
            ).exists():
                amount += ingredient['amount']
            RecipeIngridient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient_id,
                defaults={'amount': amount},
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(author=author, **validated_data)
        self.add_recipe_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.add_recipe_ingredients(ingredients, recipe)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        return ShortRecipeSerializer(
            recipe,
            context={'request': self.context.get('request')},
        ).data


class FavouriteSerializer(ModelSerializer):
    recipe = PrimaryKeyRelatedField(queryset=Recipes.objects.all())
    user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if Favorites.objects.filter(user=user, recipe__id=recipe_id).exists():
            raise ValidationError('Рецепт уже добавлен в избранное!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(instance.recipe, context=context).data


class ShoppingListSerializer(ModelSerializer):
    recipe = PrimaryKeyRelatedField(queryset=Recipes.objects.all())
    user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Cart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if Cart.objects.filter(user=user,
                               recipe__id=recipe_id).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(instance.recipe, context=context).data
