# test_routes.py
import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects


# Обозначаем, что тесту нужен доступ к БД.
# Без этой метки тест выдаст ошибку доступа к БД.
@pytest.mark.django_db
@pytest.mark.parametrize(
    'choosen_client', (
        pytest.lazy_fixture('client'),
        pytest.lazy_fixture('admin_client')
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_page_availability_for_any_user(choosen_client, name, args):
    """Доступность страниц YaNote for any user"""
    if 'detail' in name:
        url = reverse(name, args=(args.pk,))
    else:
        url = reverse(name)
    response = choosen_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'choosen_client, status', (
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK))
)
@pytest.mark.parametrize(
    'name, args', (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')))
)
def test_availability_for_comment_edit_and_delete(
        name,
        choosen_client,
        status,
        args
):
    """Доступность страниц Edit, Delete YaNews for any user"""
    url = reverse(name, args=(args.pk,))
    response = choosen_client.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', (
        ('news:edit', 'news:delete')
    )
)
def test_redirect_for_anonymous_client(client, name, comment_pk_for_args):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=comment_pk_for_args)
    print(url)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
