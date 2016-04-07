import telepot

from dotabuff.query import DotaBuffQuery


class InlineHandler(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(InlineHandler, self).__init__(seed_tuple, timeout,
                                            flavors=['inline_query', 'chosen_inline_result'])
        self._answerer = telepot.helper.Answerer(self.bot)
        self.query = DotaBuffQuery()

    def on_inline_query(self, msg):
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print(self.id, ':', 'Inline Query:', query_id, from_id, query_string)

        def compute_answer():
            players = self.query.get_players(query_string)
            articles = []
            for player in players:
                article = {'type': u'article',
                           'id': player.id, u'title': player.name,
                           'message_text': u'Dota player: {}'.format(player.name),
                           'thumb_url': player.img_url}
                articles.append(article)

            return articles

        self._answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print(self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)
