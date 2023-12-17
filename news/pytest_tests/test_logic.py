from http import HTTPStatus
import pytest

from pytest_django.asserts import (
    assertContains,
    assertRedirects
)

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


FORM_DATA = {
    'text': 'Новый текст',
}


def get_bad_words_data(word):
    return {
        'text': (
            f'Какой-то текст, '
            f'{word}, еще текст'
        )
    }


BAD_WORDS_DATA = get_bad_words_data


def test_anonymous_user_cant_create_comment(
        news, news_urls, client
):
    """Анонимный пользователь не может отправить комментарий."""
    comments_before = sorted(list(Comment.objects.all()))
    urls_instance = news_urls(pk=news.pk)
    url = urls_instance.detail_url
    response = client.post(url, data=FORM_DATA)
    login_url = urls_instance.login_url
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    comments_after = sorted(list(Comment.objects.all()))
    if not comments_before and not comments_after:
        assert True
    else:
        assert comments_before == comments_after


def test_user_can_create_comment(
        news,
        news_urls,
        author_client,
        author
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_startpoint = Comment.objects.count()
    urls_instance = news_urls(pk=news.pk)
    url = urls_instance.detail_url
    response = author_client.post(url, data=FORM_DATA)
    assertRedirects(response, url + '#comments')
    assert Comment.objects.count() == comments_startpoint + 1
    # Чтобы проверить значения полей заметки -
    # получаем её из базы при помощи метода get():
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(news_urls, news, author_client, word):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    urls_instance = news_urls(pk=news.pk)
    url = urls_instance.detail_url
    bad_words_data = BAD_WORDS_DATA(word)
    response = author_client.post(url, data=bad_words_data)
    #  Проверка наличия запрещённого слова в ответе
    assertContains(response, WARNING)
    # Проверка, что комментарий не был создан
    assert Comment.objects.count() == 0


def test_author_can_edit_note(
        news,
        author_client,
        comment,
        comment_edit_url
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(comment_edit_url, data=FORM_DATA)
    # Проверяем редирект:
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text != FORM_DATA['text']
    assert comment.news == news


def test_author_can_delete_comment(
        news_urls,
        author_client,
        comment
):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_before = Comment.objects.count()
    # assert comment in comments_before
    urls_instance = news_urls(pk=comment.pk)
    url = urls_instance.delete_url
    response = author_client.delete(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_before - 1
    comment_exists = Comment.objects.filter(pk=comment.pk).exists()
    assert not comment_exists


def test_other_user_cant_edit_note(
        news_urls,
        admin_client,
        comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    urls_instance = news_urls(pk=comment.pk)
    url = urls_instance.edit_url
    response = admin_client.post(url, data=FORM_DATA)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(pk=comment.pk)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_other_user_cant_delete_note(
        admin_client, comment, news_urls
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_before = Comment.objects.all()
    assert comment in comments_before
    urls_instance = news_urls(pk=comment.pk)
    url = urls_instance.delete_url
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_exists = Comment.objects.filter(pk=comment.pk).exists()
    assert comment_exists
