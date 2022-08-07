from django.contrib.auth import get_user_model
from core.models import CreatedModel
from django.db import models

User = get_user_model()
STR_POST_COUNT = 15
STR_COMMENTS_COUNT = 15


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Назание группы',
        help_text='Укажите название группы',)
    slug = models.SlugField(unique=True)
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите группу',
        default='default description',)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Картинка поста',
    )

    def __str__(self):
        return self.text[:STR_POST_COUNT]

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )

    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )

    def __str__(self):
        return self.text[:STR_COMMENTS_COUNT]

    class Meta:
        ordering = ["-created"]
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name="unique followers"),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='do not selffollow'),
        ]
