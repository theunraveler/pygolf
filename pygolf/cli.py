from clint.eng import join
from clint.textui import puts, colored, prompt, validators

from .game import Game, PlayerCard, Player, CardAction, DrawAction


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

    _init(game)
    while not game.is_finished:
        _do_turn(game)
    _declare_winner(game)


def _init(game):
    game.start()

    puts()
    puts(colored.green('Awesome.'))

    for player in game.players:
        puts()
        puts('Now %s should choose 2 cards to flip over.' % (colored.green(str(player))))
        _get_initial_flip(game, player)
        _puts_formatted_hand(player)
        puts()


def _do_turn(game):
    player = game.current_player

    puts()
    _puts_player_header(player)
    puts()

    if game.is_terminal:
        _puts_game_is_terminal_warning(game)
        puts()

    _puts_formatted_hand(player)

    if game.last_discard:
        _draw_action = prompt.options('What would you like to do?', [
            {'selector': str(DrawAction.ACTION_TAKE), 'prompt': 'Take the %s from the discard pile' % colored.green(str(game.last_discard))},
            {'selector': str(DrawAction.ACTION_DRAW), 'prompt': 'Draw a card'},
        ], default=str(DrawAction.ACTION_DRAW))
    else:
        _draw_action = DrawAction.ACTION_DRAW

    draw_action = DrawAction(game, _draw_action)
    card = draw_action()

    if draw_action.action == DrawAction.ACTION_DRAW:
        puts('Drew a ', newline=False)
        puts(colored.green(str(card)))

    _card_action = prompt.options(
        'What would you like to do with the %s?' % colored.green(str(card)),
        CARD_ACTIONS,
        default=str(CardAction.ACTION_DISCARD),
    )
    CardAction(game, _card_action)(card)

    game.end_turn()


def _declare_winner(game):
    puts()

    for player in game.players:
        _puts_player_header(player)
        _puts_formatted_hand(player)

    scores, winners = game.result

    puts('-' * 30)
    for player, score in list(scores.items()):
        puts('%s: %s' % (player, score))
    puts('-' * 30)

    if len(winners) == 1:
        puts(colored.green('%s is the winner!!! Thanks for playing.' % winners[0]))
    else:
        puts(colored.green('It\'s a tie between %s!!! Thanks for playing!' % join(
            [str(w) for w in winners]
        )))


def _get_players():
    num_players = prompt.query('How many players?', default='2', validators=[
        validators.IntegerValidator()
    ])
    return [
        prompt.query('Player %s name:' % (i + 1), default='Player %s' % (i + 1))
        for i in range(int(num_players))
    ]


def _get_initial_flip(game, player):
    while True:
        try:
            for index, action in list(INIT_ACTIONS.items()):
                puts('[%s] %s' % (index, action))

            cards = [
                prompt.query('First card to flip:', validators=[INIT_ACTION_VALIDATOR]),
                prompt.query('Second card to flip:', validators=[INIT_ACTION_VALIDATOR]),
            ]
            game.initial_flip(player, cards)
        except AssertionError:
            continue

        return


def _puts_formatted_hand(player):
    for row in player.cards_in_rows:
        puts('-' * CARD_WIDTH + '  ' + '-' * CARD_WIDTH)

        puts(
            '| %s|' % str(row[0]).ljust(CARD_WIDTH - 3) +
            '  ' +
            '| %s|' % str(row[1]).ljust(CARD_WIDTH - 3)
        )

        for __ in range(CARD_HEIGHT - 3):
            puts(
                '|' + (' ' * (CARD_WIDTH - 2)) + '|' +
                '  ' +
                '|' + (' ' * (CARD_WIDTH - 2)) + '|'
            )

        puts('-' * CARD_WIDTH + '  ' + '-' * CARD_WIDTH)


def _puts_player_header(player):
    as_string = str(player)
    puts(colored.green('=' * len(as_string)))
    puts(colored.green(as_string))
    puts(colored.green('=' * len(as_string)))


def _puts_game_is_terminal_warning(game):
    as_string = '%s has exposed all of their cards! This is your last turn.' % game.terminal_player
    puts(colored.red('=' * len(as_string)))
    puts(colored.red(as_string))
    puts(colored.red('=' * len(as_string)))
