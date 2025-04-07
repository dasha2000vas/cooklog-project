# COOKLOG

## Описание
<h4>CookLog - это платформа, позволяющая делиться рецептами, сохранять их, сортировать и подсчитывать ингредиенты. Здесь каждый сможет найти что-то на свой вкус.</h4>

Доступны следующие функции: регистрация и авторизация на сайте, создание и редактирование рецепта, добавление его в избранное и список покупок, фильтрация по тегам и подписка на другого пользователя.

---

## Как скачать и запустить проект:
1. **Устанавливаем Docker и Docker Compose:**
```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```

2. **Клонируем репозиторий и переходим в папку с файлом docker-compose.yml:**
```bash
git clone git@github.com:dasha2000vas/cooklog-project-react.git
cd infra
```

3. **Создаем файл .env для хранения секретов:**
```bash
sudo nano .env
```
В файле указываем:
```python
POSTGRES_DB=название_базы_данных
POSTGRES_USER=имя_пользователя
POSTGRES_PASSWORD=пароль
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=сгенерированный_секретный_ключ
DEBUG=False/True
ALLOWED_HOSTS=разрешенные_хосты
```

Сгенерировать ключ можно, например, [на этом сайте](https://djecrety.ir/).

4. **Запускаем контейнеры и сеть, связывающую их:**
```bash
sudo docker compose up
```

5. **Создаем миграции, собираем статику бэкенда и копируем ее:**
```bash
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```

Заполняем базу данных ингредиентами:
```bash
sudo docker compose exec backend python manage.py load_data
```

6. **Переходим по ссылке https://localhost:5000/**

---

## Технический стек:
* Django3.2.3
* djangorestframework3.12.4
* djoser2.1.0
* Pillow9.0.0
* gunicorn20.1.0

---

## Автор:

* Василевская Дарья
* GitHub: https://github.com/dasha2000vas
* Телеграм: https://t.me/vasdascha
* Почта: vasilevsckaya.dascha@yandex.ru

---

## Примечание:

>**Чтобы ознакомиться с сайтом ближе, [запустите проект на вашем компьютере](#как-скачать-и-запустить-проект) и перейдите по ссылке http://158.160.72.58:5000/. Документацию по проекту можно будет посмотреть после его запуска по адресу http://158.160.72.58:5000/api/docs/**
