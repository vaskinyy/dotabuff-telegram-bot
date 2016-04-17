import logging
import time
from collections import defaultdict

import dota2api

from dotabuff.config import STEAM_API_KEY

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


class SpeedMeasure(object):
    """
    Measures processing speed and report status
    """
    REPORT_EVERY = 1000

    def __init__(self):
        self.measures = defaultdict(int)
        self.update_counter = 0
        self.restart()

    def restart(self):
        self.start_time = time.time()

    def report(self):
        if self.update_counter > SpeedMeasure.REPORT_EVERY:
            self.update_counter = 0
            delta_time = time.time() - self.start_time
            for name, value in self.measures.items():
                speed = value / delta_time if delta_time else 'unknown'
                logger.info("Loaded {} {} in {} with speed {}".format(value, name, delta_time, speed))

    def measure(self, name, value=None):
        if value is not None:
            self.measures[name] = value
        else:
            self.measures[name] += 1

        self.update_counter += 1
        self.report()


def get_heroes_data():
    res = {}
    api = dota2api.Initialise(STEAM_API_KEY)
    heroes = api.get_heroes()
    for hero in heroes.get('heroes', []):
        print hero
        hero_id = hero.get('id', None)
        img_url = hero.get('url_small_portrait', None)
        localized_name = hero.get('localized_name', None)
        if hero_id and img_url and localized_name:
            res[hero_id] = localized_name, img_url
    return res
