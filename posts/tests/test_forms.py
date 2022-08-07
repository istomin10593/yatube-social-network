import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            image=SimpleUploadedFile(
                name='post_small.gif',
                content=SMALL_GIF,
                content_type='image/gif'),
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
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
            'post_create': reverse('posts:post_create'),
            'comments': reverse(
                'posts:add_comment',
                kwargs={'post_id': cls.post.id}),
        }
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.author = PostFormTests.author
        self.authorized_client_author.force_login(self.author)

    def test_poste_create(self):
        """Валидная форма создает запись в POST_CREATE."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client_author.post(
            self.URLS_MAPS['post_create'],
            data=form_data,
            follow=True
        )
        post_latest = Post.objects.latest('id')
        self.assertRedirects(response, self.URLS_MAPS['user_pofile'])
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post_latest.text, form_data['text'])
        self.assertEqual(post_latest.group.id, form_data['group'])
        self.assertEqual(post_latest.image, f'posts/{self.uploaded.name}')

    def test_poste_edite(self):
        """Валидная форма создает запись в POST_EDIT."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }
        response = self.authorized_client_author.post(
            self.URLS_MAPS['post_edit'],
            data=form_data,
            follow=True
        )
        post_after_edit = Post.objects.get(pk=self.post.id)
        self.assertRedirects(response, self.URLS_MAPS['post_detail'])
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post_after_edit.text, form_data['text'])
        self.assertEqual(post_after_edit.group.id, form_data['group'])

    def test_labels_of_text_group(self):
        """Проверяем переопределенные labels."""
        labels = {
            "group": "Группа поста",
            "text": "Текст Вашего поста",
            "image": "Картинка к Вашему посту",
        }
        for key, data in labels.items():
            field_data = PostFormTests.form.fields[key].label
            with self.subTest(key=key):
                self.assertEquals(field_data, data)

    def test_help_text_of_text_group(self):
        """Проверяем переопределенный help_text."""
        help_texts = {
            "group": "Выбирите группу",
            "text": "Напишите Ваш пост",
            "image": "Загрузите картинку к Вашему поста",
        }
        for key, data in help_texts.items():
            field_data = PostFormTests.form.fields[key].help_text
            with self.subTest(key=key):
                self.assertEquals(field_data, data)

    def test_create_comment(self):
        """Валидная форма записи нового комментария"""
        comments_count = self.post.comments.count()
        form_data = {
            'text': 'Тестовый комменатрий',
        }
        response = self.authorized_client_author.post(
            self.URLS_MAPS['comments'],
            data=form_data,
            follow=True
        )
        comment_latest = Comment.objects.latest('id')
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment_latest.text, form_data['text'])
        self.assertRedirects(response, self.URLS_MAPS['post_detail'])
        self.assertIn(comment_latest, response.context['comments'])

    def test_create_comment(self):
        """Неавторизированный гость не сможет добавить коментарий """
        self.assertEqual(Comment.objects.count(), 0)
        form_data = {
            'text': 'Тестовый комменатрий',
        }
        self.guest_client.post(
            self.URLS_MAPS['comments'],
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 0)
