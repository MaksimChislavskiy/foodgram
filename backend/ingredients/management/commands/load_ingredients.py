import csv
import os

from django.core.management.base import BaseCommand
from ingredients.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из csv файла."""

    help = "loading data into db from scv file"

    def handle(self, *args, **options):
        # Получаем базовый каталог проекта (где находится manage.py)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(os.path.dirname(base_dir))
        file_path = os.path.join(project_root, 'data', 'ingredients.csv')

        with open(file_path, 'r', encoding='UTF-8') as file_data:
            reader = csv.reader(file_data)
            next(reader)  # Пропускаем заголовок, если он есть
            for row in reader:
                name = row[0]
                measurement_unit = row[1]
                ingredient = Ingredient(
                    name=name,
                    measurement_unit=measurement_unit,
                )
                ingredient.save()

        self.stdout.write(
            self.style.SUCCESS('Ingredient data uploaded successfully')
        )
