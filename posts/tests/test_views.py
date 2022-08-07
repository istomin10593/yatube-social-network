import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.views import COUNTER_POST

from ..forms import CommentForm
from ..models import Group, Follow, Post

User = get_user_model()

STEP = 1
COUNTER_POST_FOR_TEST = COUNTER_POST + STEP
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='auth',
            first_name='Джон',
            last_name='Джонович',
        )
        cls.non_author = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_non_post = Group.objects.create(
            title='Тестовая группа - без поста',
            slug='test-slug-non-post',
            description='Тестовое описание',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )
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
            'group_no_post': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group_non_post.slug}),
            'post_create': reverse('posts:post_create'),
            'home_page': reverse('posts:index'),
            'unexist': '/unexist/',
            'follow_idex': reverse('posts:follow_index'),
            'follow': reverse(
                'posts:profile_follow',
                kwargs={'username': cls.author.username}),
            'unfollow': reverse(
                'posts:profile_unfollow',
                kwargs={'username': cls.author.username}),

        }
        cls.form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.author = PostURLTests.author
        self.authorized_client_author.force_login(self.author)
        self.authorized_client_non_author = Client()
        self.non_author = PostURLTests.non_author
        self.authorized_client_non_author.force_login(self.non_author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.URLS_MAPS['home_page']: 'posts/index.html',
            self.URLS_MAPS['group_page']: 'posts/group_list.html',
            self.URLS_MAPS['user_pofile']: 'posts/profile.html',
            self.URLS_MAPS['post_detail']: 'posts/post_detail.html',
            self.URLS_MAPS['post_edit']: 'posts/create_post.html',
            self.URLS_MAPS['post_create']: 'posts/create_post.html',
            self.URLS_MAPS['unexist']: 'core/404.html',
            self.URLS_MAPS['follow_idex']: 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_home_page_profile_post_detail_show_correct_context(self):
        """
        Шаблон HOMEPAGE, USER_PROFILE сформированы
        с правильным контекстом. Пост отображается на странице.
        """
        urls = [
            self.URLS_MAPS['home_page'],
            self.URLS_MAPS['user_pofile'],
        ]
        for url in urls:
            response = self.guest_client.get(url)
            first_context = response.context['page_obj'][0]
            page_context = {
                PostURLTests.post.text: first_context.text,
                PostURLTests.post.group: first_context.group,
                PostURLTests.post.author: first_context.author,
                PostURLTests.post.pub_date: first_context.pub_date,
                PostURLTests.post.image: first_context.image,
            }
            for page_data, context_data in page_context.items():
                with self.subTest(post_data=page_data):
                    self.assertEqual(context_data, page_data)

    def test_post_detail_show_correct_context(self):
        """
        Шаблон POST_DETAIL  сформированы с правильным контекстом.
        Пост отображается на странице.
        """
        response = self.guest_client.get(self.URLS_MAPS['post_detail'])
        first_context = response.context['post']
        posts_count_context = response.context['posts_count']
        page_context = {
            PostURLTests.post.text: first_context.text,
            PostURLTests.post.group: first_context.group,
            PostURLTests.post.author: first_context.author,
            PostURLTests.post.pub_date: first_context.pub_date,
            PostURLTests.post.image: first_context.image,
            PostURLTests.author.posts.all().count(): posts_count_context,
        }
        for page_data, context_data in page_context.items():
            with self.subTest(post_data=page_data):
                self.assertEqual(context_data, page_data)

    def test_group_page_show_correct_context(self):
        """
        Шаблон URL_GROUP_PAGE сформирован с правильным контекстом.
        Пост отображается на странице.
        """
        response = self.guest_client.get(self.URLS_MAPS['group_page'])
        page_context = response.context['page_obj'][0]
        group_context = response.context['group']
        page_context = {
            PostURLTests.post.text: page_context.text,
            PostURLTests.post.group: page_context.group,
            PostURLTests.post.author: page_context.author,
            PostURLTests.post.pub_date: page_context.pub_date,
            PostURLTests.group.title: group_context.title,
            PostURLTests.group.description: group_context.description,
            PostURLTests.group.slug: group_context.slug,
            PostURLTests.post.image: page_context.image,
        }
        for page_data, context_data in page_context.items():
            with self.subTest(post_data=page_data):
                self.assertEqual(context_data, page_data)

    def test_post_edit_post__create_get_correct_context(self):
        """
        Шаблон POST_EDIT/POST_CREATE
        сформированы с правильным контекстом.
        """
        urls = [
            self.URLS_MAPS['post_edit'],
            self.URLS_MAPS['post_create'],
        ]
        for url in urls:
            response = self.authorized_client_author.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value, url=url):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_one_post_with_group_doesnt_shown_on_other_group(self):
        """
        Пост из одной группы не будет отображаться на страницы
        другой группы
        """
        response = self.guest_client.get(self.URLS_MAPS['group_no_post'])
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_follow_possible(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок.
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан на него"""
        response_before = self.authorized_client_non_author.get(
            self.URLS_MAPS['follow_idex'])
        self.assertNotIn(
            self.post,
            response_before.context['page_obj'])

        self.authorized_client_non_author.get(
            self.URLS_MAPS['follow'])
        response_after_follow = self.authorized_client_non_author.get(
            self.URLS_MAPS['follow_idex'])
        self.assertTrue(
            Follow.objects.filter(
                user=self.non_author,
                author=self.author).exists()
        )
        self.assertIn(
            self.post,
            response_after_follow.context['page_obj'])

        self.authorized_client_non_author.get(self.URLS_MAPS['unfollow'])
        response_after_unfollow = self.authorized_client_non_author.get(
            self.URLS_MAPS['follow_idex'])
        self.assertFalse(
            Follow.objects.filter(
                user=self.non_author,
                author=self.author).exists()
        )
        self.assertNotIn(
            self.post,
            response_after_unfollow.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        post_list = range(COUNTER_POST_FOR_TEST)
        Post.objects.bulk_create(
            [Post(author=cls.author, text=f'Тестовый пост{x}', group=cls.group)
                for x in post_list])
        cls.URLS_MAPS = {
            'user_pofile': reverse(
                'posts:profile',
                kwargs={'username': cls.author.username}),
            'group_page': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}),
            'home_page': reverse('posts:index'),
        }

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """
        Проверяет количество постов на страницах.
        На первой 10, на второй 1
        """
        urls = [
            self.URLS_MAPS['home_page'],
            self.URLS_MAPS['group_page'],
            self.URLS_MAPS['user_pofile'],
        ]
        for url in urls:
            urls_value = {
                url: COUNTER_POST,
                (url + '?page=2'): STEP,
            }
            for url_value, value in urls_value.items():
                with self.subTest(value=value, url=url):
                    response = self.client.get(url_value)
                    self.assertEqual(
                        len(response.context['page_obj']), value)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='auth',
            first_name='Джон',
            last_name='Джонович',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()

    def test_cache_index_pages(self):
        """Проверка работы кэширования данных главной страницы"""
        first_response = self.guest_client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.author,
            text='Еще один пост',
        )
        response_added_post = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            first_response.content,
            response_added_post.content
        )
        cache.clear()
        response_after_cache_clean = self.guest_client.get(
            reverse('posts:index'))
        self.assertNotEqual(
            first_response.content,
            response_after_cache_clean.content
        )
