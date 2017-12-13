from clint.textui import puts, colored, prompt, validators

from .game import Game, PlayerCard, Player


INIT_ACTIONS = {
    '1': 'Flip the top left card',
    '2': 'Flip the top right card',
    '3': 'Flip the middle left card',
    '4': 'Flip the middle right card',
    '5': 'Flip the bottom left card',
    '6': 'Flip the bottom right card',
}
INIT_ACTION_VALIDATOR = validators.OptionValidator(INIT_ACTIONS.keys())


CARD_ACTION_TAKE = '1'
CARD_ACTION_DRAW = '2'

ACTIONS = [
    {'selector': str(index), 'prompt': message}
    for index, message in list(Game.ACTIONS.items())
]


CARD_WIDTH = 20
CARD_HEIGHT = 10


def main():
    puts(colored.green('Welcome to Golf!'))

    puts()
    num_players = prompt.query('How many players?', default='2', validators=[
        validators.IntegerValidator()
    ])
    player_names = [
        prompt.query('Player %s name:' % (i + 1), default='Player %s' % (i + 1))
        for i in range(int(num_players))
    ]

    game = Game(players=[Player(name=name) for name in player_names])

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

        cards = [None, None]
        while cards[0] == cards[1]:
            for index, action in list(INIT_ACTIONS.items()):
                puts('[%s] %s' % (index, action))

            cards = [
                prompt.query('First card to flip:', validators=[INIT_ACTION_VALIDATOR]),
                prompt.query('Second card to flip:', validators=[INIT_ACTION_VALIDATOR]),
            ]

        for card_index in cards:
            player.cards[int(card_index) - 1].state = PlayerCard.STATE_FACE_UP

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
        card_action = prompt.options('What would you like to do?', [
            {'selector': CARD_ACTION_TAKE, 'prompt': 'Take the %s from the discard pile' % colored.green(str(game.last_discard))},
            {'selector': CARD_ACTION_DRAW, 'prompt': 'Draw a card'},
        ], default=CARD_ACTION_DRAW)
        card = game.last_discard if card_action == CARD_ACTION_TAKE else _do_draw(game)
    else:
        card = _do_draw(game)

    action = prompt.options(
        'What would you like to do with the %s?' % colored.green(str(card)),
        ACTIONS,
        default=str(Game.ACTION_DISCARD),
    )

    game.turn(card, int(action))


def _do_draw(game):
    card = game.deck.draw()
    puts('Drew a ', newline=False)
    puts(colored.green(str(card)))
    return card


def _declare_winner(game):
    puts()

    for player in game.players:
        _puts_player_header(player)
        _puts_formatted_hand(player)

    scores = {p: p.hand_score for p in game.players}

    puts('-' * 30)
    for player, score in list(scores.items()):
        puts('%s: %s' % (player, score))
    puts('-' * 30)

    best = min(scores.values())
    winners = [p for p, s in list(scores.items()) if s == best]

    if len(winners) == 1:
        puts(colored.green('%s is the winner!!! Thanks for playing.' % winners[0]))
    else:
        puts(colored.green('It\'s a tie between %s!!! Thanks for playing!' % ', '.join(
            [str(w) for w in winners]
        )))


def _puts_formatted_hand(player):
    for row in player.cards_in_rows:
        puts('-' * CARD_WIDTH + '  ' + '-' * CARD_WIDTH)

        puts(
            '| %s|' % str(row[0]).ljust(CARD_WIDTH - 3) +
            '  ' +
            '| %s|\n' % str(row[1]).ljust(CARD_WIDTH - 3)
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
