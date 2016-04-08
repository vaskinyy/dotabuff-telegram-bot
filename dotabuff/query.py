import logging
import random
import requests
from scrapy.selector import Selector

from dotabuff.config import DEFAULT_NAMES, URL, PLAYERS_CUTOFF, MATCHES_CUTOFF
from dotabuff.models import DotaBuffPlayer, DotaBuffMatch

logger = logging.getLogger(__name__)


class DotaBuffQuery(object):
    """
    Requests DotaBuff server for players, matches, etc.
    """

    def _request(self, url):
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/27.0.1453.94 Safari/537.36'}

        resp = requests.get(url, headers=headers)
        return resp

    def get_players(self, name):
        # TODO cache players
        players = []

        name = name or random.choice(DEFAULT_NAMES)
        player_search_url = URL + u'search?q={name}&commit=Search'.format(
            name=name.lower())

        resp = self._request(player_search_url)
        if not resp.ok:
            logger.error("Cannot get player {}".format(resp.status_code))
            return players

        player_divs = Selector(text=resp.content).css('.result-player')
        for num, player_div in enumerate(player_divs):
            if num > PLAYERS_CUTOFF:
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
            last_match_date = player_div.css('.identity time').xpath('text()').extract_first(
                default=None)

            player = DotaBuffPlayer(name=name, id=id, img_url=img_url,
                                    last_match_date=last_match_date)
            players.append(player)

        return players

    def get_matches(self, player_id):
        matches = []

        player_url = URL + u'/players/{id}'.format(id=player_id)
        resp = self._request(player_url)
        if not resp.ok:
            logger.error("Cannot get player {}".format(resp.status_code))
            return matches

        match_divs = Selector(text=resp.content).css('.performances-overview .r-row')

        for num, match_div in enumerate(match_divs):
            if num > MATCHES_CUTOFF:
                break

            id = match_div.xpath('@data-link-to').extract_first(default=None)
            if not id:
                continue
            id = id[len('/matches/'):]

            icon_text_container = match_div.css('.r-icon-text')
            hero_img = icon_text_container.css('.r-body img').xpath('@src').extract_first(
                default=None)
            if hero_img and hero_img.startswith('/'):
                hero_img = 'http://dotabuff.com' + hero_img

            hero_name = icon_text_container.css('.r-body > a').xpath('text()').extract_first(
                default=None)
            if not hero_name:
                continue

            match_result_container = match_div.css('.r-match-result')
            match_result = match_result_container.css('.r-body > a').xpath('text()').extract_first(
                default=None)
            if not match_result:
                continue

            match_age = match_result_container.css('.r-body time').xpath(
                'text()').extract_first(
                default=None)
            if not match_age:
                continue

            duration = match_div.css('.r-duration .r-body').xpath(
                'text()').extract_first(
                default=None)
            if not duration:
                continue

            kda_span = match_div.css('.r-line-graph .r-body .kda-record')

            kda = '/'.join(kda_span.css('.value').xpath('text()').extract())

            if not kda:
                continue

            match = DotaBuffMatch(match_id=id, hero_name=hero_name, match_result=match_result,
                                  match_age=match_age, duration=duration, kda=kda,
                                  hero_img=hero_img)
            matches.append(match)

        return matches
