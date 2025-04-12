import unittest
import numpy as np
from services.rating_logic import (
    g,
    E_elo,
    new_volatility_vectorized,
    update_player_rating
)

class TestRatingLogic(unittest.TestCase):

    def test_g_function(self):
        self.assertAlmostEqual(g(350), 1.0 / np.sqrt(1 + (3 * 350**2) / (np.pi**2)), places=6)
        self.assertGreater(g(50), g(350), msg="g(rd) должна уменьшаться при росте RD")

    def test_E_elo(self):
        self.assertAlmostEqual(E_elo(1500, 1500), 0.5)
        self.assertGreater(E_elo(1600, 1500), 0.5)
        self.assertLess(E_elo(1400, 1500), 0.5)

    def test_volatility_convergence(self):
        # Примерные данные
        a = np.array([np.log(0.06**2)])
        rd = np.array([350.0])
        v = np.array([0.06])
        delta = np.array([0.5])

        vol = new_volatility_vectorized(a, rd, v, delta)
        self.assertTrue(vol[0] > 0)
        self.assertIsInstance(vol[0], float)

    def test_update_player_rating_no_games(self):
        rating, rd, vol = 1500.0, 350.0, 0.06
        opp_ratings = np.array([])
        opp_rds = np.array([])
        results = np.array([])

        new_rating, new_rd, new_vol = update_player_rating(rating, rd, vol, opp_ratings, opp_rds, results)

        self.assertAlmostEqual(new_rating, rating, places=6)
        self.assertAlmostEqual(new_rd, rd, places=3)  # допускаем микроскопическое изменение
        self.assertAlmostEqual(new_vol, vol, places=6)


    def test_update_player_rating_basic_win(self):
        rating, rd, vol = 1500.0, 350.0, 0.06
        opp_ratings = np.array([1400.0])
        opp_rds = np.array([350.0])
        results = np.array([1.0])  # Победа

        new_rating, new_rd, new_vol = update_player_rating(rating, rd, vol, opp_ratings, opp_rds, results)
        self.assertGreater(new_rating, rating)
        self.assertIsInstance(new_rd, float)
        self.assertIsInstance(new_vol, float)

    def test_update_player_rating_with_mixed_results(self):
        rating, rd, vol = 1500.0, 350.0, 0.06
        opp_ratings = np.array([1520.0, 1480.0])
        opp_rds = np.array([330.0, 340.0])
        results = np.array([1.0, 0.0])  # Победа и поражение

        new_rating, new_rd, new_vol = update_player_rating(rating, rd, vol, opp_ratings, opp_rds, results)
        self.assertNotEqual(new_rating, rating)
        self.assertNotEqual(new_rd, rd)
        self.assertNotEqual(new_vol, vol)

if __name__ == '__main__':
    unittest.main()
