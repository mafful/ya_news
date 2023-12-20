import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

FORM_DATA = {
    'text': 'Новый текст',
}


def test_news_count(client, home_url, all_news):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    news_quantity_in_response = len(response.context['object_list'])
    assert news_quantity_in_response == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, all_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    news_quantity_in_response = response.context['object_list']
    all_dates = [news.date for news in news_quantity_in_response]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, home_url, comments):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(home_url)
    news_quantity_in_response = response.context['object_list']
    news = news_quantity_in_response[0]
    all_comments_dates = [
        comment.created for comment in news.comment_set.all()
    ]
    assert all_comments_dates == sorted(all_comments_dates)


def test_anonymous_user_cannot_access_comment_form(
        client, news, news_detail_url
):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = client.get(news_detail_url, data=FORM_DATA)
    assert 'form' not in response.context


def test_authorised_client_can_access_comment_form(
        author_client, news_detail_url):
    """
    авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости
    """
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)
