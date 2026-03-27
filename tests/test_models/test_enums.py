"""Tests for enum types."""

from __future__ import annotations


class TestGameType:
    def test_regular_season(self):
        from mlb_statsapi.models.enums import GameType

        assert GameType("R") == GameType.REGULAR_SEASON
        assert GameType.REGULAR_SEASON.value == "R"

    def test_spring_training(self):
        from mlb_statsapi.models.enums import GameType

        assert GameType("S") == GameType.SPRING_TRAINING

    def test_postseason_types(self):
        from mlb_statsapi.models.enums import GameType

        assert GameType("F").value == "F"  # Wild Card
        assert GameType("D").value == "D"  # Division Series
        assert GameType("L").value == "L"  # League Championship
        assert GameType("W").value == "W"  # World Series

    def test_is_string(self):
        from mlb_statsapi.models.enums import GameType

        assert isinstance(GameType.REGULAR_SEASON, str)
        assert GameType.REGULAR_SEASON == "R"


class TestAbstractGameState:
    def test_values(self):
        from mlb_statsapi.models.enums import AbstractGameState

        assert AbstractGameState("Preview") == AbstractGameState.PREVIEW
        assert AbstractGameState("Live") == AbstractGameState.LIVE
        assert AbstractGameState("Final") == AbstractGameState.FINAL

    def test_is_string(self):
        from mlb_statsapi.models.enums import AbstractGameState

        assert isinstance(AbstractGameState.FINAL, str)
        assert AbstractGameState.FINAL == "Final"


class TestHandCode:
    def test_values(self):
        from mlb_statsapi.models.enums import HandCode

        assert HandCode("L") == HandCode.LEFT
        assert HandCode("R") == HandCode.RIGHT
        assert HandCode("S") == HandCode.SWITCH

    def test_is_string(self):
        from mlb_statsapi.models.enums import HandCode

        assert isinstance(HandCode.LEFT, str)


class TestPositionType:
    def test_values(self):
        from mlb_statsapi.models.enums import PositionType

        assert PositionType("Pitcher") == PositionType.PITCHER
        assert PositionType("Catcher") == PositionType.CATCHER
        assert PositionType("Infielder") == PositionType.INFIELDER
        assert PositionType("Outfielder") == PositionType.OUTFIELDER
        assert PositionType("Hitter") == PositionType.HITTER
        assert PositionType("Runner") == PositionType.RUNNER

    def test_is_string(self):
        from mlb_statsapi.models.enums import PositionType

        assert isinstance(PositionType.PITCHER, str)
        assert PositionType.PITCHER == "Pitcher"
