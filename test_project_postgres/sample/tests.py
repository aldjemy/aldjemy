from django.test import TestCase
from sqlalchemy.dialects.postgresql import array
from sample.models import TicTacToeBoard


class TestArrayField(TestCase):
    """
    Tests that queries involving array fields can be performed.
    """

    def test_tic_tac_toe(self):
        """
        Test querying the TicTacToeBoard model.
        """
        boards = [
            ['x', 'o', 'x', 'o', 'o', 'x', 'x', 'x', 'o'],  # both (full board)
            [' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' '],  # only x
            [' ', ' ', ' ', 'o', 'o', ' ', ' ', ' ', 'o'],  # only o
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # none
        ]
        for board in boards:
            ttt = TicTacToeBoard(board=board)
            ttt.save()

        contains = lambda c: TicTacToeBoard.sa.board.contains(array([c]))

        query = TicTacToeBoard.sa.query(TicTacToeBoard.sa.id)

        assert query.filter(contains('x')).count() == 2
        assert query.filter(contains('o')).count() == 2
        assert query.filter(contains(' ')).count() == 3