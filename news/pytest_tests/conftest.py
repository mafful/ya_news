from datetime import datetime, timedelta
import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def expected_url(login_url):
    def inner(url):
        return f'{login_url}?next={url}'
    return inner


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Новость с комментарием',
        text='Текст заметки',
    )


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def all_news():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(300)
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст заметки',
    )


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def comments(news, author):
    now = timezone.now()
    [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст заметки {index}',
            created=now - timedelta(days=index),
        )
        for index in range(222)
    ]
