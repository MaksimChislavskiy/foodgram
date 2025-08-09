#!/bin/bash

# Определяем команду python в зависимости от ОС
case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

# Находим manage.py
PATH_TO_MANAGE_PY=$(find ../ -name "manage.py" -not -path "*/env" -not -path "*/venv")
BASE_DIR="$(dirname "${PATH_TO_MANAGE_PY}")"
cd $BASE_DIR || exit

# Проверяем успешность перехода
status=$?
if [ $status -ne 0 ]; then
    echo "Ошибка: не удалось найти manage.py или перейти в директорию проекта"
    exit $status
fi

# Выполняем очистку ингредиентов
echo "from ingredients.models import Ingredient; \
     count, _ = Ingredient.objects.all().delete(); \
     print(f'Удалено {count} ингредиентов') if count else print('Нет ингредиентов для удаления'); \
     exit(0)" | $python manage.py shell

status=$?
if [ $status -ne 0 ]; then
    echo "Ошибка при удалении ингредиентов"
    exit $status
fi

echo "Таблица ингредиентов успешно очищена"