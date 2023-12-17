from datetime import datetime, timedelta
import pytest

from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news_urls():
    class NewsURLs:

        def __init__(self, pk):
            self.HOME_URL = 'news:home'
            self.DETAIL_URL = 'news:detail'
            self.EDIT_URL = 'news:edit'
            self.DELETE_URL = 'news:delete'
            self.LOGIN_URL = 'users:login'
            self.LOGOUT_URL = 'users:logout'
            self.SIGNUP_URL = 'users:signup'

            self.home_url = reverse(self.HOME_URL)
            self.detail_url = reverse(self.DETAIL_URL, args=(pk,))
            self.edit_url = reverse(self.EDIT_URL, args=(pk,))
            self.delete_url = reverse(self.DELETE_URL, args=(pk,))
            self.login_url = reverse(self.LOGIN_URL)
            self.logout_url = reverse(self.LOGOUT_URL)
            self.signup_url = reverse(self.SIGNUP_URL)

        def get_expected_url(self, client, reverse_url):
            url = getattr(self, reverse_url)
            if client == self.client:
                return f'{self.login_url}?next={url}'
            else:
                return url

    return NewsURLs


@pytest.fixture
def choosen_client(request):
    client_type = request.param
    if client_type == 'client':
        return pytest.lazy_fixture('client')
    elif client_type == 'admin_client':
        return pytest.lazy_fixture('admin_client')
    elif client_type == 'author_client':
        return pytest.lazy_fixture('author_client')


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
def all_news():
    news_objects = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(300)
    ]
    News.objects.bulk_create(news_objects)
    return news_objects


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
    comments_objects = [
        Comment(
            news=news,
            author=author,
            text=f'Текст заметки {index}',
            created=now + timedelta(days=index),
        )
        for index in range(222)
    ]
    Comment.objects.bulk_create(comments_objects)
    return comments_objects
