import pytest

# from django.conf import settings
from django.urls import reverse


def common_response(client):
    url = reverse('news:home')
    response = client.get(url)
    return response.context['object_list']


@pytest.mark.django_db
def test_news_count(client, all_news):
    """Количество новостей на главной странице — не более 10."""
    object_list = common_response(client)
    news_count = len(object_list)
    # print(all_news)
    assert news_count == len(all_news) - 1


@pytest.mark.django_db
def test_news_order(client, all_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    object_list = common_response(client)
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, comments):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    object_list = common_response(client)
    news = [news for news in object_list
            if news.title == 'Новость с комментарием'][0]
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'choosen_client, name, args, answer',
    [
        (
            pytest.lazy_fixture('admin_client'),
            'news:detail',
            pytest.lazy_fixture('news'),
            True
        ),
        (
            pytest.lazy_fixture('client'),
            'news:detail',
            pytest.lazy_fixture('news'),
            False
        ),
    ]
)
def test_existing_of_form_for_choosen_client(
        choosen_client,
        name, args,
        answer
):
    """
    Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости, а авторизованному доступна.
    """
    url = reverse(name, args=(args.pk,))
    response = choosen_client.get(url)
    assert ('form' in response.context) is answer
