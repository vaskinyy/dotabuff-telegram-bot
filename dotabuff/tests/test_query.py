import unittest

from dotabuff.config import VIP_PLAYERS_IDS
from dotabuff.query import DotaQuery


class Test_DotaBuffQuery(unittest.TestCase):
    def setUp(self):
        self.query = DotaQuery()

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
        self.assertEqual(atomic.id, '116845505')
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

    def test_no_players_last_date(self):
        players = self.query.get_players("Dendi")
        self.assertTrue(len(players) > 0)
        Dendi = players[0]
        self.assertTrue(len(Dendi.last_match_date) > 0)

    def test_matches_of_a_player(self):
        matches = self.query.get_matches("88271237")
        self.assertTrue(len(matches) > 0)
        match = matches[0]

        self.assertTrue(len(match.match_id) > 0)
        self.assertTrue(len(match.hero_name) > 0)
        self.assertTrue(len(match.match_result) > 0)
        self.assertTrue(len(match.match_age) > 0 and match.match_age_str.endswith('ago'))
        self.assertTrue(len(match.duration) > 0)
        self.assertTrue(len(match.kda) > 0 and '/' in match.kda)

    def test_vip_players(self):
        for vip_player_name in VIP_PLAYERS_IDS:
            players = self.query.get_players(vip_player_name)
            self.assertTrue(len(players) > 0)
            vip_player = players[0]
            self.assertEqual(vip_player.name.lower(), vip_player_name.lower())