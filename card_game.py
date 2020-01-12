import random
from enum import Enum
import functools
import time
import copy


class Card:
    def __init__(self, card_id, text):
        self._card_id = card_id
        self._text = text

    def get_id(self):
        return self._card_id

    def get_text(self):
        return self._text


class Cards:
    def __init__(self):
        self._ids = [x for x in range(12)]
        self._ids = [x for x in range(2)]
        self._card_tracker = {id: 4 for id in self._ids}
        self._cards = ['A', 'K', 'Q', '10',
                       '9', '8', '7', '6', '5', '4', '3', '2']

    def _update_card_tracker(self, card_id):
        self._card_tracker[card_id] -= 1
        if self._card_tracker[card_id] == 0:
            self._ids.remove(card_id)

    def get_random_card(self):
        if len(self._ids) == 0:
            print('No card left to play the game.')
            raise InvalidOperationException()
        id = self._ids[random.randrange(0, len(self._ids))]
        self._update_card_tracker(id)
        return Card(id, self._cards[id])


class InvalidOperationException(Exception):
    pass


class GameStatus(Enum):
    # 0 not started, 1 started, 2 tied, 3 not possible to break tie, 4 finished
    NOT_STARTED = 'Not started'
    STARTING = 'Starting'
    TIED = 'Tied'
    IMPOSSIBLE_TO_BREAK_TIE = 'Impossible to break tie'
    FINISHED = 'Finished'

    def __str__(self):
        return 'Game status: %s' % self.value


class Player:
    def __init__(self, id):
        self._id = id
        self._cards = [[] for id in range(12)]

    def get_id(self):
        return self._id

    def get_cards(self):
        return copy.deepcopy(self._cards)

    def add_card(self, card):
        return self._cards[card.get_id()].append(card)

    def show_cards(self):
        print('Cards for player %s: ' % (self._id),
              [x.get_text() for x in functools.reduce(lambda x, y: x+y, self._cards)])

    # if there is tie reset cards for each player so that only new card decides the result
    def reset_card(self):
        self._cards = [[] for _ in range(12)]

    def _check_count(self, cards1, cards2, count):
        result = 0
        count1 = max(map(len, cards1))
        count2 = max(map(len, cards2))
        if max(count1, count2) == count:
            if count1 == count2:
                result = 1 if cards1 > cards2 else -1
            else:
                result = 1 if count1 > count2 else -1
        return result

    def _check_sequence(self, cards1, cards2):
        result = 0
        seq1 = '111' in ''.join(map(str, map(len, cards1)))
        seq2 = '111' in ''.join(map(str, map(len, cards2)))
        if seq1 and seq2:
            result = 1 if cards1 > cards2 else -1
        elif seq1 or seq2:
            result = 1 if seq1 else -1
        return result

    def _compare_cards(self, cards1, cards2):
        result = 0
        cards1 = [[item.get_text() for item in card]for card in cards1]
        cards2 = [[item.get_text() for item in card]for card in cards2]
        if cards1 != cards2:
            result = self._check_count(cards1, cards2, 3) or self._check_sequence(
                cards1, cards2) or self._check_count(cards1, cards2, 2) or (1 if cards1 > cards2 else -1)

        return result

    def has_better_cards(self, other):
        return self._compare_cards(self._cards, other.get_cards())


class CardGame:
    def __init__(self, players_id):
        if len(players_id) < 2:
            raise ValueError("Atleast two players should play this game.")
        if len(players_id) * 3 > 48:
            raise ValueError('Too many player to play the game.')
        self._players = {id: Player(id) for id in players_id}
        self._available_players = players_id
        self._cards = Cards()
        self._game_status = GameStatus.NOT_STARTED

    def _print_game_status(self):
        for id in self._available_players:
            self._players[id].show_cards()

    def play(self):
        self._game_status = GameStatus.STARTING
        while True:
            print(self._game_status)
            if self._game_status == GameStatus.STARTING:
                self._start_game()
                self._print_game_status()
                self._remove_losers_from_game()
                if self._is_game_tied():
                    self._game_status = GameStatus.TIED
                else:
                    self._game_status = GameStatus.FINISHED

            elif self._game_status == GameStatus.TIED:
                self._try_to_break_tie()
                self._print_game_status()
                if not self._is_game_tied():
                    self._game_status = GameStatus.FINISHED

            elif self._game_status == GameStatus.IMPOSSIBLE_TO_BREAK_TIE:
                self._print_game_status()
                print('Not possible to break tie. All cards used.')
                break

            elif self._game_status == GameStatus.FINISHED:
                self._show_winner()
                break

            print('-------------------------------------------------------')
            time.sleep(1)

    def _start_game(self):
        for _ in range(3):
            self._distribute_card()

    def _show_winner(self):
        print('Player %s won the game.' % str(self._available_players[-1]))

    def _distribute_card(self):
        for id in self._available_players:
            card = self._cards.get_random_card()
            self._players[id].add_card(card)

    def _compare_cards(self, player1, player2):
        return player1.has_better_cards(player2)

    def _remove_player(self, player):
        print('Player %s lost.' % str(player.get_id()))
        self._available_players.remove(player.get_id())

    def _remove_losers_from_game(self):
        i = 0
        while i + 1 < len(self._available_players):
            player1 = self._players[self._available_players[i]]
            player2 = self._players[self._available_players[i + 1]]
            result = self._compare_cards(player1, player2)
            if result:
                self._remove_player(player1) if result == - \
                    1 else self._remove_player(player2)
                i -= 1
            i += 1

    def _reset_players_cards(self):
        for id in self._available_players:
            self._players[id].reset_card()

    def _is_game_tied(self):
        return len(self._available_players) > 1

    def _try_to_break_tie(self):
        self._reset_players_cards()
        try:
            self._distribute_card()
        except InvalidOperationException:
            self._game_status = GameStatus.IMPOSSIBLE_TO_BREAK_TIE


if __name__ == '__main__':
    players = [1, 2, 3, 4, 5, 6]
    players = [1, 2]
    card_game = CardGame(players)
    card_game.play()
