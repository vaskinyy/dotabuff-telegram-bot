class DotaBuffPlayer(object):
    """
    Holds player's data
    """

    def __init__(self, name, id, img_url):
        self.name = name
        self.id = id
        self.img_url = img_url

    def __repr__(self):
        return u'{}-{}'.format(self.name, self.id)

    @property
    def telegram_article(self):
        return {'type': u'article',
                'id': self.id, u'title': self.name,
                'message_text': u'Dota player: {}'.format(self.name),
                'thumb_url': self.img_url}
