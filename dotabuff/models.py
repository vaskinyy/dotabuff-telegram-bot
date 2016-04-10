import datetime
import os
import time

import ago
from cached_property import cached_property

os.environ['TZ'] = 'UTC'
time.tzset()


class DotaBuffPlayer(object):
    """
    Holds player's data
    """

    def __init__(self, name, id, img_url, last_match_date=None):
        self.name = name
        self.id = id
        self.img_url = img_url
        self.last_match_date = last_match_date
        self.matches = []

    def __repr__(self):
        return u'{}-{}'.format(self.name, self.id)

    @property
    def telegram_article(self):
        article = {'type': u'article',
                   'id': self.id[:8],
                   'title': self._message_preview,
                   'message_text': self._message_text,
                   'thumb_url': self.img_url,
                   'description': self._message_description,
                   'parse_mode': 'Markdown',
                   }
        return article

    @property
    def _message_preview(self):
        return self.name

    @property
    def _message_text(self):
        head = u'''
        *{name}*'s last matches
        '''.format(name=self.name, img_url=self.img_url)
        matches = u''
        for match in self.matches:
            matches += u'''
*{match_result}* {match_age} as {hero_name}
KDA: _{kda}_. Duration: {duration}
[Details]({match_url})
---'''.format(match_result=match.match_result.strip(), match_age=match.match_age_str,
              hero_name=match.hero_name, hero_icon=match.hero_img, kda=match.kda,
              duration=match.duration, match_url=match.match_url)
        foot = u'''
[All matches]({player_url})'''.format(player_url=self.player_url)

        return head + matches + foot

    @property
    def _message_description(self):
        res = self.last_match_date_str
        res += '\n'
        if self.matches:
            res += 'as ' + self.matches[0].hero_name
        return res

    @cached_property
    def last_match_date_str(self):
        return str_date_to_age(self.last_match_date)

    @cached_property
    def player_url(self):
        return u'http://www.dotabuff.com/players/{}'.format(self.id)


class DotaBuffMatch(object):
    """
    Holds match data
    """

    def __init__(self, match_id, hero_name, match_result, match_age, duration, kda, hero_img=None):
        self.match_id = match_id
        self.hero_name = hero_name
        self.match_result = match_result
        self.match_age = match_age
        self.duration = duration
        self.kda = kda
        self.hero_img = hero_img

    def __repr__(self):
        return u'{}. {} {}. Duration: {}. KDA: {}'.format(self.hero_name, self.match_result,
                                                          self.match_age_str, self.duration,
                                                          self.kda)

    @cached_property
    def match_age_str(self):
        return str_date_to_age(self.match_age)

    @cached_property
    def match_url(self):
        return u'http://www.dotabuff.com/matches/{}'.format(self.match_id)


def str_date_to_age(str_date):
    try:
        parsed_date = datetime.datetime.strptime(str_date[:-len('+00:00')], "%Y-%m-%dT%H:%M:%S")
        res = ago.human(parsed_date, precision=1)
        if not res:
            return str_date
        return res
    except BaseException:
        pass
    return str_date
