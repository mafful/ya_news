from http import HTTPStatus
import pytest

pytestmark = pytest.mark.django_db

CLIENT = pytest.lazy_fixture('client')
ADMIN_CLIENT = pytest.lazy_fixture('admin_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')


@pytest.mark.parametrize(
    'choosen_client, expected_status', [
        (CLIENT, HTTPStatus.OK),
        (ADMIN_CLIENT, HTTPStatus.OK),
    ]
)
def test_page_availability_for_any_user(
    choosen_client,
    expected_status,
    home_url,
    login_url,
    logout_url,
    signup_url,
    news_detail_url
):
    """Доступность страниц YaNews for any user"""
    home_response = choosen_client.get(home_url)
    assert home_response.status_code == expected_status
    login_response = choosen_client.get(login_url)
    assert login_response.status_code == expected_status
    logout_response = choosen_client.get(logout_url)
    assert logout_response.status_code == expected_status
    signup_response = choosen_client.get(signup_url)
    assert signup_response.status_code == expected_status
    detail_response = choosen_client.get(news_detail_url)
    assert detail_response.status_code == expected_status


def test_redirection_for_anonymous(
        client,
        comment_edit_url,
        comment_delete_url,
):
    edit_response = client.get(comment_edit_url)
    assert edit_response.status_code == HTTPStatus.FOUND
    assert 'login' in edit_response.url

    delete_response = client.get(comment_delete_url)
    assert delete_response.status_code == HTTPStatus.FOUND
    assert 'login' in delete_response.url
