from . import cards


class Game(object):

    ROUNDS_PER_GAME = 9

    def __init__(self, players):
        self.players = players
        self.rounds = []

    def begin_round(self):
        self.rounds.append(Round(self))

    @property
    def current_round(self):
        return self.rounds[-1]

    @property
    def result(self):
        scores = [0] * len(self.players)

        for round_ in self.rounds:
            for index, score in enumerate(round_.result):
                scores[index] += score

        best = min(scores)
        winners = [self.players[index] for index, score in enumerate(scores) if score == best]
        return (scores, winners)


class Round(object):

    CARDS_PER_PLAYER = 6

    def __init__(self, game):
        self.deck = cards.Deck()
        self.hands = [Hand(player) for player in game.players]
        for __ in range(self.CARDS_PER_PLAYER):
            for hand in self.hands:
                hand.cards.append(HandCard(self.deck.draw()))
        self.__current_hand = 0
        self.__terminal_hand = None
        self.last_discard = self.deck.draw()

    @property
    def is_terminal(self):
        """
        Whether any of the players has flipped all of their cards. This will be
        `True` during the last go-around after a player has flipped all of their
        cards.
        """
        return self.__terminal_hand is not None

    @property
    def is_finished(self):
        """
        Whether the round is completely over (i.e. is terminal and all other
        players have taken their last turn).
        """
        return self.__terminal_hand == self.__current_hand

    @property
    def current_hand(self):
        return self.hands[self.__current_hand]

    @property
    def terminal_hand(self):
        """
        Returns the `Hand` object that was the first to have flipped over all of
        their cards, or `None` if none has yet.
        """
        if self.__terminal_hand is None:
            return
        return self.hands[self.__terminal_hand]

    @property
    def result(self):
        """
        Returns a list of scores in the order of the game's players.
        """
        scores = [hand.score for hand in self.hands]

        for index, hand in enumerate(self.hands):
            # Four corners.
            if hand.is_four_corners:
                for j in range(len(self.hands)):
                    if j == index:
                        continue
                    scores[j] += 30

        return scores

    def end_turn(self):
        """
        Advances the round to the next player. Returns the new current `Hand`
        object.
        """
        if self.__should_terminate():
            self.__terminal_hand = self.__current_hand

        if self.__current_hand == len(self.hands) - 1:
            self.__current_hand = 0
        else:
            self.__current_hand = self.__current_hand + 1

        return self.current_hand

    def __should_terminate(self):
        return self.__terminal_hand is None and any(
            all(card.state == card.STATE_FACE_UP for card in hand.cards)
            for hand in self.hands
        )


class FlipAction(object):
    """
    Represents the initial card flip that happens at the beginning of the round.
    """

    def __init__(self, hand):
        self.hand = hand

    def __call__(self, card_1, card_2):
        card_1 = int(card_1)
        card_2 = int(card_2)

        assert card_1 >= 1 and card_1 <= 6, '%s is not a valid card index' % card_1
        assert card_2 >= 1 and card_2 <= 6, '%s is not a valid card index' % card_2
        assert card_1 != card_2, 'Cards must be different'

        self.hand.cards[card_1 - 1].flip()
        self.hand.cards[card_2 - 1].flip()


class DrawAction(object):
    """
    Represents the act of either taking the top card of the discard pile or
    drawing a new card.
    """

    ACTION_TAKE = 1
    ACTION_DRAW = 2

    def __init__(self, round_, action):
        self.round = round_
        self.action = int(action)

    def __call__(self):
        if self.action == self.ACTION_TAKE:
            return self.round.last_discard
        return self.round.deck.draw()


class CardAction(object):
    """
    Represents an action taken with a card.
    """

    ACTION_DISCARD = 0
    TAKE_ACTIONS = {
        1: 'Replace the top left card',
        2: 'Replace the top right card',
        3: 'Replace the middle left card',
        4: 'Replace the middle right card',
        5: 'Replace the bottom left card',
        6: 'Replace the bottom right card',
    }
    DRAW_ACTIONS = TAKE_ACTIONS.copy()
    DRAW_ACTIONS.update({
        ACTION_DISCARD: 'Discard',
    })

    def __init__(self, round_, action):
        self.round = round_
        self.action = int(action)

    def __call__(self, card):
        assert self.action in self.DRAW_ACTIONS.keys(), 'Action is invalid'

        if self.action == self.ACTION_DISCARD:
            self.round.last_discard = card
        else:
            self.round.last_discard = self.round.current_hand.cards[
                self.action - 1
            ].card
            self.round.current_hand.cards[self.action - 1] = HandCard(
                card=card,
                state=HandCard.STATE_FACE_UP
            )


class Hand(object):
    """
    Represents a hand of cards for a player.
    """

    def __init__(self, player):
        self.player = player
        self.cards = []

    @property
    def card_groups(self):
        """
        Returns the cards in groups of 2, suitable for displaying, calculating
        the score, etc.
        """
        return [self.cards[i:i + 2] for i in range(0, len(self.cards), 2)]

    @property
    def score(self):
        """
        Returns the score of the hand.
        """
        score = 0

        if len(self.cards) == 0:
            return score

        for row in self.card_groups:
            if row[0].card.rank == row[1].card.rank:
                continue
            score += row[0].card.points
            score += row[1].card.points

        return score

    @property
    def is_four_corners(self):
        return len(set([
            self.cards[index].card.rank for index in [0, 1, 4, 5]
        ])) == 1

    def flip_all(self):
        for card in self.cards:
            card.flip()


class HandCard(object):
    """
    Represents a card in a player's hand. Contains both the card and the current
    state (face up or down) of the card.
    """

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

    def flip(self):
        self.state = self.STATE_FACE_UP

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

    def __str__(self):
        return self.name
