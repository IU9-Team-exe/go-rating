import numpy as np
import math

# Системные константы
START_RATING = 1500.0
START_RD = 350.0
START_VOLATILITY = 0.06
ALPHA = 10.0            # коэффициент для аномальной коррекции
TAU = 0.5               # системный параметр для волатильности
THRESHOLD = 0.3         # порог для применения аномальной поправки

def g(rd):
    """Вычисление функции g(RD) по системе Glicko-2."""
    return 1.0 / np.sqrt(1.0 + (3.0 * rd**2) / (np.pi**2))

def E_rating(rating, opp_rating, opp_rd):
    """Вычисление ожидаемого результата (expected score) с учетом неопределенности оппонента."""
    g_opp = g(opp_rd)
    return 1.0 / (1.0 + np.exp(-g_opp * (rating - opp_rating) / 400.0))

def E_elo(rating, opp_rating):
    """Классический ожидаемый результат по формуле Elo."""
    return 1.0 / (1.0 + 10.0**((opp_rating - rating) / 400.0))

def new_volatility_vectorized(a, rd, v, delta, tau=TAU, eps=1e-6, max_iter=100):
    """
    Векторизованный метод Ньютона для вычисления новой волатильности.
    
    :param a: вектор log(old_vol^2)
    :param rd: вектор текущих значений RD для игроков
    :param v: вектор вычисленных дисперсий для каждого игрока
    :param delta: вектор дельт для обновления рейтинга
    :param tau: параметр системы (по умолчанию TAU)
    :param eps: порог сходимости
    :param max_iter: максимальное число итераций
    :return: вектор новых значений волатильности
    """
    x = a.copy()
    for _ in range(max_iter):
        exp_x = np.exp(x)
        denom = (rd**2 + v + exp_x)
        f = (exp_x * (delta**2 - rd**2 - v - exp_x) / (2.0 * (denom**2))) - (x - a) / (tau**2)
        dfx = (exp_x * (delta**2 - rd**2 - v - exp_x) / (2.0 * (denom**2)) -
               exp_x * (exp_x + 2.0*(rd**2+v+exp_x)) / (2.0*(denom**3))) - 1.0 / (tau**2)
        x_new = x - f / dfx
        if np.max(np.abs(x_new - x)) < eps:
            x = x_new
            break
        x = x_new
    else:
        raise ValueError("Метод Ньютона не сошёлся для некоторых элементов")
    return np.exp(x / 2.0)

def update_ratings_vectorized(ratings, rds, vols, games, tau=TAU, alpha=ALPHA, threshold=THRESHOLD):
    """
    Векторизованное обновление рейтингов для множества игр за один рейтинговый период.
    
    :param ratings: np.array с текущими рейтингами игроков, форма (N,)
    :param rds: np.array с текущими значениями RD, форма (N,)
    :param vols: np.array с волатильностями, форма (N,)
    :param games: np.array формы (M, 3), где каждая строка: [индекс игрока 1, индекс игрока 2, результат (от лица игрока 1)]
    :param tau, alpha, threshold: параметры системы
    :return: обновлённые массивы: (new_ratings, new_rds, new_vols)
    """
    # Преобразуем входной массив игр (если это не np.array)
    games = np.array(games)
    i_indices = games[:, 0].astype(np.int64)
    j_indices = games[:, 1].astype(np.int64)
    results_i = games[:, 2].astype(np.float64)
    results_j = 1.0 - results_i  # результат с точки зрения игрока j

    # Для игрока i (первого игрока)
    rating_i = ratings[i_indices]
    rating_j = ratings[j_indices]
    rd_j = rds[j_indices]
    g_j = g(rd_j)
    E_i = 1.0 / (1.0 + np.exp(-g_j * (rating_i - rating_j) / 400.0))
    v_inv_i = g_j**2 * E_i * (1.0 - E_i)
    delta_contrib_i = g_j * (results_i - E_i)

    # Вычисляем аномальную поправку по классической формуле Elo
    E_elo_i = E_elo(rating_i, rating_j)
    anomaly_i = np.where(np.abs(results_i - E_elo_i) > threshold, alpha * (results_i - E_elo_i), 0.0)

    # Для игрока j (второго игрока)
    rating_j_2 = ratings[j_indices]
    rating_i_2 = ratings[i_indices]
    rd_i = rds[i_indices]
    g_i = g(rd_i)
    E_j = 1.0 / (1.0 + np.exp(-g_i * (rating_j_2 - rating_i_2) / 400.0))
    v_inv_j = g_i**2 * E_j * (1.0 - E_j)
    delta_contrib_j = g_i * (results_j - E_j)

    E_elo_j = E_elo(rating_j_2, rating_i_2)
    anomaly_j = np.where(np.abs(results_j - E_elo_j) > threshold, alpha * (results_j - E_elo_j), 0.0)

    # Агрегируем вклады по каждому игроку
    N = ratings.shape[0]
    sum_v_inv = np.zeros(N, dtype=np.float64)
    sum_delta = np.zeros(N, dtype=np.float64)
    sum_anom = np.zeros(N, dtype=np.float64)

    np.add.at(sum_v_inv, i_indices, v_inv_i)
    np.add.at(sum_delta, i_indices, delta_contrib_i)
    np.add.at(sum_anom, i_indices, anomaly_i)

    np.add.at(sum_v_inv, j_indices, v_inv_j)
    np.add.at(sum_delta, j_indices, delta_contrib_j)
    np.add.at(sum_anom, j_indices, anomaly_j)

    played = sum_v_inv > 0
    v = np.zeros_like(ratings)
    delta = np.zeros_like(ratings)
    v[played] = 1.0 / sum_v_inv[played]
    delta[played] = v[played] * sum_delta[played]

    # Расчёт новой волатильности
    new_vols = vols.copy()
    if np.any(played):
        a = np.log(vols[played]**2)
        new_vols[played] = new_volatility_vectorized(a, rds[played], v[played], delta[played], tau=tau)

    # Обновление RD и рейтинга
    new_rds = rds.copy()
    new_ratings = ratings.copy()
    if np.any(played):
        new_rds[played] = np.sqrt(rds[played]**2 + new_vols[played]**2)
        new_ratings[played] = ratings[played] + g(new_rds[played]) * delta[played] + sum_anom[played]

    return new_ratings, new_rds, new_vols

