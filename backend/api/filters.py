from django_filters import rest_framework as filters

from recipes.models import Ingredients, Recipes, Tag


class RecipeFilterSet(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        method='filter_tags', queryset=Tag.objects.all(), to_field_name='slug'
    )

    class Meta:
        model = Recipes
        fields = (
            'name', 'tags', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def filter_is_favorited(self, queryset, field_name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, field_name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    @staticmethod
    def filter_tags(queryset, field_name, value):
        if value:
            return queryset.filter(tags__in=value).distinct()
        return queryset


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredients
        fields = ('name',)
