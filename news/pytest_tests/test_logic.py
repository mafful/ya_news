# test_logic.py
import pytest
from http import HTTPStatus

# # Дополнительно импортируем функцию slugify.
# from pytils.translit import slugify
from pytest_django.asserts import assertRedirects

from django.urls import reverse

from news.models import Comment

# Импортируем из модуля forms сообщение об ошибке:
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(pk_for_args, client, form_data,):
    """Анонимный пользователь не может отправить комментарий."""
    comments_in_db = Comment.objects.all()
    url = reverse('news:detail', args=pk_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_in_db.count()


@pytest.mark.django_db
def test_user_can_create_comment(
        pk_for_args,
        author_client,
        author, form_data
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_in_db = Comment.objects.count()
    url = reverse('news:detail', args=pk_for_args)
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(url, data=form_data)
    print(Comment.objects.all())
    assertRedirects(response, reverse(
        'news:detail', args=pk_for_args) + '#comments')
    # Считаем общее количество заметок в БД, ожидаем 1 заметку.
    assert Comment.objects.count() == comments_in_db + 1
    # Чтобы проверить значения полей заметки -
    # получаем её из базы при помощи метода get():
    new_comment = Comment.objects.get()
    print(new_comment.author)
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(pk_for_args, author_client):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=pk_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    # print(response.content.decode('utf-8'))
    assert WARNING in response.content.decode('utf-8')


@pytest.mark.django_db
def test_author_can_edit_note(
        author_client,
        form_data,
        comment,
        comment_pk_for_args
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    # Получаем адрес страницы редактирования заметки:
    url = reverse('news:edit', args=comment_pk_for_args)
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(url, form_data)
    # Проверяем редирект:
    assert response.status_code == 302
    # Обновляем объект заметки note: получаем обновлённые данные из БД:
    comment.refresh_from_db()
    print(comment.text, form_data['text'])
    # Проверяем, что атрибуты заметки соответствуют обновлённым:
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(
        author_client,
        comment,
        comment_pk_for_args
):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_in_db = Comment.objects.all()
    print(comments_in_db.count())
    url = reverse('news:delete', args=comment_pk_for_args)
    print(url)
    response = author_client.post(url)
    # Check for a successful response
    assert response.status_code == 302
    # Check that the comment is no longer in the database
    with pytest.raises(Comment.DoesNotExist):
        Comment.objects.get(pk=comment.pk)
    print(Comment.objects.count(), comments_in_db.count())
    assert Comment.objects.count() == comments_in_db.count()


@pytest.mark.django_db
def test_other_user_cant_edit_note(
        admin_client,
        form_data,
        comment,
        comment_pk_for_args
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=comment_pk_for_args)
    response = admin_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(pk=comment.pk)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_other_user_cant_delete_note(admin_client, comment_pk_for_args):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_in_db = Comment.objects.all()
    url = reverse('news:delete', args=comment_pk_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_in_db.count()
