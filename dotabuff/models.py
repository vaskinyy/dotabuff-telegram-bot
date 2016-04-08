class DotaBuffPlayer(object):
    """
    Holds player's data
    """

    def __init__(self, name, id, img_url):
        self.name = name
        self.id = id
        self.img_url = img_url
        self.matches = []

    def __repr__(self):
        return u'{}-{}'.format(self.name, self.id)

    @property
    def telegram_article(self):
        return {'type': u'article',
                'id': self.id, u'title': self.name,
                'message_text': u'Dota player: {}'.format(self.name),
                'thumb_url': self.img_url}


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
                                                          self.match_age, self.duration, self.kda)

        # @property
        # def telegram_article(self):
        #     return {'type': u'article',
        #             'id': self.id, u'title': self.name,
        #             'message_text': u'Dota player: {}'.format(self.name),
        #             'thumb_url': self.img_url}
