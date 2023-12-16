import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

# Обозначаем, что тесту нужен доступ к БД.
# Без этой метки тест выдаст ошибку доступа к БД.
pytestmark = pytest.mark.django_db


HOME_URL = 'news:home'
DETAIL_URL = 'news:detail'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'


@pytest.mark.parametrize(
    'choosen_client', (
        pytest.lazy_fixture('client'),
        pytest.lazy_fixture('admin_client')
    )
)
@pytest.mark.parametrize(
    'name', (
        HOME_URL,
        DETAIL_URL,
        'users:login',
        'users:logout',
        'users:signup'),
)
def test_page_availability_for_any_user(choosen_client, name, news_detail_url):
    """Доступность страниц YaNote for any user"""
    if name == DETAIL_URL:
        url = news_detail_url
    else:
        url = reverse(name)
    response = choosen_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'choosen_client, status', (
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'url, reverse_url', (
        (EDIT_URL, pytest.lazy_fixture('comment_edit_url')),
        (DELETE_URL, pytest.lazy_fixture('comment_delete_url'))
    )
)
def test_availability_for_comment_edit_and_delete(
        url,
        choosen_client,
        status,
        reverse_url
):
    """Доступность страниц Edit, Delete YaNews for any user"""
    if choosen_client == 'client':
        login_url = reverse('users:login')
        url = reverse_url
        expected_url = f'{login_url}?next={url}'
        response = choosen_client.get(url)
        assertRedirects(response, expected_url)
    else:
        url = reverse_url
        response = choosen_client.get(url)
        assert response.status_code == status
