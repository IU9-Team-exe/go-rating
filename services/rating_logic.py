import numpy as np
import math

TAU = 0.5
ALPHA = 10.0
THRESHOLD = 0.3

def g(rd: float) -> float:
    return 1.0 / math.sqrt(1.0 + (3.0 * rd**2) / (math.pi**2))

def E_elo(rating: float, opp_rating: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((opp_rating - rating) / 400.0))

def new_volatility_vectorized(a, rd, v, delta, tau=TAU, eps=1e-6, max_iter=100):
    x = a.copy()
    for _ in range(max_iter):
        exp_x = np.exp(x)
        denom = rd**2 + v + exp_x
        f = (exp_x * (delta**2 - rd**2 - v - exp_x) / (2.0 * denom**2)) - (x - a) / (tau**2)
        dfx = (exp_x * (delta**2 - rd**2 - v - exp_x) / (2.0 * denom**2)
              - exp_x * (exp_x + 2.0*(rd**2+v+exp_x)) / (2.0*denom**3)) - 1.0 / (tau**2)
        x_new = x - f / dfx
        if np.max(np.abs(x_new - x)) < eps:
            return np.exp(x_new / 2.0)
        x = x_new
    raise ValueError("Метод Ньютона не сошёлся")

def update_player_rating(rating, rd, volatility, opp_ratings, opp_rds, results):
    g_vals = 1.0 / np.sqrt(1.0 + (3.0 * opp_rds**2) / (math.pi**2))
    E_vals = 1.0 / (1.0 + np.exp(-g_vals * (rating - opp_ratings) / 400.0))
    delta_i = g_vals * (results - E_vals)
    v_inv = g_vals**2 * E_vals * (1 - E_vals)
    v_total = 1.0 / np.sum(v_inv) if np.sum(v_inv) > 0 else 0.0
    delta_total = v_total * np.sum(delta_i)

    E_elo_vals = 1.0 / (1.0 + 10.0 ** ((opp_ratings - rating) / 400.0))
    anomaly = np.where(np.abs(results - E_elo_vals) > THRESHOLD, ALPHA * (results - E_elo_vals), 0.0)
    total_anomaly = np.sum(anomaly)

    a = np.array([np.log(volatility**2)])
    rd_arr = np.array([rd])
    v_arr = np.array([v_total])
    delta_arr = np.array([delta_total])
    new_vol = new_volatility_vectorized(a, rd_arr, v_arr, delta_arr)[0]

    new_rd = math.sqrt(rd**2 + new_vol**2)
    new_rating = rating + g(new_rd) * delta_total + total_anomaly

    return new_rating, new_rd, new_vol
