from django.forms import ModelChoiceField, ModelForm, Textarea, ValidationError

from .models import Comment, Group, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        group = ModelChoiceField(queryset=Post.objects.all(),
                                 required=False, to_field_name="group")
        widgets = {
            "text": Textarea(),
        }

        labels = {
            "group": "Группа поста",
            "text": "Текст Вашего поста",
            "image": "Картинка к Вашему посту",
        }

        help_texts = {
            "group": "Выбирите группу",
            "text": "Напишите Ваш пост",
            "image": "Загрузите картинку к Вашему поста",
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise ValidationError('Обязательно поле. Пожалуйста заполните')
        return data

    def cleaned_group(self):
        group = self.cleaned_data['group']
        if group and Group.objects.filter(pk=group).count() == 0:
            raise ValidationError('Группы не существует')
        return group


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            "text": Textarea(),
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise ValidationError('Обязательно поле. Пожалуйста заполните')
        return data
