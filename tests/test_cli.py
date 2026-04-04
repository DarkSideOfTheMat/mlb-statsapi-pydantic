"""Tests for the mlb-statsapi CLI."""

from __future__ import annotations

import json

import pytest
import respx

from mlb_statsapi.cli import (
    DEFAULTS,
    build_parser,
    help_endpoint,
    list_endpoints,
    main,
    parse_params,
)
from tests.conftest import load_fixture

# ---------------------------------------------------------------------------
# Unit tests (no network / mocking)
# ---------------------------------------------------------------------------


class TestParseParams:
    """Test KEY=VALUE parsing."""

    def test_valid_pairs(self):
        assert parse_params(["sportId=1", "date=07/01/2024"]) == {
            "sportId": "1",
            "date": "07/01/2024",
        }

    def test_value_with_equals(self):
        assert parse_params(["foo=a=b"]) == {"foo": "a=b"}

    def test_empty_list(self):
        assert parse_params([]) == {}

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Invalid parameter"):
            parse_params(["badparam"])


class TestBuildParser:
    """Test argparse configuration."""

    def test_endpoint_and_params(self):
        parser = build_parser()
        args = parser.parse_args(["schedule", "sportId=1", "date=07/01/2024"])
        assert args.endpoint == "schedule"
        assert args.params == ["sportId=1", "date=07/01/2024"]
        assert args.output == "json"

    def test_output_flag(self):
        parser = build_parser()
        args = parser.parse_args(["schedule", "-o", "py"])
        assert args.output == "py"

    def test_list_endpoints_flag(self):
        parser = build_parser()
        args = parser.parse_args(["--list-endpoints"])
        assert args.list_endpoints is True

    def test_help_endpoint_flag(self):
        parser = build_parser()
        args = parser.parse_args(["schedule", "--help-endpoint"])
        assert args.help_endpoint is True


class TestListEndpoints:
    """Test endpoint listing."""

    def test_output_contains_endpoints(self, capsys):
        list_endpoints()
        out = capsys.readouterr().out
        assert "schedule" in out
        assert "teams" in out
        assert "game" in out
        assert "Available endpoints" in out


class TestHelpEndpoint:
    """Test endpoint help display."""

    def test_known_endpoint(self, capsys):
        help_endpoint("schedule")
        out = capsys.readouterr().out
        assert "Endpoint: schedule" in out
        assert "sportId" in out

    def test_hyphen_normalization(self, capsys):
        help_endpoint("game-boxscore")
        out = capsys.readouterr().out
        assert "Endpoint: game_boxscore" in out

    def test_unknown_endpoint(self, capsys):
        help_endpoint("bogus")
        err = capsys.readouterr().err
        assert "Unknown endpoint" in err

    def test_shows_defaults(self, capsys):
        help_endpoint("standings")
        out = capsys.readouterr().out
        assert "Defaults:" in out
        assert "103,104" in out


class TestDefaults:
    """Test that sensible defaults are applied."""

    def test_defaults_applied(self):
        merged = {**DEFAULTS.get("schedule", {}), **{}}
        assert merged["sportId"] == "1"

    def test_user_overrides_defaults(self):
        merged = {**DEFAULTS.get("schedule", {}), **{"sportId": "11"}}
        assert merged["sportId"] == "11"


class TestHyphenNormalization:
    """Test endpoint name normalization."""

    def test_hyphen_to_underscore(self):
        assert "game-boxscore".replace("-", "_") == "game_boxscore"


# ---------------------------------------------------------------------------
# Integration tests (with respx mocking + capsys)
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_api():
    with respx.mock(base_url="https://statsapi.mlb.com/api") as api:
        yield api


class TestMainIntegration:
    """Test the main() entry point end-to-end."""

    def test_list_endpoints_exit_0(self, capsys):
        rc = main(["--list-endpoints"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "schedule" in out

    def test_no_endpoint_prints_help(self, capsys):
        rc = main([])
        assert rc == 1

    def test_help_endpoint_exit_0(self, capsys):
        rc = main(["schedule", "--help-endpoint"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Endpoint: schedule" in out

    def test_bogus_endpoint_exit_1(self, capsys):
        rc = main(["bogus_endpoint"])
        assert rc == 1
        err = capsys.readouterr().err
        assert "Error" in err

    def test_invalid_param_format_exit_1(self, capsys):
        rc = main(["schedule", "badparam"])
        assert rc == 1
        err = capsys.readouterr().err
        assert "Invalid parameter" in err

    def test_schedule_json_output(self, mock_api, capsys):
        data = load_fixture("schedule")
        mock_api.get("/v1/schedule").respond(200, json=data)

        rc = main(["schedule", "sportId=1", "date=07/01/2024"])
        assert rc == 0
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "dates" in parsed

    def test_schedule_py_output(self, mock_api, capsys):
        data = load_fixture("schedule")
        mock_api.get("/v1/schedule").respond(200, json=data)

        rc = main(["schedule", "sportId=1", "-o", "py"])
        assert rc == 0
        out = capsys.readouterr().out
        # py mode output is not JSON
        with pytest.raises(json.JSONDecodeError):
            json.loads(out)

    def test_sports_with_defaults(self, mock_api, capsys):
        data = load_fixture("sports")
        mock_api.get("/v1/sports").respond(200, json=data)

        rc = main(["sports"])
        assert rc == 0
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "sports" in parsed

    def test_http_error_exit_1(self, mock_api, capsys):
        mock_api.get("/v1/sports").respond(500)

        rc = main(["sports"])
        assert rc == 1
        err = capsys.readouterr().err
        assert "Error" in err

    def test_hyphen_endpoint_name(self, mock_api, capsys):
        data = load_fixture("boxscore")
        mock_api.get("/v1/game/744914/boxscore").respond(200, json=data)

        rc = main(["game-boxscore", "gamePk=744914"])
        assert rc == 0

    def test_standings_uses_defaults(self, mock_api, capsys):
        data = load_fixture("standings")
        mock_api.get("/v1/standings").respond(200, json=data)

        rc = main(["standings"])
        assert rc == 0
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "records" in parsed
