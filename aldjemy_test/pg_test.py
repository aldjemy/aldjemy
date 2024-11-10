import pytest
from aldjemy.engine import create_engine
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import array

from aldjemy_test.pg.models import (
    DateRangeModel,
    DecimalArrayModel,
    JsonModel,
    TicTacToeBoard,
)


@pytest.mark.django_db(transaction=True, databases=["pg"])
class TestArrayField:
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

        engine = create_engine("pg")
        with Session(engine, future=True) as session:
            stmt = select(func.count()).select_from(TicTacToeBoard.sa)
            assert session.scalar(stmt.where(contains("x"))) == 2
            assert session.scalar(stmt.where(contains("o"))) == 2
            assert session.scalar(stmt.where(contains(" "))) == 3

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

        engine = create_engine("pg")
        with Session(engine, future=True) as session:
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

        engine = create_engine("pg")
        with engine.begin() as connection:
            test_data = connection.execute(query)

        for t_data, c_object in zip(test_data, created_objects):
            t_data_id, t_data_board = t_data
            assert t_data_id == c_object.id
            assert t_data_board == c_object.board


class TestJsonField:
    def test_model_creates(self):
        """
        It's important that the field not cause the project to fail startup.
        """
        assert JsonModel.sa is not None


class TestDateRangeField:
    def test_model_creates(self):
        assert DateRangeModel.sa is not None


class TestDecimalArrayField:
    def test_model_creates(self):
        assert DecimalArrayModel.sa is not None
