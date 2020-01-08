import random
import functools
import time


class Cards:
    def __init__(self):
        self.card_tracker = [4] * 12
        self.card_text = ['A', 'K', 'Q', '10',
                          '9', '8', '7', '6', '5', '4', '3', '2']
        # reduse available_ids to increase tie probability
        self.available_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        # self.available_ids = [0, 1, 2 ]

    def get_random_card(self):
        if len(self.available_ids) == 0:
            raise InvalidOperationException('No card left to play the game.')
        id = self.available_ids[random.randrange(0, len(self.available_ids))]
        self.card_tracker[id] -= 1
        if self.card_tracker[id] == 0:
            self.available_ids.remove(id)
        return Card(id, self.card_text[id])


class InvalidOperationException(Exception):
    pass


class Card:
    def __init__(self, id, text):
        self.id = id
        self.text = text


class Player:
    def __init__(self, id):
        self.id = id
        self.cards = [[] for _ in range(13)]

    def show_cards(self):
        print('Cards for player %s: ' % (self.id),
              [x.text for x in functools.reduce(lambda x, y: x+y, self.cards)])

    # if there is tie reset cards for each player so that only new card decides the result
    def reset_card(self):
        self.cards = [[] for _ in range(13)]

    def compare_cards(self, cards1, cards2):
        count1 = max(map(len, cards1))
        count2 = max(map(len, cards2))

        # check trial
        if max(count1, count2) >= 3:
            if count1 == count2:
                return 1 if cards1 > cards2 else -1
            elif count1 > count2:
                return 1
            else:
                return -1

        # check sequence
        seq1 = '111' in ''.join(map(str, map(len, cards1)))
        seq2 = '111' in ''.join(map(str, map(len, cards2)))
        if seq1 and seq2:
            return 1 if cards1 > cards2 else -1
        elif seq1 or seq2:
            return 1 if seq1 else -1

        # check pair
        if max(count1, count2) == 2:
            if count1 == count2:
                return 1 if cards1 > cards2 else -1
            elif count1 > count2:
                return 1
            else:
                return -1

        # finally value
        return 1 if cards1 > cards2 else -1

    def has_better_cards(self, other):
        cards1 = [[(card.id, card.text) for card in cards] for cards in self.cards]
        cards2 = [[(card.id, card.text) for card in cards] for cards in other.cards]
        return 0 if cards1 == cards2 else self.compare_cards(cards1, cards2)


class Game:
    def __init__(self, players_id):
        if len(players_id) * 3 > 48:
            raise Exception('Too many player to play the game.')
        self.players = {id: Player(id) for id in players_id}
        self.available_players = players_id
        self.cards = Cards()
        # 0 not started, 1 started, 2 tied, 3 not possible to break tie, 4 finished
        self.game_status = 0

    def play(self):
        while True:
            if self.game_status == 0:
                self.distribute_first_time()
                self.game_status = 1
            elif self.game_status == 2:
                print('Game tied')
                self.try_to_break_tie()

            self.print_game_status()
            self.remove_losers_from_game()
            if self.is_game_finished():
                self.game_status = 4
                self.show_winner()
                break
            elif self.game_status == 3:
                print('Not possible to break tie. All cards used.')
                break
            else:
                self.game_status = 2
            print('-------------------------------------------------------')
            time.sleep(1)

    def is_game_finished(self):
        return len(self.available_players) == 1

    def print_game_status(self):
        for id in self.available_players:
            self.players[id].show_cards()

    def show_winner(self):
        print('Player %s won the game.' % str(self.available_players[-1]))

    def distribute_first_time(self):
        for _ in range(3):
            self.distribute_card()

    def distribute_card(self):
        for id in self.available_players:
            card = self.cards.get_random_card()
            self.players[id].cards[card.id].append(card)

    def remove_losers_from_game(self):
        i = 0
        while i + 1 < len(self.available_players):
            result = self.players[self.available_players[i]].has_better_cards(
                self.players[self.available_players[i + 1]])
            id = None
            if result == -1:
                id = self.available_players.pop(i)
            elif result == 1:
                id = self.available_players.pop(i + 1)
            if id is not None:
                print('Player %s lost.' % str(id))
                i -= 1
            i += 1

    def try_to_break_tie(self):
        try:
            for id in self.available_players:
                self.players[id].reset_card()
            self.distribute_card()
        except InvalidOperationException:
            self.game_status = 3


players = [1, 2, 3, 4, 5, 6]
game = Game(players)
game.play()
