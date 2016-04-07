

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