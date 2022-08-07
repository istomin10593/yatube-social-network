## Улучшение проекта Yatube

## 📖 Contents

- [Overview](#-overview-)
  - [Features](#-how-powerful-your-social-dating-webapp-will-be-)
- [Installation](#-installation-)
- [License](#%EF%B8%8F-license-)
- [About Me](#-author-)
  - [Contact Me](#-contact-suggestion--feedback-)
  - [Hire Me](#-hire-me-at-your-company-)
  - [Offer me a cup of tea?](#-offer-me-a-cup-of-tea-or-tea-bags-)

В проект добавлены кастомные страницы ошибок:
 - 404 page_not_found
 - 403 permission_denied_view
Написан тест, проверяющий, что страница 404 отдает кастомный шаблон.
С помощью sorl-thumbnail выведены иллюстрации к постам:
 - в шаблон главной страницы,
 - в шаблон профайла автора,
 - в шаблон страницы группы,
 - на отдельную страницу поста.
Написаны тесты, которые проверяют:
при выводе поста с картинкой изображение передаётся в словаре context
 - на главную страницу,
 - на страницу профайла,
 - на страницу группы,
 - на отдельную страницу поста;
при отправке поста с картинкой через форму PostForm создаётся запись в базе данных;

Написана система комментирования записей. На странице поста под текстом записи выводится форма для отправки комментария, а ниже — список комментариев. Комментировать могут только авторизованные пользователи. Работоспособность модуля протестирована.

Список постов на главной странице сайта хранится в кэше и обновляется раз в 20 секунд.
Написан тест для проверки кеширования главной страницы. Логика теста: при удалении записи из базы, она остаётся в response.content главной страницы до тех пор, пока кэш не будет очищен принудительно.

Проект реализован на Django Framework.

## 🛠 Installation

  * Clone yatube-social-network from Github:

```
  git clone git@github.com:istomin10593/yatube-social-network.git
```

  * Create and activate virtual environment:

```
  py -3.7 -m venv venv
```

```
source venv/Scripts/activate
```

  * Install the packages according to the configuration file requirements.txt:

```
python -m pip install --upgrade pip
```

```
  pip install -r requirements.txt
```


  * Run server and project:

```
  python manage.py runserver
```

## 🤝 Hire Me At Your Company?

Are you building  Microservices or Web Services?

Do you think you might need a software engineer like me at your company? (with opportunity work remote or relocate) 👉 **[Welcome to my Linkedin](https://www.linkedin.com/in/artem-istomin-a5b192246)**!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin&logoColor=white&style=for-the-badge)](https://www.linkedin.com/artem-istomin-a5b192246/ "Artem Istomin LinkedIn") [![Whatsapp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/61426874095?text=I%27m%20looking%20for%20a%20software%20engineer%20like%20you)