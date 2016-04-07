import random
import logging
import requests
from scrapy.selector import Selector
from dotabuff.models import DotaBuffPlayer

logger = logging.getLogger(__name__)


class DotaBuffQuery(object):
    """
    Requests DotaBuff server for players, matches, etc.
    """
    URL = 'http://www.dotabuff.com/'
    DEFAULT_NAMES = ['Puppey', 'Dendi', 'Atomic', 'HappyMeds']
    PLAYERS_CUTOFF = 10

    def get_players(self, name):
        players = []
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/27.0.1453.94 Safari/537.36'}

        name = name or random.select(DotaBuffQuery.DEFAULT_NAMES)

        player_url = DotaBuffQuery.URL + u'search?q={name}&commit=Search'.format(
            name=name.lower())

        resp = requests.get(player_url, headers=headers)
        if not resp.ok:
            logger.error("Cannnot get player {}".format(resp.status_code))
            return players

        player_divs = Selector(text=resp.content).css('.result-player')
        for num, player_div in enumerate(player_divs):
            if num > DotaBuffQuery.PLAYERS_CUTOFF:
                break

            name = player_div.xpath('@data-filter-value').extract_first(default=None)

            if not name:
                continue

            id = player_div.css('.inner').xpath('@data-player-id').extract_first(default=None)
            if not id:
                id = player_div.css('.inner').xpath('@data-link-to').extract_first(default=None)
                if not id:
                    continue
                id = id[len('/players/'):]
            img_url = player_div.css('img').xpath('@src').extract_first(default=None)

            if not img_url:
                continue

            # TODO add last match time

            player = DotaBuffPlayer(name=name, id=id, img_url=img_url)
            players.append(player)

        return players
