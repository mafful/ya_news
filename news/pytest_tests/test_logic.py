from http import HTTPStatus
import pytest

from pytest_django.asserts import (
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
        comment_edit_url, login_url, client
):
    """Анонимный пользователь не может отправить комментарий."""
    comments_before = sorted(Comment.objects.all())
    response = client.post(comment_edit_url, data=FORM_DATA)
    expected_url = f'{login_url}?next={comment_edit_url}'
    assertRedirects(response, expected_url)
    comments_after = sorted(Comment.objects.all())
    assert comments_before == comments_after


def test_user_can_create_comment(
        news,
        comment_edit_url,
        news_detail_url,
        author_client,
        author
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(comment_edit_url, data=FORM_DATA)
    assertRedirects(response, news_detail_url + '#comments')

    if Comment.objects.count() == 1:
        new_comment = Comment.objects.get()
        # Сверяем атрибуты объекта с ожидаемыми.
        assert new_comment.text == FORM_DATA['text']
        assert new_comment.author == author
        assert new_comment.news == news


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(news_detail_url, author_client, word):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = BAD_WORDS_DATA(word)
    response = author_client.post(news_detail_url, data=bad_words_data)
    form_errors = response.context['form'].errors.get('text', [])
    assert WARNING in form_errors
    # Проверка, что комментарий не был создан
    assert Comment.objects.count() == 0


def test_author_can_edit_note(
        news,
        author_client,
        comment,
        comment_edit_url
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(comment_edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.news == news


def test_author_can_delete_comment(
        author_client,
        comment,
        comment_delete_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_before = Comment.objects.count()
    # assert comment in comments_before
    response = author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_before - 1
    comment_exists = Comment.objects.filter(pk=comment.pk).exists()
    assert not comment_exists


def test_other_user_cant_edit_note(
        admin_client,
        comment,
        comment_edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = admin_client.post(comment_edit_url, data=FORM_DATA)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(pk=comment.pk)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_other_user_cant_delete_note(
        admin_client, comment, comment_delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_before = Comment.objects.count()
    assert comment in Comment.objects.all()
    response = admin_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
    comment_exists = Comment.objects.filter(pk=comment.pk).exists()
    assert comment_exists
