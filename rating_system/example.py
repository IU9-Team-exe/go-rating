import numpy as np
from rating_system import update_ratings_vectorized, START_RATING, START_RD, START_VOLATILITY

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