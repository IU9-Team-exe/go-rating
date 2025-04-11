# Рейтинговая система для онлайн-игр (на примере Го)

Этот проект реализует гибридную рейтинговую систему для десятков тысяч пользователей с использованием алгоритмов Glicko‑2, корректировок аномалий и дополнительных байесовских методов для новых игроков. Основное внимание уделено векторизованным вычислениям с использованием NumPy для повышения производительности при пакетном обновлении рейтингов. Рейтинговые данные сохраняются в базе данных с использованием SQLAlchemy.

## Структура проекта

```
project/
├── docs/                    # Обоснование выбора формул
│   ├── formulas.md
│   ├── formulas.pdf
│   └── formulas.tex
├── rating_system/
│   ├── __init__.py          # Инициализация пакета (может быть пустым)
│   ├── rating_system.py     # Основная логика обновления рейтингов (векторизованная версия)
│   └── db_handler.py        # Модуль для работы с базой данных (загрузка/обновление пользователей)
├── tests/
│   └── test_rating_system.py  # Тесты для модуля rating_system.py
└── README.md                
```

## Требования

- Python 3.7+
- NumPy
- SQLAlchemy
- (для тестов) unittest – включён в стандартную библиотеку

## Установка зависимостей

Создайте виртуальное окружение и установите необходимые пакеты:

```bash
python -m venv venv
source venv/bin/activate         # Для Linux/MacOS
venv\Scripts\activate            # Для Windows

pip install numpy sqlalchemy
```

## Настройка базы данных

По умолчанию используется SQLite база данных. В файле `rating_system/db_handler.py` можно изменить URL подключения, если требуется использовать другую СУБД:
```python
def get_engine(db_url='sqlite:///ratings.db'):
    return create_engine(db_url, echo=False)
```

Чтобы создать таблицы, выполните следующий скрипт (например, в интерактивном режиме Python):

```python
from rating_system.db_handler import get_engine, create_tables
engine = get_engine()
create_tables(engine)
```

## Запуск обновления рейтингов

Пример использования модуля `rating_system` (обновление рейтингов для набора пользователей):
1. Загрузите данные пользователей из БД через модуль `db_handler`.
2. Сформируйте массивы с рейтингами, RD и волатильностями.
3. Соберите массив сыгранных игр в виде матрицы (каждая строка: `[индекс игрока 1, индекс игрока 2, результат (от лица игрока 1)]`).
4. Вызовите функцию `update_ratings_vectorized`.

Пример кода (из файла `rating_system/example.py`):
```python
import numpy as np
from rating_system.rating_system import update_ratings_vectorized, START_RATING, START_RD, START_VOLATILITY

N_players = 5  # Например, 5 игроков или больше для реального случая
ratings = np.full(N_players, START_RATING, dtype=np.float64)
rds = np.full(N_players, START_RD, dtype=np.float64)
vols = np.full(N_players, START_VOLATILITY, dtype=np.float64)

# Массив игр: каждая строка [индекс игрока 1, индекс игрока 2, результат для игрока 1]
games = np.array([
    [0, 1, 1.0],
    [2, 3, 0.0],
    [3, 4, 0.5],
    [1, 2, 0.7]
])
new_ratings, new_rds, new_vols = update_ratings_vectorized(ratings, rds, vols, games)

# Результаты обновления можно сохранить в БД с помощью db_handler.bulk_update_users(...)
for i in range(N_players):
    print(f"Игрок {i}: Рейтинг = {new_ratings[i]:.2f}, RD = {new_rds[i]:.2f}, Волатильность = {new_vols[i]:.5f}")
```

## Запуск тестов

Тесты написаны с использованием модуля `unittest` и располагаются в каталоге `tests`.

Чтобы запустить тесты, выполните команду из корневого каталога проекта:
```bash
python -m unittest discover -s tests
```

## Развертывание и масштабирование

- **Пакетное обновление:** Векторизированный подход с NumPy позволяет эффективно обновлять рейтинги для десятков тысяч пользователей за один проход.
- **БД:** Для хранения рейтингов используется SQLAlchemy, что упрощает перенос данных между различными СУБД (SQLite, PostgreSQL, MySQL и т.д.).
- **Масштабирование:** При росте числа пользователей рекомендуется оптимизировать загрузку данных (например, батчевое извлечение данных) и обновление через bulk-операции в БД.

Дополнительные инструкции и академическое обоснование формул можно найти в `docs\`.
