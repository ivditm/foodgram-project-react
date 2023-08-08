from http import HTTPStatus
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase


from recipes.models import Cart, Favorites, Tag, Recipes, Ingredients
from users.models import Follow, User

URLS = ['tags', 'recipes',
        'users', 'ingredients']

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

MY_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='my.gif',
    content=MY_GIF,
    content_type='image/gif'
)
PATH_TO_PICTURE = 'recipes/my.gif'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class RecipeApiTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='pizdec',
                                       email='pizdec@yandex.ru',
                                       first_name='pizdec',
                                       last_name='pizdec',
                                       password='pizdec1234')
        cls.user_1 = User.objects.create(username='suka',
                                         email='suka@yandex.ru',
                                         first_name='pizdec',
                                         last_name='pizdec',
                                         password='suka1234')
        cls.user_2 = User.objects.create(username='blya',
                                         email='blya@yandex.ru',
                                         first_name='blya',
                                         last_name='blya',
                                         password='blya1234')
        cls.tag = Tag.objects.create(name='breakfast',
                                     slug='breakfast',
                                     color='blue')
        cls.tag_1 = Tag.objects.create(name='dinner',
                                       slug='dinner',
                                       color='red')
        cls.ingredient = Ingredients.objects.create()
        cls.recipe = Recipes.objects.create(text='fuck_it_all',
                                            author=cls.user,
                                            cooking_time=2,
                                            name='fuck_all',
                                            image=UPLOADED)
        cls.recipe.ingredients.add(cls.ingredient,
                                   through_defaults={'amount': 3})
        cls.recipe.tags.add(cls.tag)
        cls.recipe_1 = Recipes.objects.create(text='fuck_it_all',
                                              author=cls.user_1,
                                              cooking_time=2,
                                              name='fuck_all',
                                              image=UPLOADED)
        cls.recipe.ingredients.add(cls.ingredient,
                                   through_defaults={'amount': 10})
        cls.recipe.tags.add(cls.tag_1)
        cls.shopping_list = Cart.objects.create(user=cls.user,
                                                recipe=cls.recipe)
        cls.favorite = Favorites.objects.create(user=cls.user,
                                                recipe=cls.recipe)
        cls.follow = Follow.objects.create(following=cls.user,
                                           user=cls.user_1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client_1 = APIClient()
        self.client_1.force_authenticate(user=self.user_1)
        self.client_not_auth = APIClient()

    def test_access(self):
        for user in [self.client, self.client_not_auth]:
            for addres in URLS + [f'recipes/{self.recipe.id}',
                                  f'tags/{self.tag.id}',
                                  f'ingredients/{self.ingredient.id}']:
                self.assertEqual((user
                                  .get(f'/api/{addres}/')
                                  .status_code),
                                 HTTPStatus.OK)

    def test_create_account(self):
        url = '/api/users/'
        data = {'username': 'dobby',
                'email': 'dobby@yandex.ru',
                'first_name': 'dobby',
                'last_name': 'dobby',
                'password': 'dobby1234'}
        response = self.client_not_auth.post(url, data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.latest('id').username, 'dobby')

    def test_login(self):
        data = {'email': 'blya@yandex.ru',
                'password': 'blya1234'}
        self.assertEqual(self.client_not_auth.post('/api/auth/token/login/',
                         data, format='json').status_code, HTTPStatus.OK)

    def test_profile(self):
        self.assertEqual(self.client.get(
            '/api/users/me/').status_code, HTTPStatus.OK)
        self.assertEqual(self.client_1.get(
            f'/api/users/{self.user.id}/').status_code, HTTPStatus.OK)

    def test_chage_password(self):
        """Что-то непонятное"""
        url = '/api/users/set_password/'
        data = {'current_password': 'pizdec1234',
                'new_password': 'Verydifficultpassword1298'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.first().password,
                         'Verydifficultpassword1298')

    def test_create_recipe(self):
        url = '/api/recipes/'
        data = {"ingredients": [{"id": 1, "amount": 10}], "tags": [
            1],
            "image": "data:image/png;base64,"
                     "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa"
                     "AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EA"
                     "AAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAAB"
                     "JRU5ErkJggg==",
            "name": "suka_new_post",
            "text": "suka_new_post", "cooking_time": 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(Recipes.objects.count(), 4)
        self.assertEqual(Recipes.objects.latest('id').name, 'suka_new_post')

    def test_delete_recipes(self):
        self.assertEqual(self.client_1.delete(
            f'/api/recipes/{self.recipe.id}/').status_code,
            HTTPStatus.FORBIDDEN)
        self.assertEqual((self.client
                          .delete(f'/api/recipes/{self.recipe.id}/')
                          .status_code),
                         HTTPStatus.NO_CONTENT)

    def test_change_recipe(self):
        url = f'/api/recipes/{self.recipe.id}/'
        data = {"ingredients": [{"id": 1, "amount": 10}], "tags": [
            1],
            "image": "data:image/png;base64,"
                     "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa"
                     "AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EA"
                     "AAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAAB"
                     "JRU5ErkJggg==",
            "name": "suka_new_post",
            "text": "suka_new_post", "cooking_time": 1}
        response_unautor = self.client_1.patch(url, data, format='json')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response_unautor.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_shopping_cart(self):
        url = '/api/recipes/download_shopping_cart/'
        url_1 = f'/api/recipes/{self.recipe.id}/shopping_cart/'
        url_2 = f'/api/recipes/{self.recipe_1.id}/shopping_cart/'
        response = self.client.get(url)
        data = {"id": 1,
                "name": "fuck_all",
                "image": PATH_TO_PICTURE,
                "cooking_time": 2}
        data_1 = {"id": 3,
                  "name": "fuck_all",
                  "image": PATH_TO_PICTURE,
                  "cooking_time": 2}
        wrong_post_response = self.client.post(url_1, data, format='json')
        good_post_response = self.client.post(url_2, data_1, format='json')
        delete_response = self.client.delete(url_1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(wrong_post_response.status_code,
                         HTTPStatus.BAD_REQUEST)
        self.assertEqual(good_post_response.status_code, HTTPStatus.CREATED)
        self.assertEqual(delete_response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Cart.objects.filter(
            user=self.user, recipe=self.recipe).exists())
        # self.assertEqual(delete_response.status_code, HTTPStatus.BAD_REQUEST)

    def test_favorite(self):
        url_1 = f'/api/recipes/{self.recipe.id}/favorite/'
        url_2 = f'/api/recipes/{self.recipe_1.id}/favorite/'
        data = {"id": 1,
                "name": "fuck_all",
                "image": PATH_TO_PICTURE,
                "cooking_time": 2}
        data_1 = {"id": 3,
                  "name": "fuck_all",
                  "image": PATH_TO_PICTURE,
                  "cooking_time": 2}
        wrong_post_response = self.client.post(url_1, data, format='json')
        good_post_response = self.client.post(url_2, data_1, format='json')
        delete_response = self.client.delete(url_1)
        self.assertEqual(wrong_post_response.status_code,
                         HTTPStatus.BAD_REQUEST)
        self.assertEqual(good_post_response.status_code, HTTPStatus.CREATED)
        self.assertEqual(delete_response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Favorites.objects.filter(
            user=self.user, recipe=self.recipe).exists())

    def test_followings(self):
        url = '/api/users/subscriptions/'
        url_1 = f'/api/users/{self.recipe.id}/subscribe/'
        # url_2 = f'/api/users/{self.recipe_1.id}/shopping_cart/'
        response = self.client.get(url)
        data = {
            "email": "suka@yandex.ru",
            "id": 0,
            "username": "pizdec",
            "first_name": "pizdec",
            "last_name": "pizdec",
            "is_subscribed": True,
            "recipes":

            [

                {
                    "id": 0,
                    "name": "fuck_all",
                    "image": PATH_TO_PICTURE,
                    "cooking_time": 2
                }
            ],
            "recipes_count": 1

        }
        delete_response = self.client_1.delete(url_1)
        good_post_response = self.client_1.post(url_1, data, format='json')
        wrong_post_response = self.client_1.post(url_1, data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(delete_response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(good_post_response.status_code, HTTPStatus.CREATED)
        self.assertEqual(wrong_post_response.status_code,
                         HTTPStatus.BAD_REQUEST)
