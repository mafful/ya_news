import pytest

from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import (
    assertRedirects,
    assertQuerysetEqual,
    assertContains
)


from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db

HOME_URL = 'news:home'
LOGIN_URL = 'users:login'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'


def test_anonymous_user_cant_create_comment(
        news_detail_url, client, form_data
):
    """Анонимный пользователь не может отправить комментарий."""
    comments_before = Comment.objects.all()
    response = client.post(news_detail_url, data=form_data)
    login_url = reverse(LOGIN_URL)
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    comments_after = Comment.objects.all()
    assertQuerysetEqual(
        comments_before, comments_after)


def test_user_can_create_comment(
        news,
        news_detail_url,
        author_client,
        author, form_data
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_startpoint = Comment.objects.filter(author=author).count()
    url = news_detail_url
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(url, data=form_data)
    assertRedirects(response, news_detail_url + '#comments')
    # Считаем общее количество заметок в БД, ожидаем 1 заметку.
    assert Comment.objects.filter(
        author=author).count() == comments_startpoint + 1
    # Чтобы проверить значения полей заметки -
    # получаем её из базы при помощи метода get():
    new_comment = Comment.objects.filter(
        author=author).get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(news_detail_url, author_client, word):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = news_detail_url
    bad_words_data = {'text': f'Какой-то текст, {word}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    #  Проверка наличия запрещённого слова в ответе
    assertContains(response, WARNING)
    # Проверка, что комментарий не был создан
    assert Comment.objects.count() == 0


def test_author_can_edit_note(
        news,
        author_client,
        form_data,
        comment,
        comment_edit_url
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(comment_edit_url, form_data)
    # Проверяем редирект:
    assert response.status_code == 302
    # Обновляем объект заметки note: получаем обновлённые данные из БД:
    comment.refresh_from_db()
    # Проверяем, что атрибуты заметки соответствуют обновлённым:
    assert comment.text == form_data['text']
    assert comment.author == form_data['author']
    assert comment.news == news


def test_author_can_delete_comment(
        author_client,
        comment,
        comment_delete_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_before = Comment.objects.all()
    assert comment in comments_before
    response = author_client.delete(comment_delete_url)
    assert response.status_code == 302
    comments_after = Comment.objects.all()
    assert comment not in comments_after
    assert Comment.objects.count() == comments_before.count() - 1
    with pytest.raises(Comment.DoesNotExist):
        Comment.objects.get(pk=comment.pk)


def test_other_user_cant_edit_note(
        admin_client,
        form_data,
        comment,
        comment_edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = admin_client.post(comment_edit_url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(pk=comment.pk)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_other_user_cant_delete_note(
        admin_client, comment, comment_delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_before = Comment.objects.all()
    assert comment in comments_before
    response = admin_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_after = Comment.objects.all()
    assert comment in comments_after
