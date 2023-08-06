from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()

NAME_MAX_LENGHT = SLUG_TAG_MAX_LENGHT = 200
COLOR_TAG_MAX_LENGHT = 7
MIN_INT_VALUE = 1


class Tag(models.Model):
    name = models.CharField(verbose_name='название тэга',
                            max_length=NAME_MAX_LENGHT,
                            unique=True,
                            help_text='введите название тэга')
    slug = models.SlugField(verbose_name='слаг',
                            max_length=SLUG_TAG_MAX_LENGHT,
                            unique=True,
                            help_text='введите уникальный слаг')
    color = models.CharField(verbose_name='Цвет в HEX',
                             max_length=COLOR_TAG_MAX_LENGHT,
                             unique=True,
                             help_text='введите цвет в формате HEX')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        default_related_name = 'tags'

    def __str__(self) -> str:
        return self.name


class Ingredients(models.Model):
    name = models.CharField(verbose_name='Название ингридиента',
                            max_length=NAME_MAX_LENGHT,
                            help_text='введите название ингридиента')
    measurement_unit = models.CharField(verbose_name='единицы измерения',
                                        max_length=NAME_MAX_LENGHT,
                                        help_text='введите меру измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        db_table = 'ingridients'
        default_related_name = 'ingrodients'

    def __str__(self) -> str:
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey('Recipes',
                               on_delete=models.CASCADE,
                               verbose_name='ингридиент')
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            verbose_name='тэг')

    class Meta:
        verbose_name = 'тэг рецепта'
        verbose_name_plural = 'тэги рецепта'
        constraints = [
            UniqueConstraint(fields=['recipe', 'tag'],
                             name='unique_recipe_tag')
        ]

    def __str__(self):
        return 'тэги рецепта'


class Recipes(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='автор рецепта')
    name = models.CharField(verbose_name='название рецепта',
                            max_length=NAME_MAX_LENGHT,
                            help_text='введите название рецепта')
    text = models.TextField('описание рецепта')
    cooking_time = models.PositiveSmallIntegerField('время приготовления'
                                                    ' (в минутах)',
                                                    validators=[
                                                        MinValueValidator(
                                                            MIN_INT_VALUE,
                                                            'укажите хоть'
                                                            ' какое-то'
                                                            ' кол-во')],
                                                    help_text='введите время '
                                                    'приготовления в минутах')
    image = models.ImageField('картинка',
                              upload_to='recipes',
                              help_text='загрузите картинку')
    tags = models.ManyToManyField(Tag,
                                  through='RecipeTag',
                                  verbose_name='Теги рецепта',
                                  help_text='подберите тэги')
    ingredients = models.ManyToManyField(Ingredients,
                                         through='RecipeIngridient',
                                         help_text='выберите ингридиенты')
    pub_date = models.DateTimeField(verbose_name="Дата публикации",
                                    default=datetime.now(),
                                    editable=False)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self) -> str:
        return self.name


class RecipeIngridient(models.Model):
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               verbose_name='рецепт')
    ingredient = models.ForeignKey(Ingredients,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   verbose_name='ингридиенты')
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(
        MIN_INT_VALUE,
        'укажите хоть какое-то кол-во'
    )],
        verbose_name='кол-во '
    )

    class Meta:
        verbose_name = 'Рецепт с ингридиентами'
        verbose_name_plural = 'Рецепты с ингридиентами'

    def __str__(self):
        return 'рецепты с ингридиентами и их кол-вом'


class Cart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    @property
    def cooking_time(self):
        return self.recipe.cooking_time

    class Meta:
        constraints = [UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart'
        )]
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'


class Favorites(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    @property
    def cooking_time(self):
        return self.recipe.cooking_time

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite'
        )]
        ordering = ('-id',)
        verbose_name = 'избранное'
        default_related_name = 'favorites'
