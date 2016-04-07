import unittest

from dotabuff.query import DotaBuffQuery


class Test_DotaBuffQuery(unittest.TestCase):
    def setUp(self):
        self.query = DotaBuffQuery()

    def test_players_by_name_happymeds(self):
        players = self.query.get_players("HappyMeds")

        self.assertTrue(len(players) > 0)
        happymeds = players[0]
        self.assertEqual(happymeds.name, 'HappyMeds')
        self.assertEqual(happymeds.id, '163519691')
        self.assertTrue(len(happymeds.img_url) > 0)

    def test_players_by_name_atomic(self):
        players = self.query.get_players("Atomic")
        self.assertTrue(len(players) > 0)
        atomic = players[0]
        self.assertEqual(atomic.name, 'Atomic')
        self.assertEqual(atomic.id, '93734428')
        self.assertTrue(len(atomic.img_url) > 0)

    def test_random_players_with_empty_name(self):
        players = self.query.get_players("Atomic")
        self.assertTrue(len(players) > 0)

    def test_verified_players_first_if_any(self):
        players = self.query.get_players("Dendi")
        self.assertTrue(len(players) > 0)
        Dendi = players[0]
        self.assertEqual(Dendi.name, 'Na`Vi.Dendi')
        self.assertEqual(Dendi.id, '70388657')
        self.assertTrue(len(Dendi.img_url) > 0)

    def test_no_players_if_no_result(self):
        players = self.query.get_players(u"//////")
        self.assertFalse(players)
