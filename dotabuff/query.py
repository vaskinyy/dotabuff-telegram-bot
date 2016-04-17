import logging
import random
import requests
import dota2api
from dota2api.src.exceptions import APIError
from scrapy.selector import Selector

from dotabuff.config import DEFAULT_NAMES, DOTABUFF_URL, PLAYERS_CUTOFF, MATCHES_CUTOFF, VIP_PLAYERS_IDS, \
    STEAM_API_KEY, HEROES_DATA
from dotabuff.models import DotaPlayer, DotaMatch
from datetime import datetime, timedelta
from dotabuff.utils import get_heroes_data

logger = logging.getLogger(__name__)


class DotaQuery(object):
    """
    Requests Dota API servers for players, matches, etc.
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

        vip_id = self.vip_player_id(name)
        if vip_id:
            logger.info('Found vip player {} {}'.format(name, vip_id))
            name = vip_id

        players = []

        name = name or random.choice(DEFAULT_NAMES)
        player_search_url = DOTABUFF_URL + u'search?q={name}&commit=Search'.format(
            name=name.lower())

        resp = self._request(player_search_url)
        if not resp.ok:
            logger.error("Cannot get player {}".format(resp.status_code))
            return players

        player_divs = Selector(text=resp.content).css('.result-player')
        for num, player_div in enumerate(player_divs):
            if num >= PLAYERS_CUTOFF:
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

            last_match_date = player_div.css('.identity time').xpath('@datetime').extract_first(
                default=None)
            if not last_match_date:
                continue

            player = DotaPlayer(name=name, id=id, img_url=img_url,
                                last_match_date=last_match_date)

            # load matches
            player.matches = self.get_matches(player.id)

            players.append(player)

        return players

    def get_matches(self, player_id):
        """
        Query DotaBuff
        :param player_id:
        :return:
        """
        matches = []

        player_url = DOTABUFF_URL + u'/players/{id}'.format(id=player_id)
        resp = self._request(player_url)
        if not resp.ok:
            logger.error("Cannot get player {}".format(resp.status_code))
            return matches

        match_divs = Selector(text=resp.content).css('.performances-overview .r-row')

        for num, match_div in enumerate(match_divs):
            if num >= MATCHES_CUTOFF:
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
                '@datetime').extract_first(
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

            match = DotaMatch(match_id=id, hero_name=hero_name, match_result=match_result,
                              match_age=match_age, duration=duration, kda=kda,
                              hero_img=hero_img)
            matches.append(match)

        return matches

    def vip_player_id(self, name):
        name = name.lower()
        for vip_name in VIP_PLAYERS_IDS:
            if vip_name.lower() == name:
                return VIP_PLAYERS_IDS[vip_name]
        return None


class DotaSteamQuery(DotaQuery):
    """
    Requests Dota Steam API servers for players, matches, etc.
    """

    def __init__(self):
        super(DotaSteamQuery, self).__init__()
        self.api = dota2api.Initialise(STEAM_API_KEY)

    def get_matches(self, player_id):
        """
        Query Steam API
        :param player_id:
        :return:
        """

        matches = []
        if not player_id:
            return matches
        player_id = int(player_id)

        try:
            hist = self.api.get_match_history(player_id, matches_requested=MATCHES_CUTOFF)
        except APIError as er:
            return matches

        if 'matches' in hist:
            for num, match in enumerate(hist['matches']):
                if num >= MATCHES_CUTOFF:
                    break

                id = str(match.get('match_id', None))
                if not id:
                    continue

                match_datails = self.api.get_match_details(match_id=id)

                hero_id = None
                kda = None
                match_result = None
                for player in match_datails.get('players', []):
                    player_account_id = player.get('account_id', None)
                    if player_account_id and player_account_id == int(player_id):
                        hero_id = player.get('hero_id', None)
                        player_slot = player.get('player_slot', None)
                        # https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails#Player_Slot
                        is_radiant = bool(player_slot & (1 << 7))
                        radiant_wins = match_datails.get('radiant_win', None)
                        if is_radiant and radiant_wins:
                            match_result = "Won Match"
                        else:
                            match_result = "Lost Match"
                        kills = player.get('kills', None)
                        deaths = player.get('deaths', None)
                        assists = player.get('assists', None)
                        if kills and deaths and assists:
                            kda = '{}/{}/{}'.format(kills, deaths, assists)
                        break

                if not hero_id:
                    continue

                if hero_id not in HEROES_DATA:
                    continue

                hero_name = HEROES_DATA[hero_id][0]
                hero_img = HEROES_DATA[hero_id][1]

                start_time = match_datails.get('start_time', None)
                if not start_time:
                    continue
                match_age = '{:%Y-%m-%dT%H:%M:%S+00:00}'.format(datetime.fromtimestamp(start_time))

                if not match_age:
                    continue

                duration_seconds = match_datails.get('duration', None)
                if not duration_seconds:
                    continue
                delta = timedelta(seconds=duration_seconds)
                duration_date = datetime(1990, 1, 1) + delta
                if duration_date.hour:
                    duration = "{:%H:%M:%S}".format(duration_date)
                else:
                    duration = "{:%M:%S}".format(duration_date)

                match = DotaMatch(match_id=id, hero_name=hero_name, match_result=match_result,
                                  match_age=match_age, duration=duration, kda=kda,
                                  hero_img=hero_img)
                matches.append(match)

        return matches
