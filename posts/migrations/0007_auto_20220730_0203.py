# Generated by Django 2.2.16 on 2022-07-29 22:03

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220730_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=sorl.thumbnail.fields.ImageField(blank=True, help_text='Картинка поста', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
