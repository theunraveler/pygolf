import random


class Card(object):

    SUIT_CLUB = 'club'
    SUIT_DIAMOND = 'diamond'
    SUIT_HEART = 'heart'
    SUIT_SPADE = 'spade'
    SUITS = [SUIT_CLUB, SUIT_DIAMOND, SUIT_HEART, SUIT_SPADE]

    RANK_ACE = 'A'
    RANK_TWO = '2'
    RANK_THREE = '3'
    RANK_FOUR = '4'
    RANK_FIVE = '5'
    RANK_SIX = '6'
    RANK_SEVEN = '7'
    RANK_EIGHT = '8'
    RANK_NINE = '9'
    RANK_TEN = '10'
    RANK_JACK = 'J'
    RANK_QUEEN = 'Q'
    RANK_KING = 'K'
    RANKS = [
        RANK_ACE, RANK_TWO, RANK_THREE, RANK_FOUR, RANK_FIVE, RANK_SIX,
        RANK_SEVEN, RANK_EIGHT, RANK_NINE, RANK_TEN, RANK_JACK, RANK_QUEEN,
        RANK_KING
    ]

    def __init__(self, suit, rank):
        assert suit in self.SUITS, 'Suit is invalid'
        assert rank in self.RANKS, 'Rank is invalid'
        self.suit = suit
        self.rank = rank

    @property
    def points(self):
        if self.rank == self.RANK_ACE:
            return -2
        elif self.rank == self.RANK_KING:
            return 0
        elif self.rank == self.RANK_QUEEN and self.suit == self.SUIT_SPADE:
            return 40
        elif self.rank in [self.RANK_JACK, self.RANK_QUEEN]:
            return 10
        return int(self.rank)

    def __str__(self):
        return '%s of %ss' % (self.rank, self.suit)
    __repr__ = __str__


class Deck(object):

    def __init__(self):
        self.cards = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.cards.append(Card(suit, rank))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()
