import pytest

from django.urls import reverse

from news.forms import CommentForm
from .conftest import author

pytestmark = pytest.mark.django_db

HOME_URL = 'news:home'
DETAIL_URL = 'news:detail'

FORM_DATA = {
    'text': 'Новый текст',
    'author': author,
}


def common_response(client):
    url = reverse(HOME_URL)
    response = client.get(url)
    return response.context['object_list']


def test_news_count(client, all_news):
    """Количество новостей на главной странице — не более 10."""
    assert len(common_response(client)) == len(all_news) - 1


def test_news_order(client, all_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    object_list = common_response(client)
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


def test_comments_order(client, comments):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    object_list = common_response(client)
    news = [news for news in object_list
            if news.title == 'Новость с комментарием'][0]
    all_comments = [comment.created for comment in news.comment_set.all()]
    sorted_dates = sorted(all_comments, reverse=False)
    assert all_comments == sorted_dates


def test_existing_of_form_for_client(client, news_detail_url):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    url = news_detail_url
    response = client.get(url, data=FORM_DATA)
    assert 'form' not in response.context


def test_existing_of_form_for_admin_client(admin_client, news):
    """
    авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости
    """
    url = reverse(DETAIL_URL, args=(news.pk,))
    response = admin_client.get(url, data=FORM_DATA)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)
