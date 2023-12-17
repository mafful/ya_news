import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

FORM_DATA = {
    'text': 'Новый текст',
}


def home_url(client, url='news:home'):
    url = reverse(url)
    response = client.get(url)
    return response.context['object_list']


def test_news_count(client, all_news):
    """Количество новостей на главной странице — не более 10."""
    assert settings.NEWS_COUNT_ON_HOME_PAGE == len(home_url(client))


def test_news_order(client, all_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    object_list = home_url(client)
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, comments):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    object_list = home_url(client)
    news = object_list[0]
    all_comments_dates = [
        comment.created for comment in news.comment_set.all()
    ]
    assert all_comments_dates == sorted(all_comments_dates, reverse=False)


def test_existing_of_form_for_client(client, news, news_urls):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    urls_instance = news_urls(pk=news.pk)
    url = urls_instance.detail_url
    response = client.get(url, data=FORM_DATA)
    assert 'form' not in response.context


def test_existing_of_form_for_admin_client(author_client, comment, news_urls):
    """
    авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости
    """
    urls_instance = news_urls(pk=comment.pk)
    url = urls_instance.detail_url
    response = author_client.get(url)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)
