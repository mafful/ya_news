from http import HTTPStatus
import pytest

pytestmark = pytest.mark.django_db

CLIENT = pytest.lazy_fixture('client')
ADMIN_CLIENT = pytest.lazy_fixture('admin_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')


@pytest.mark.parametrize(
    'choosen_client, page_name', [
        (CLIENT, 'home'),
        (CLIENT, 'detail'),
        (CLIENT, 'login'),
        (CLIENT, 'logout'),
        (CLIENT, 'signup'),
        (ADMIN_CLIENT, 'home'),
        (ADMIN_CLIENT, 'detail'),
        (ADMIN_CLIENT, 'login'),
        (ADMIN_CLIENT, 'logout'),
        (ADMIN_CLIENT, 'signup'),
    ]
)
def test_page_availability_for_any_user(
    choosen_client,
    page_name,
    news,
    news_urls
):
    """Доступность страниц YaNews for any user"""
    urls_instance = news_urls(pk=news.pk)
    if page_name == 'detail':
        url = urls_instance.detail_url
    else:
        url = getattr(urls_instance, f'{page_name}_url')
    response = choosen_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'choosen_client, expected_status, reverse_url', [
        (CLIENT, HTTPStatus.FOUND, 'edit_url'),
        (CLIENT, HTTPStatus.FOUND, 'delete_url'),
        (ADMIN_CLIENT, HTTPStatus.NOT_FOUND, 'edit_url'),
        (ADMIN_CLIENT, HTTPStatus.NOT_FOUND, 'delete_url'),
        (AUTHOR_CLIENT, HTTPStatus.OK, 'edit_url'),
        (AUTHOR_CLIENT, HTTPStatus.OK, 'delete_url'),
    ]
)
def test_availability_for_comment_edit_and_delete(
        news_urls,
        comment,
        choosen_client,
        expected_status,
        reverse_url
):
    """Доступность страниц Edit, Delete YaNews for any user"""
    urls_instance = news_urls(pk=comment.pk)
    url = getattr(urls_instance, reverse_url)

    if choosen_client == 'client':
        expected_url = urls_instance.get_expected_url(
            choosen_client, reverse_url)
        response = choosen_client.get(url)
        assert response.status_code == expected_status
        assert str(response.url) == expected_url
    else:
        response = choosen_client.get(url)
        print(url)
        assert response.status_code == expected_status


def test_news_urls(news_urls, comment):
    urls = news_urls(comment.pk)
    assert urls.home_url == '/'
    assert urls.detail_url == f'/news/{comment.pk}/'
    assert urls.edit_url == f'/edit_comment/{comment.pk}/'
    assert urls.delete_url == f'/delete_comment/{comment.pk}/'
    assert urls.login_url == '/auth/login/'
