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


CARD_ACTIONS = [
    {'selector': str(index), 'prompt': message}
    for index, message in list(CardAction.ACTIONS.items())
]


CARD_WIDTH = 20
CARD_HEIGHT = 10


def main():
    puts(colored.green('Welcome to Golf!'))
    puts()

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

    if round_.last_discard:
        _draw_action = prompt.options('What would you like to do?', [
            {'selector': str(DrawAction.ACTION_TAKE), 'prompt': 'Take the %s from the discard pile' % colored.green(str(round_.last_discard))},
            {'selector': str(DrawAction.ACTION_DRAW), 'prompt': 'Draw a card'},
        ], default=str(DrawAction.ACTION_DRAW))
    else:
        _draw_action = DrawAction.ACTION_DRAW

    draw_action = DrawAction(round_, _draw_action)
    card = draw_action()

    if draw_action.action == DrawAction.ACTION_DRAW:
        puts('Drew a ', newline=False)
        puts(colored.green(str(card)))

    _card_action = prompt.options(
        'What would you like to do with the %s?' % colored.green(str(card)),
        CARD_ACTIONS,
        default=str(CardAction.ACTION_DISCARD),
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
