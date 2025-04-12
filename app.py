from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import numpy as np

from rating_system.db_handler import get_engine, create_tables, get_session, get_all_users, bulk_update_users, User
from rating_system.rating_system import update_ratings_vectorized, START_RATING, START_RD, START_VOLATILITY

# Создаем объект FastAPI
app = FastAPI(title="Go Rating System API")

# Настраиваем базу данных
engine = get_engine()  # по умолчанию SQLite, можно указать другой URL
create_tables(engine)

# Функция для получения сессии БД через зависимость
def get_db_session():
    session = get_session(engine)
    try:
        yield session
    finally:
        session.close()

# Pydantic модели для запросов и ответов
class GameResult(BaseModel):
    player1_id: int
    player2_id: int
    result: float  # 1.0 - победа player1, 0.5 - ничья, 0.0 - поражение player1

class UserOut(BaseModel):
    id: int
    rating: float
    rd: float
    volatility: float

    class Config:
        orm_mode = True

@app.get("/users", response_model=List[UserOut])
def get_users(session=Depends(get_db_session)):
    """
    Возвращает список всех пользователей с текущими значениями рейтингов, RD и волатильности.
    """
    users = get_all_users(session)
    return users

@app.post("/ratings/update")
def update_ratings(games: List[GameResult], session=Depends(get_db_session)):
    """
    Пересчет рейтингов по итогам партий. Получает список игр, где каждая игра задается
    идентификаторами игроков и результатом (от лица первого игрока).
    
    Алгоритм:
    
    1. Загружаются все пользователи из БД.
    2. Формируются массивы рейтингов, RD и волатильности с одинаковым порядком.
    3. Для каждой игры определяется индекс игрока в массиве на основе сопоставления с ID.
    4. Вызывается функция update_ratings_vectorized для пакетного обновления.
    5. Результаты записываются обратно в БД.
    """
    # Загружаем всех пользователей
    users = get_all_users(session)
    if not users:
        raise HTTPException(status_code=404, detail="Нет пользователей в базе данных.")

    # Для обеспечения стабильного соответствия формируем список пользователей, отсортированный по id
    users_sorted = sorted(users, key=lambda u: u.id)
    # Построим мэппинг: user_id -> индекс в массиве
    id_to_index = {user.id: idx for idx, user in enumerate(users_sorted)}
    N = len(users_sorted)

    # Формируем numpy-массивы для рейтингов, RD и волатильности
    ratings = np.full(N, START_RATING, dtype=np.float64)
    rds     = np.full(N, START_RD, dtype=np.float64)
    vols    = np.full(N, START_VOLATILITY, dtype=np.float64)
    
    # Если для некоторых пользователей уже установлены значения (из БД), используем их
    for idx, user in enumerate(users_sorted):
        ratings[idx] = user.rating
        rds[idx]     = user.rd
        vols[idx]    = user.volatility

    # Формируем массив игр для передачи в update_ratings_vectorized
    games_list = []
    for game in games:
        # Проверяем, что оба игрока присутствуют в базе
        if game.player1_id not in id_to_index or game.player2_id not in id_to_index:
            raise HTTPException(status_code=404, detail=f"Один из игроков {game.player1_id} или {game.player2_id} не найден.")
        idx1 = id_to_index[game.player1_id]
        idx2 = id_to_index[game.player2_id]
        # Каждая игра задается как [индекс игрока1, индекс игрока2, результат (от лица первого игрока)]
        games_list.append([idx1, idx2, game.result])
    games_np = np.array(games_list, dtype=np.float64)

    # Проводим векторизированное обновление
    new_ratings, new_rds, new_vols = update_ratings_vectorized(ratings, rds, vols, games_np)

    # Обновляем БД. Порядок обновления соответствует пользователям в users_sorted,
    # поэтому извлекаем их id в нужном порядке.
    ids = [user.id for user in users_sorted]
    bulk_update_users(session, ids, new_ratings, new_rds, new_vols)

    return {"detail": "Рейтинги успешно обновлены."}
