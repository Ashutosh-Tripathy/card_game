# python3 -m unittest discover -v
# nodemon   --watch test_card_game.py --watch card_game.py  --exec "python3 -m unittest discover -v"
# coverage run -m unittest discover
# coverage html

import unittest
from unittest.mock import MagicMock, Mock, call
from card_game import Cards, InvalidOperationException, Card, GameStatus, Player, CardGame


class TestCard(unittest.TestCase):
    """Test cases for Card"""

    def test_init(self):
        """Test Card initial instance variables. """
        card = Card(0, 'A')
        self.assertEqual(card.get_id(), 0)
        self.assertEqual(card.get_text(), 'A')


class TestCards(unittest.TestCase):
    """Test cases for Cards"""

    def test_init(self):
        """Test Cards initial instance variables. """
        cards = Cards()
        self.assertIsInstance(cards._ids, list)
        self.assertIsInstance(cards._card_tracker, dict)
        self.assertIsInstance(cards._cards, list)

    def test_update_card_tracker(self):
        """_update_card_tracker should reduce card count by 1 """
        cards = Cards()
        init_count = cards._card_tracker[0]
        cards._update_card_tracker(0)
        self.assertEqual(cards._card_tracker[0], init_count - 1)

    def test_update_card_tracker_when_card_used(self):
        cards = Cards()
        cards._update_card_tracker(0)
        cards._update_card_tracker(0)
        cards._update_card_tracker(0)
        cards._update_card_tracker(0)
        self.assertTrue(0 not in cards._ids)

    def test_get_random_card(self):
        cards = Cards()
        self.assertIsInstance(cards.get_random_card(), Card)

    def test_get_random_card_when_no_ids(self):
        cards = Cards()
        cards._ids = []
        self.assertRaises(InvalidOperationException, cards.get_random_card)


class TestGameStatus(unittest.TestCase):
    """Test cases for GameStatus"""

    def test_str(self):
        game_status = GameStatus.NOT_STARTED
        self.assertEqual(str(game_status), 'Game status: Not started')


class TestPlayer(unittest.TestCase):
    """Test cases for Player"""

    def test_init(self):
        """Test Player initial instance variables. """
        player = Player(0)
        self.assertEqual(player.get_id(), 0)
        self.assertIsInstance(player.get_cards(), list)

    def test_add_card(self):
        player = Player(0)
        init_count = len(player.get_cards()[0])
        player.add_card(Card(0, 'A'))
        self.assertEqual(len(player.get_cards()[0]), init_count + 1)

    def test_show_cards(self):
        player = Player(0)
        try:
            player.show_cards()
        except Exception:
            self.fail("show_cards() raised Exception unexpectedly!")

    def test_reset_card(self):
        player = Player(0)
        init_cards = player.get_cards()
        player.add_card(Card(0, 'A'))
        player.reset_card()
        self.assertEqual(player.get_cards(), init_cards)

    def test_check_count_when_triplet_and_sequence(self):
        player = Player(0)
        self.assertEqual(player._check_count(
            [[], ['K', 'K', 'K']], [['A'], ['K'], ['Q']], 3), 1)

    def test_check_count_when_two_triplet(self):
        player = Player(0)
        self.assertEqual(player._check_count(
            [[], ['K', 'K', 'K']], [['A', 'A', 'A'], []], 3), -1)

    def test_check_count_when_no_triplet(self):
        player = Player(0)
        self.assertEqual(player._check_count(
            [['A'], ['K', 'K']], [['A', 'A'], ['K']], 3), 0)

    def test_check_sequence_when_sequece_and_pair(self):
        player = Player(0)
        self.assertEqual(player._check_sequence(
            [['A'], ['K'], ['Q']], [['A'], ['K', 'K']]), 1)

    def test_check_sequence_when_two_sequece(self):
        player = Player(0)
        self.assertEqual(player._check_sequence(
            [['A'], ['K'], ['Q'], []], [[], ['K'], ['Q'], ['10']]), 1)

    def test_compare_cards_when_equal_cards(self):
        player = Player(0)
        cards = [[Card(0, 'A')]]
        player._check_count = MagicMock()
        player._check_sequence = MagicMock()
        self.assertEqual(player._compare_cards(cards, cards), 0)
        player._check_count.assert_not_called()
        player._check_sequence.assert_not_called()

    def test_compare_cards_when_cards_not_equal(self):
        player = Player(0)
        cards1 = [[Card(0, 'A')], []]
        cards2 = [[], [Card(1, 'K')]]
        mock = Mock(return_value=0)

        player._check_count = mock
        player._check_sequence = mock
        self.assertEqual(player._compare_cards(cards1, cards2), 1)
        card_param1 = [['A'], []]
        card_param2 = [[], ['K']]
        calls = [call(card_param1, card_param2, 3), call(
            card_param1, card_param2), call(card_param1, card_param2, 2)]
        mock.assert_has_calls(calls)

    def test_has_better_cards(self):
        player1 = Player(0)
        player2 = Player(0)
        card = Card(0, 'A')
        player1.add_card(card)
        player1._compare_cards = MagicMock()
        player1.has_better_cards(player2)
        player1._compare_cards.assert_called_with([[card], [], [], [], [], [], [], [], [
        ], [], [], []], [[], [], [], [], [], [], [], [], [], [], [], []])


class TestCardGame(unittest.TestCase):
    """Test cases for CardGame"""

    def test_init(self):
        card_game = CardGame([0, 1])
        self.assertIsInstance(card_game._players, dict)
        self.assertIsInstance(card_game._available_players, list)
        self.assertIsInstance(card_game._cards, Cards)
        self.assertEqual(card_game._game_status, GameStatus.NOT_STARTED)

    def test_init_when_only_one_player(self):
        self.assertRaises(ValueError, CardGame, [0])

    def test_init_when_more_than_16_players(self):
        self.assertRaises(ValueError, CardGame, [x for x in range(17)])

    def test_print_game_status(self):
        card_game = CardGame([0, 1])
        try:
            card_game._print_game_status()
        except Exception:
            self.fail("_print_game_status() raised Exception unexpectedly!")

    def test_show_winner(self):
        card_game = CardGame([0, 1])
        try:
            card_game._show_winner()
        except Exception:
            self.fail("_print_game_status() raised Exception unexpectedly!")

    def test_is_game_tied(self):
        card_game = CardGame([0, 1])
        self.assertTrue(card_game._is_game_tied())

    def test_try_to_break_tie(self):
        card_game = CardGame([0, 1])
        card_game._reset_players_cards = MagicMock()
        card_game._distribute_card = MagicMock()

        card_game._try_to_break_tie()
        card_game._reset_players_cards.assert_called_once()
        card_game._distribute_card.assert_called_once()

    def test_remove_player(self):
        card_game = CardGame([0, 1])
        card_game._remove_player(Player(1))
        self.assertTrue(1 not in card_game._available_players)


if __name__ == '__main__':
    unittest.main()
