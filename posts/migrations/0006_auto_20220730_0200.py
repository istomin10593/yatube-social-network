# Generated by Django 2.2.16 on 2022-07-29 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20220729_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Картинка поста', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]