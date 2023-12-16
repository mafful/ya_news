import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

# Текущая дата.
today = datetime.today()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture(autouse=True)
def news():
    news = News.objects.create(  # Создаём объект заметки.
        title='Новость с комментарием',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def all_news():
    return [
        News.objects.create(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст заметки',
    )
    return comment


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def comments(news, author):
    now = timezone.now()
    return [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст заметки {index}',
            created=now + timedelta(days=index),
        )
        for index in range(222)
    ]


# Добавляем фикстуру form_data
@pytest.fixture
def form_data(author):
    return {
        'text': 'Новый текст',
        'author': author,
    }
