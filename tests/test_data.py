import unittest
from unittest.mock import patch
import pandas as pd
from fifa.data import DataStore


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = DataStore()

    def test_tournament_totals(self):
        standings = self.data.standings()
        self.assertEqual(len(standings), 32)
        self.assertEqual(standings.P.sum(), 128)
        self.assertEqual(standings.GF.sum(), 172)
        self.assertEqual(standings.GA.sum(), 172)
        self.assertTrue((standings.P == standings.W + standings.D + standings.L).all())
        self.assertEqual(standings.W.sum(), standings.L.sum())

    def test_shootouts_are_draws(self):
        argentina = self.data.standings().set_index('Team').loc['Argentina']
        self.assertEqual((argentina.W, argentina.D, argentina.L, argentina.Pts), (4, 2, 1, 14))

    def test_standings_tiebreaks(self):
        rows = self.data.standings().to_dict('records')
        expected = sorted(rows, key=lambda r: (-r['Pts'], -r['GD'], -r['GF'], r['Team']))
        self.assertEqual(rows, expected)

    def test_possession_counts_matches_once(self):
        counts = self.data.possession_outcomes()
        self.assertEqual(sum(counts.values()), 64)
        self.assertEqual(counts, {'Won': 22, 'Drew': 14, 'Lost': 25, 'Equal possession': 3})

    def test_pairing_works_after_row_shuffle(self):
        other = DataStore()
        other.team_matches = other.team_matches.sample(frac=1, random_state=7)
        pd.testing.assert_frame_equal(other.standings(), self.data.standings())
        self.assertEqual(other.possession_outcomes(), self.data.possession_outcomes())

    def test_matrices(self):
        for covariance in [False, True]:
            matrix = self.data.matrix(covariance)
            self.assertEqual(matrix.shape, (10, 10))
            pd.testing.assert_frame_equal(matrix, matrix.T)
        self.assertTrue((self.data.matrix().to_numpy().diagonal().round(10) == 1).all())

    def test_player_identity_and_missing_values(self):
        messi = self.data.player('Argentina', 'Lionel Messi')
        self.assertEqual(messi.goals, 7)
        with self.assertRaises(ValueError):
            self.data.player('France', 'Lionel Messi')
        self.assertEqual(len(self.data.players), 680)
        self.assertEqual(self.data.players.tackles.isna().sum(), 3)

    def test_no_reads_during_analysis(self):
        with patch('pandas.read_csv', side_effect=AssertionError('Unexpected reload')):
            self.data.standings()
            self.data.discipline()
            self.data.possession_outcomes()
            self.data.matrix()
            self.data.player('Argentina', 'Lionel Messi')

    def test_fairplay_formula(self):
        table = self.data.discipline()
        self.assertTrue((table.Score == table['Yellow cards'] + 3*table['Red cards']).all())


if __name__ == '__main__':
    unittest.main()
