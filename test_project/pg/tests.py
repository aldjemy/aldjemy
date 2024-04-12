from django.db import transaction
from django.test import TestCase, TransactionTestCase
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import array

from aldjemy.core import get_engine
from aldjemy.session import get_session
from test_project.pg.models import (
    DateRangeModel,
    DecimalArrayModel,
    JsonModel,
    TicTacToeBoard,
)


class TestArrayField(TransactionTestCase):
    """
    Tests that queries involving array fields can be performed.
    """

    databases = ["pg"]

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

        session = get_session("pg")
        test_object = session.get(TicTacToeBoard.sa, created_objects[0].id)
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
            select(TicTacToeBoard.sa.id, TicTacToeBoard.sa.board)
            .order_by(TicTacToeBoard.sa.id)
            .limit(10)
        )

        with get_engine("pg").begin() as connection:
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


class TestDateRangeField(TestCase):
    def test_model_creates(self):
        assert DateRangeModel.sa is not None


class TestDecimalArrayField(TestCase):
    def test_model_creates(self):
        assert DecimalArrayModel.sa is not None


class RegressionTests(TestCase):
    databases = ["pg"]

    def test_transaction_is_not_rolled_back(self):
        """
        https://github.com/aldjemy/aldjemy/issues/173
        We are using savepoints in the hope of reproducing the conditions
        that helped us identify a regression introduced by SQLAlchemy 1.4.

        A ROLLBACK is emitted on every re-usage of a connection.
        This is undesirable, since we assume django owns the connection
        and the transaction state that comes with it.
        """
        board = [" "] * 9
        with transaction.atomic("pg"):
            tic_tac_toe = TicTacToeBoard.objects.create(board=board)
            # Just initiate a connection with SQLA, because the transation is rollback
            # the data we just created with django ORM is not available
            # Hence sqlalchemy.exc.NoResultFound is raised

            # if the exception is not raised, we assume, no ROLLBACK is emitted,
            # Indicating we successfully disabled the ROLLBACK.
            TicTacToeBoard.sa.query().filter(
                TicTacToeBoard.sa.id == tic_tac_toe.id
            ).one()
