import unittest
import numpy as np
from rating_system.rating_system import update_ratings_vectorized, START_RATING, START_RD, START_VOLATILITY

class TestRatingSystem(unittest.TestCase):
    def test_update_ratings(self):
        """Проверка изменения рейтингов и волатильности при наличии сыгранных игр.
           Для RD допускается незначительное изменение, так как начальное значение RD (350)
           доминирует по сравнению с волатильностью."""
        N_players = 5
        ratings = np.full(N_players, START_RATING, dtype=np.float64)
        rds = np.full(N_players, START_RD, dtype=np.float64)
        vols = np.full(N_players, START_VOLATILITY, dtype=np.float64)
        games = np.array([
            [0, 1, 1.0],
            [2, 3, 0.0],
            [3, 4, 0.5],
            [1, 2, 0.7]
        ])
        new_ratings, new_rds, new_vols = update_ratings_vectorized(ratings, rds, vols, games)
        
        # Рейтинг должен измениться для как минимум одного игрока.
        self.assertFalse(np.allclose(new_ratings, ratings))
        # Волатильность должна измениться для как минимум одного игрока.
        self.assertFalse(np.allclose(new_vols, vols))
        # RD может измениться незначительно; допускаем разницу на уровне 1e-2.
        self.assertTrue(np.allclose(new_rds, rds, atol=1e-2))
    
    def test_no_games_no_change(self):
        """Если игр не было, параметры остаются неизменными."""
        N_players = 5
        ratings = np.full(N_players, START_RATING, dtype=np.float64)
        rds = np.full(N_players, START_RD, dtype=np.float64)
        vols = np.full(N_players, START_VOLATILITY, dtype=np.float64)
        games = np.empty((0, 3))
        new_ratings, new_rds, new_vols = update_ratings_vectorized(ratings, rds, vols, games)
        np.testing.assert_array_equal(new_ratings, ratings)
        np.testing.assert_array_equal(new_rds, rds)
        np.testing.assert_array_equal(new_vols, vols)

if __name__ == '__main__':
    unittest.main()
