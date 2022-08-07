from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.non_author = User.objects.create_user(username='HasNoName')
        cls.URLS_MAPS = {
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}),
            'user_pofile': reverse(
                'posts:profile',
                kwargs={'username': cls.author.username}),
            'group_page': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}),
            'post_create': reverse('posts:post_create'),
            'home_page': reverse('posts:index'),
            'login': (reverse('users:login') + '?next='),
            'unexist': '/unexist/0/',
            'comments': reverse(
                'posts:add_comment',
                kwargs={'post_id': cls.post.id}),
            'follow_idex': reverse('posts:follow_index'),
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_non_author = Client()
        self.non_author = PostURLTests.non_author
        self.authorized_client_non_author.force_login(self.non_author)
        self.authorized_client_author = Client()
        self.author = PostURLTests.author
        self.authorized_client_author.force_login(self.author)

    def test_urls_unxist(self):
        """Запрос к несуществующей странице вернёт ошибку 404"""
        response = self.guest_client.get(
            self.URLS_MAPS['unexist'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_guest_client(self):
        """Страницы  доступны любому пользователю."""
        urls = [
            self.URLS_MAPS['home_page'],
            self.URLS_MAPS['group_page'],
            self.URLS_MAPS['user_pofile'],
            self.URLS_MAPS['post_detail'],
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_client(self):
        """Страницы  доступны авторизованному пользователю."""
        urls = [
            self.URLS_MAPS['post_create'],
            self.URLS_MAPS['follow_idex'],
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client_non_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_author_client(self):
        """Страницы доступны автору поста."""
        response = self.authorized_client_author.get(
            self.URLS_MAPS['post_edit'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects_guest_user_edit_post__on_login(self):
        """
        Анонимный пользователь будет перенапрален
        со страницы создания(редактирования) на страницу входа.
        """
        redirect_urls = {
            self.URLS_MAPS['post_create']:
                (self.URLS_MAPS['login'] + self.URLS_MAPS['post_create']),
            self.URLS_MAPS['post_edit']:
                (self.URLS_MAPS['login'] + self.URLS_MAPS['post_edit']),
        }
        for address, redirect_page in redirect_urls.items():
            with self.subTest(redirect_page=redirect_page):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect_page)

    def test_edit_post_redirect_non_author_on_post_page_edit(self):
        """
        Не автор поста будет перенаправлен со страницы редактирования
        на страницу просмотра поста
        """
        response = self.authorized_client_non_author.get(
            self.URLS_MAPS['post_edit'], follow=True)
        self.assertRedirects(response, self.URLS_MAPS['post_detail'])
