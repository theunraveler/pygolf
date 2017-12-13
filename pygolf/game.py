from . import cards


class Game(object):

    CARDS_PER_PLAYER = 6

    def __init__(self, players=None):
        self.deck = cards.Deck()
        self.players = [] if players is None else players

    @property
    def is_terminal(self):
        return self.__terminal_player is not None

    @property
    def is_finished(self):
        return self.__terminal_player == self.__current_player

    @property
    def current_player(self):
        return self.players[self.__current_player]

    @property
    def terminal_player(self):
        if self.__terminal_player is None:
            return
        return self.players[self.__terminal_player]

    @property
    def result(self):
        if not self.is_finished:
            return (None, None)

        scores = {p: p.hand_score for p in self.players}
        best = min(scores.values())
        winners = [p for p, s in list(scores.items()) if s == best]
        return (scores, winners)

    def start(self):
        assert len(self.players) > 0, 'Game has no players'

        for __ in range(self.CARDS_PER_PLAYER):
            for player in self.players:
                player.cards.append(PlayerCard(self.deck.draw()))
        self.__current_player = 0
        self.__terminal_player = None
        self.last_discard = None
        return self

    def initial_flip(self, player, cards):
        cards = [int(card) for card in cards]

        assert len(cards) == 2, 'Must flip 2 cards'
        for card in cards:
            assert card >= 1 and card <= 6, '%s is not a valid card index' % card
        assert cards[0] != cards[1], 'Cards must be different'

        for card_index in cards:
            player.cards[card_index - 1].state = PlayerCard.STATE_FACE_UP

    def end_turn(self):
        if self.__should_terminate():
            self.__terminal_player = self.__current_player

        if self.__current_player == len(self.players) - 1:
            self.__current_player = 0
        else:
            self.__current_player = self.__current_player + 1

        return self.current_player

    def __should_terminate(self):
        return self.__terminal_player is None and any(
            all(card.state == card.STATE_FACE_UP for card in player.cards)
            for player in self.players
        )


class DrawAction(object):

    ACTION_TAKE = 1
    ACTION_DRAW = 2

    def __init__(self, game, action):
        self.game = game
        self.action = int(action)

    def __call__(self):
        if self.action == self.ACTION_TAKE:
            return self.game.last_discard
        return self.game.deck.draw()


class CardAction(object):

    ACTION_DISCARD = 0
    ACTIONS = {
        1: 'Replace the top left card',
        2: 'Replace the top right card',
        3: 'Replace the middle left card',
        4: 'Replace the middle right card',
        5: 'Replace the bottom left card',
        6: 'Replace the bottom right card',
        ACTION_DISCARD: 'Discard',
    }

    def __init__(self, game, action):
        self.game = game
        self.action = int(action)

    def __call__(self, card):
        assert self.action in self.ACTIONS.keys(), 'Action is invalid'

        if self.action == self.ACTION_DISCARD:
            self.game.last_discard = card
        else:
            self.game.last_discard = self.game.current_player.cards[
                self.action - 1
            ].card
            self.game.current_player.cards[self.action - 1] = PlayerCard(
                card=card,
                state=PlayerCard.STATE_FACE_UP
            )


class PlayerCard(object):

    STATE_FACE_DOWN = 0
    STATE_FACE_UP = 1
    STATES = [STATE_FACE_DOWN, STATE_FACE_UP]
    STATE_DISPLAYS = {
        STATE_FACE_DOWN: 'face down',
        STATE_FACE_UP: 'face up'
    }

    def __init__(self, card, state=STATE_FACE_DOWN):
        assert state in self.STATES, 'State is invalid'
        self.card = card
        self.state = state

    def get_state_display(self):
        return self.STATE_DISPLAYS[self.state]

    def __str__(self):
        if self.state == self.STATE_FACE_DOWN:
            return ''
        else:
            return str(self.card)

    def __repr__(self):
        return '%s (%s)' % (repr(self.card), self.state)


class Player(object):

    def __init__(self, name):
        self.name = name
        self.cards = []

    @property
    def cards_in_rows(self):
        return [self.cards[i:i + 2] for i in range(0, Game.CARDS_PER_PLAYER, 2)]

    @property
    def hand_score(self):
        score = 0

        if len(self.cards) == 0:
            return score

        for row in self.cards_in_rows:
            if row[0].card.rank == row[1].card.rank:
                continue
            score += row[0].card.points
            score += row[1].card.points

        return score

    def __str__(self):
        return self.name
