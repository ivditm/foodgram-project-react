# praktikum_new_diplom

сайт [https://finalivdit.ddns.net/]

### Пререквизиты:

- macOS Monterey 12.3
- Python 3.9
- pip
- csv
- PostgreSQL
- git

### Описание запуска проекта:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:ivditm/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

Импорт БД из csv:

```
python3 manage.py import_csv
```