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


def test_anonymous_user_cant_create_comment(
        comment_edit_url, login_url, client
):
    """Анонимный пользователь не может создать комментарий."""
    initial_comments = sorted(Comment.objects.all())

    response = client.post(comment_edit_url, data=FORM_DATA)
    expected_url = f'{login_url}?next={comment_edit_url}'
    assertRedirects(response, expected_url)

    final_comments = sorted(Comment.objects.all())
    assert initial_comments == final_comments


def test_user_can_create_comment(
        news,
        comment_edit_url,
        news_detail_url,
        author_client,
        author
):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(comment_edit_url, data=FORM_DATA)
    assertRedirects(response, news_detail_url + '#comments')

    assert Comment.objects.count() == 1

    new_comment = Comment.objects.first()
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
    bad_words_data = get_bad_words_data(word)
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

    changed_comment = Comment.objects.get(pk=comment.pk)
    assert changed_comment.text == FORM_DATA['text']
    assert changed_comment.news == comment.news
    assert changed_comment.author == comment.author


def test_author_can_delete_comment(
        author_client,
        comment,
        comment_delete_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    initial_number_of_comments = Comment.objects.count()

    response = author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_number_of_comments - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_other_user_cant_edit_note(
        admin_client,
        comment,
        comment_edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = admin_client.post(comment_edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_other_user_cant_delete_note(
        admin_client, comment, comment_delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    initial_number_of_comments = Comment.objects.count()
    comment_before = set(Comment.objects.filter(pk=comment.pk))
    response = admin_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_number_of_comments
    assert Comment.objects.filter(pk=comment.pk).exists()
    comment_after = set(Comment.objects.filter(pk=comment.pk))
    assert (
        comment_after == comment_before
    )
