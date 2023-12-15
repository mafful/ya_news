# conftest.py
import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


# Текущая дата.
today = datetime.today()
# Вчера.
yesterday = today - timedelta(days=1)
# Завтра.
tomorrow = today + timedelta(days=1)


@pytest.fixture(autouse=True)
def news():
    news = News.objects.create(  # Создаём объект заметки.
        title='Новость с комментарием',
        text='Текст заметки',
    )
    return news


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания заметки.
def pk_for_args(news):
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (news.pk,)


@pytest.fixture
def all_news():
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    all_news = News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст заметки',
    )
    return comment


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания заметки.
def comment_pk_for_args(comment):
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (comment.pk,)


@pytest.fixture
def comments(news, author):
    comment_list = []
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(  # Создаём объект заметки.
            news=news,
            author=author,
            text=f'Текст заметки {index}',

        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comment_list.append(comment)
    return comment_list


# Добавляем фикстуру form_data
@pytest.fixture
def form_data(author):
    return {
        'text': 'Новый текст',
        'author': author,
    }
