# praktikum_new_diplom

## Foodgram
 
Сервис для публикации рецептов. 
 
## Для запуска сервиса необходимо выполнить следующие действия
 

 Склонируйте репозиторий

 ```bash
git clone git@github.com:MrProfessorCat/api_yamdb.gitgit@github.com:MrProfessorCat/api_yamdb.git
 ```

 Перейдите в директорию infra.
 Выполните команду для сборки контейнеров

 ```bash
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py load_data
 ```

## Тестирование сервиса

Сервис доступен по адресу http://51.250.71.100/
### Учетные данные:
```bash
Администратор:
login: admin@mail.ru
pass: 123admin123

Тестовые пользователи:
login: ivan@mail.ru
pass: 123ivan123

login: alice@mail.ru
pass: 123alice123
```


![Статус workflow](https://github.com/MrProfessorCat/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
