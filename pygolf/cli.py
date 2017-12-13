from clint.arguments import Args
from clint.eng import join
from clint.textui import puts, colored, prompt, validators

import prettytable

from .game import Game, Player, FlipAction, CardAction, DrawAction


INIT_ACTIONS = {
    '1': 'Flip the top left card',
    '2': 'Flip the top right card',
    '3': 'Flip the middle left card',
    '4': 'Flip the middle right card',
    '5': 'Flip the bottom left card',
    '6': 'Flip the bottom right card',
}
INIT_ACTION_VALIDATOR = validators.OptionValidator(INIT_ACTIONS.keys())


CARD_TAKE_ACTIONS = [
    {'selector': str(index), 'prompt': message}
    for index, message in list(CardAction.TAKE_ACTIONS.items())
]
CARD_DRAW_ACTIONS = [
    {'selector': str(index), 'prompt': message}
    for index, message in list(CardAction.DRAW_ACTIONS.items())
]


CARD_WIDTH = 20
CARD_HEIGHT = 10


def main():
    puts(colored.green('Welcome to Golf!'))
    puts()

    args = Args()

    if args.contains(['-r', '--rules']):
        _do_rules()
        return

    _do_game()


def _do_game():
    game = Game(players=[Player(name=name) for name in _get_players()])

    puts()
    puts(colored.green('Awesome.'))

    while len(game.rounds) < 9:
        game.begin_round()

        puts()
        _puts_beginning_of_round_header(game)

        _init_round(game.current_round)
        while not game.current_round.is_finished:
            _do_turn(game.current_round)

        _puts_end_of_round_summary(game)

    _declare_winner(game)


def _init_round(round_):
    for hand in round_.hands:
        puts()
        puts('Now %s should choose 2 cards to flip over.' % (colored.green(str(hand.player))))
        _do_initial_flip(hand)
        _puts_formatted_hand(hand)
        puts()


def _do_turn(round_):
    player = round_.current_hand.player

    puts()
    _puts_player_header(player)
    puts()

    if round_.is_terminal:
        _puts_round_is_terminal_warning(round_)
        puts()

    _puts_formatted_hand(round_.current_hand)

    _draw_action = prompt.options('What would you like to do?', [
        {'selector': str(DrawAction.ACTION_TAKE), 'prompt': 'Take the %s from the discard pile' % colored.green(str(round_.last_discard))},
        {'selector': str(DrawAction.ACTION_DRAW), 'prompt': 'Draw a card'},
    ], default=str(DrawAction.ACTION_DRAW))
    draw_action = DrawAction(round_, _draw_action)
    card = draw_action()

    if draw_action.action == DrawAction.ACTION_DRAW:
        puts('Drew a ', newline=False)
        puts(colored.green(str(card)))
        _card_action = prompt.options(
            'What would you like to do with the %s?' % colored.green(str(card)),
            CARD_DRAW_ACTIONS,
            default=str(CardAction.ACTION_DISCARD),
        )
    else:
        _card_action = prompt.options(
            'What would you like to do with the %s?' % colored.green(str(card)),
            CARD_TAKE_ACTIONS
        )

    CardAction(round_, _card_action)(card)

    round_.end_turn()


def _declare_winner(game):

    __, winners = game.result

    if len(winners) == 1:
        message = '%s is the winner!!! Thanks for playing.' % winners[0]
    else:
        message = 'It\'s a tie between %s!!! Thanks for playing!' % join(
            [str(w) for w in winners]
        )
    _puts_bordered_header(message, colored.green)


def _get_players():
    num_players = prompt.query('How many players?', default='2', validators=[
        validators.IntegerValidator()
    ])
    return [
        prompt.query('Player %s name:' % (i + 1), default='Player %s' % (i + 1))
        for i in range(int(num_players))
    ]


def _do_initial_flip(hand):
    while True:
        try:
            for index, action in list(INIT_ACTIONS.items()):
                puts('[%s] %s' % (index, action))

            FlipAction(hand)(*[
                prompt.query('%s card to flip:' % index, validators=[INIT_ACTION_VALIDATOR])
                for index in ['First', 'Second']
            ])
        except AssertionError:
            continue

        return


def _puts_beginning_of_round_header(game):
    _puts_bordered_header('Round #%s' % len(game.rounds), colored.green)


def _puts_formatted_hand(hand):
    for group in hand.card_groups:
        puts('-' * CARD_WIDTH + '  ' + '-' * CARD_WIDTH)

        left_card, right_card = group
        puts(
            '| %s|' % str(left_card).ljust(CARD_WIDTH - 3) +
            '  ' +
            '| %s|' % str(right_card).ljust(CARD_WIDTH - 3)
        )

        for __ in range(CARD_HEIGHT - 3):
            puts(
                '|' + (' ' * (CARD_WIDTH - 2)) + '|' +
                '  ' +
                '|' + (' ' * (CARD_WIDTH - 2)) + '|'
            )

        puts('-' * CARD_WIDTH + '  ' + '-' * CARD_WIDTH)


def _puts_player_header(player):
    _puts_bordered_header(str(player), colored.green)


def _puts_round_is_terminal_warning(round_):
    _puts_bordered_header(
        '%s has exposed all of their cards! This is your last turn.' % round_.terminal_hand.player,
        colored.red
    )


def _puts_end_of_round_summary(game):
    puts()
    _puts_bordered_header(
        'Round #%s finished! Here are the results: ' % len(game.rounds),
        colored.green
    )
    puts()

    for hand in game.current_round.hands:
        _puts_player_header(hand.player)
        hand.flip_all()
        _puts_formatted_hand(hand)

    summary = prettytable.PrettyTable(
        ['Round'] + [str(player) for player in game.players]
    )
    summary.align['Round'] = 'r'
    summary.hrules = prettytable.ALL
    for index, round_ in enumerate(game.rounds):
        summary.add_row(['Round #%s' % (index + 1)] + [str(score) for score in round_.result])
    summary.add_row(['Total'] + [str(score) for score in game.result[0]])
    puts(str(summary))


def _puts_bordered_header(text, formatter=str):
    length = len(text)
    puts(formatter('=' * length))
    puts(formatter(text))
    puts(formatter('=' * length))


def _do_rules():
    puts(
        """
        Golf (also known as Polish Polka, Polish Poker, Turtle, Hara Kiri,
        Poison, or Crazy Nines) is a card game where players try to earn the
        lowest number of points (as in golf, the sport) over the course of nine
        rounds (or "holes" to further use golfing terminology). It is a game
        for two or more players using a standard 52-card deck.

        Each player is dealt 6 cards face down from the deck, the remainder is
        placed face down and the top card is turned up to start the discard
        pile beside it. Players arrange their 6 cards in a 2 x 3 grid in front
        of them and turn 2 of these cards face up. This arrangement is
        maintained throughout the game and players always have 6 cards in front
        of them.

        The object is for players to reduce the value of the cards in front of
        them by either swapping them for lesser value cards or by pairing them
        up with cards of equal rank and trying to get the lowest score.

        Beginning with the first player, players take turns drawing single cards
        from either the deck or discard pile. The drawn card may either be
        swapped for one of that player's 6 cards, or discarded. If the card is
        swapped for one of the face down cards, the card swapped in remains face
        up. The round ends when all of a player's cards are face-up. Remaining
        players then have one turn to draw a card to improve their hands and
        then scores are totaled and recorded. Then a new round begins.

        During play it is not legal for a player to pick up a card from the
        discard pile and return it to the discard pile without playing it, to
        allow another player to retrieve the card. A card picked up from the
        discard pile must be swapped with one of the current player's cards.

        Game is nine "holes" (deals), and the player with the lowest total score
        is designated winner.

        Scores are calculated as follows:

            - Aces are worth -2
            - Kings are worth 0
            - The Queen of Spades is worth 40
            - All other cards are worth their face value (face cards are 10)
            - Cards of the same rank opposite one another in a row cancel each
              other out
            - If a player has cards of the same rank in all 4 corners of their
              arrangement (known as "four corners") at the end of the round,
              all other players receive 30 points.

        (Taken from https://en.wikipedia.org/wiki/Golf_%28card_game%29, with
        slight modifications)
    """)
