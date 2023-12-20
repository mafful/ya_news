from http import HTTPStatus
import pytest

pytestmark = pytest.mark.django_db

CLIENT = pytest.lazy_fixture('client')
ADMIN_CLIENT = pytest.lazy_fixture('admin_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')
COMMENT_EDIT_URL = pytest.lazy_fixture('comment_edit_url')
COMMENT_DELETE_URL = pytest.lazy_fixture('comment_delete_url')


CLIENTS_AND_URLS = [
    (CLIENT, HOME_URL, '/', HTTPStatus.OK),
    (CLIENT, LOGIN_URL, '/auth/login/', HTTPStatus.OK),
    (CLIENT, LOGOUT_URL, '/auth/logout/', HTTPStatus.OK),
    (CLIENT, SIGNUP_URL, '/auth/signup/', HTTPStatus.OK),
    (CLIENT, NEWS_DETAIL_URL, '/news/1/', HTTPStatus.OK),
    (ADMIN_CLIENT, HOME_URL, '/', HTTPStatus.OK),
    (ADMIN_CLIENT, LOGIN_URL, '/auth/login/', HTTPStatus.OK),
    (ADMIN_CLIENT, LOGOUT_URL, '/auth/logout/', HTTPStatus.OK),
    (ADMIN_CLIENT, SIGNUP_URL, '/auth/signup/', HTTPStatus.OK),
    (ADMIN_CLIENT, NEWS_DETAIL_URL, '/news/1/', HTTPStatus.OK),
]


@pytest.mark.parametrize(
    'choosen_client, url_name, url_path, expected_status',
    CLIENTS_AND_URLS
)
def test_page_availability_for_any_user(
    choosen_client, url_name, url_path, expected_status
):
    """Доступность страниц YaNews for any user"""
    response = choosen_client.get(url_name)
    print(response.request['PATH_INFO'], url_path)
    assert response.status_code == expected_status
    assert response.request['PATH_INFO'] == url_path


@pytest.mark.parametrize(
    'url', [COMMENT_EDIT_URL, COMMENT_DELETE_URL]
)
def test_redirection_for_anonymous(client, login_url, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    expected_url = f'{login_url}?next={url}'
    assert response.url == expected_url
