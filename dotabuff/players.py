import logging
import dota2api

from dotabuff.config import STEAM_API_KEY
from dotabuff.utils import SpeedMeasure

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


class PlayersDbLoader(object):
    """
    Loads steam name-id mapping for Dota 2 players and stores it
    """
    def __init__(self):
        self.match_limit = None
        self.start_offset = 0
        self.api = dota2api.Initialise(STEAM_API_KEY)
        self.ids = {}
        self.speed_measure = SpeedMeasure()

    def update(self):
        tmp_ids = set()

        for match in self._matches():
            self.speed_measure.measure('matches')

            for player_id in self._player_ids(match):
                tmp_ids.add(player_id)
            self._dump_ids(tmp_ids)

        self._dump_ids(tmp_ids, forse=True)
        print len(self.ids)

    def _matches(self):
        total = self.start_offset or 0
        while True:
            try:
                matches = self.api.get_match_history_by_seq_num(total)
            except Exception as ex:
                logger.error(ex)
                continue
            loaded = len(matches['matches'])
            total += loaded
            for match in matches['matches']:
                yield match
            if loaded <= 0 or (self.match_limit and self.match_limit < total):
                break
        logger.info('Loaded {} matches'.format(total))
        print self.ids

    def _dump_ids(self, tmp_ids, forse=False):
        if len(tmp_ids) > 100 or forse:
            for steam_id, name in self._player_names(tmp_ids):
                self.ids[steam_id] = name
            self.speed_measure.measure('steam_ids', len(self.ids))
            tmp_ids.clear()

    def _player_ids(self, match):
        for player in match['players']:
            if 'account_id' in player:
                yield player['account_id']

    def _player_names(self, ids):
        try:
            players = self.api.get_player_summaries(ids)
            for player in players['players']:
                if 'steamid' in player and 'personaname' in player:
                    yield player['steamid'], player['personaname']
        except Exception as ex:
            logger.error(ex)

# DUMP TO DB
