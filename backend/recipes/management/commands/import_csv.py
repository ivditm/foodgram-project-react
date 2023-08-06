import os
from pathlib import Path

import pandas as pd
import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

PROJECT_DIR = Path(settings.BASE_DIR).resolve().joinpath('data')
FILE_TO_OPEN = PROJECT_DIR / 'ingredients.csv'


load_dotenv()


dbname = os.getenv('POSTGRES_DB', 'final'),
user = os.getenv('POSTGRES_USER', 'final_user')
password = os.getenv('POSTGRES_PASSWORD', '')
if settings.DEBUG:
    host = os.getenv('HOST', '')
else:
    host = os.getenv('DB_HOST', '')


class Command(BaseCommand):
    help = 'загрузка в БД ингридиентов'

    def handle(self, *args, **options):
        with open(
            FILE_TO_OPEN, 'r', encoding='UTF-8'
        ) as file:
            conn = psycopg2.connect(dbname='final',
                                    host=host,
                                    port=5432,
                                    user=user,
                                    password=password)
            try:
                cursor = conn.cursor()
                data = pd.read_csv(file, names=['ingridient', 'values'])
                for index in range(len(data)):
                    cursor.execute(f'''
                                    insert into
                                            ingridients (name,
                                                         measurement_unit)
                                            values (
                                   '{data['ingridient'][index]}',
                                   '{data['values'][index]}'
                                   );
                                ''')
                cursor.close()
                conn.commit()
            finally:
                conn.close()
