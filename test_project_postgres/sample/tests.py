from django.test import TestCase
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import array
from sample.models import TicTacToeBoard, JsonModel

from aldjemy.core import get_engine


class TestArrayField(TestCase):
    """
    Tests that queries involving array fields can be performed.
    """

    def test_tic_tac_toe(self):
        """
        Test querying the TicTacToeBoard model.
        """
        boards = [
            ["x", "o", "x", "o", "o", "x", "x", "x", "o"],  # both (full board)
            [" ", " ", " ", " ", "x", " ", " ", " ", " "],  # only x
            [" ", " ", " ", "o", "o", " ", " ", " ", "o"],  # only o
            [" ", " ", " ", " ", " ", " ", " ", " ", " "],  # none
        ]
        for board in boards:
            ttt = TicTacToeBoard(board=board)
            ttt.save()

        contains = lambda c: TicTacToeBoard.sa.board.contains(array([c]))

        query = TicTacToeBoard.sa.query(TicTacToeBoard.sa.id)

        assert query.filter(contains("x")).count() == 2
        assert query.filter(contains("o")).count() == 2
        assert query.filter(contains(" ")).count() == 3

    def test_sa_objects_fetching(self):
        """
        Test full object fetching using SQLAlchemy-aldjemy ORM.
        """
        boards = [
            ["x", "o", "x", "o", "o", "x", "x", "x", "o"],  # both (full board)
            [" ", " ", " ", " ", "x", " ", " ", " ", " "],  # only x
            [" ", " ", " ", "o", "o", " ", " ", " ", "o"],  # only o
            [" ", " ", " ", " ", " ", " ", " ", " ", " "],  # none
        ]

        created_objects = []
        for board in boards:
            ttt = TicTacToeBoard(board=board)
            ttt.save()
            created_objects.append(ttt)

        test_object = TicTacToeBoard.sa.query().get(created_objects[0].id)
        assert test_object.id == created_objects[0].id
        assert test_object.board == boards[0]

    def test_sa_sql_expression_language_fetching(self):
        """
        Test full record fetching using SQLAlchemy-aldjemy SQL Expression Language.
        """
        boards = [
            ["x", "o", "x", "o", "o", "x", "x", "x", "o"],  # both (full board)
            [" ", " ", " ", " ", "x", " ", " ", " ", " "],  # only x
            [" ", " ", " ", "o", "o", " ", " ", " ", "o"],  # only o
            [" ", " ", " ", " ", " ", " ", " ", " ", " "],  # none
        ]

        created_objects = []
        for board in boards:
            ttt = TicTacToeBoard(board=board)
            ttt.save()
            created_objects.append(ttt)

        query = (
            select([TicTacToeBoard.sa.id, TicTacToeBoard.sa.board])
            .order_by(TicTacToeBoard.sa.id)
            .limit(10)
        )

        with get_engine().begin() as connection:
            test_data = connection.execute(query)

        for t_data, c_object in zip(test_data, created_objects):
            t_data_id, t_data_board = t_data
            assert t_data_id == c_object.id
            assert t_data_board == c_object.board


class TestJsonField(TestCase):
    def test_model_creates(self):
        """
        It's important that the field not cause the project to fail startup.
        """
        assert JsonModel.sa is not None
