import unittest
# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import Client, TestCase


# Получаем модель пользователя.
User = get_user_model()


@unittest.skip('пропуск тестовых тестов из списка тестов')
class TestNews(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя.
        cls.user = User.objects.create(username='testUser')
        # Создаём объект клиента.
        cls.user_client = Client()
        # "Логинимся" в клиенте при помощи метода force_login().
        cls.user_client.force_login(cls.user)
        print(cls.user_client)
        # Теперь через этот клиент можно отправлять запросы
        # от имени пользователя с логином "testUser".
