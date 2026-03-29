"""End-to-end tests using the real client against the live MLB Stats API.

Run with: pytest tests/test_integration/test_e2e.py -m integration
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def client():
    from mlb_statsapi.client.sync_client import MlbClient

    with MlbClient() as c:
        yield c


class TestScheduleE2E:
    def test_fetch_opening_day_2024(self, client):
        schedule = client.schedule(date="03/28/2024")
        assert len(schedule.dates) == 1
        assert len(schedule.dates[0].games) > 0
        game = schedule.dates[0].games[0]
        assert game.status.abstract_game_state == "Final"
        assert game.teams.away.team.name is not None
        assert game.teams.home.team.name is not None

    def test_fetch_july_4th_2024(self, client):
        schedule = client.schedule(date="07/04/2024")
        games = schedule.dates[0].games
        assert len(games) >= 5  # Full slate on July 4th
        for game in games:
            assert game.game_pk > 0
            assert game.venue.name is not None

    def test_fetch_date_range(self, client):
        schedule = client.schedule(start_date="09/28/2024", end_date="09/30/2024")
        assert len(schedule.dates) == 3
        for date in schedule.dates:
            assert len(date.games) > 0

    def test_fetch_team_schedule(self, client):
        schedule = client.schedule(team_id=147, date="06/15/2024")  # Yankees
        assert len(schedule.dates) == 1
        games = schedule.dates[0].games
        assert len(games) >= 1
        team_ids = {g.teams.away.team.id for g in games} | {
            g.teams.home.team.id for g in games
        }
        assert 147 in team_ids


class TestTeamsE2E:
    def test_fetch_all_teams(self, client):
        teams = client.teams()
        assert len(teams.teams) == 30
        names = {t.name for t in teams.teams}
        assert "New York Yankees" in names or "Yankees" in names

    def test_fetch_single_team(self, client):
        result = client.team(team_id=137)  # Giants
        assert len(result.teams) == 1
        assert result.teams[0].abbreviation == "SF"


class TestPlayerE2E:
    def test_fetch_ohtani(self, client):
        result = client.person(person_id=660271)
        ohtani = result.people[0]
        assert ohtani.full_name == "Shohei Ohtani"
        assert ohtani.bat_side.code == "L"
        assert ohtani.pitch_hand.code == "R"
        assert ohtani.primary_position is not None
        assert ohtani.birth_country == "Japan"

    def test_fetch_judge(self, client):
        result = client.person(person_id=592450)
        judge = result.people[0]
        assert judge.full_name == "Aaron Judge"
        assert judge.bat_side.code == "R"


class TestStandingsE2E:
    def test_fetch_2024_standings(self, client):
        standings = client.standings(season=2024)
        assert len(standings.records) == 6
        for record in standings.records:
            assert len(record.team_records) == 5
            first = record.team_records[0]
            assert first.division_rank == "1"
            assert first.league_record.wins > 0


class TestGameDataE2E:
    def test_boxscore(self, client):
        """Fetch boxscore for a known completed game."""
        box = client.boxscore(game_pk=744914)
        assert box.teams.away.team.id == 117  # Astros
        assert box.teams.home.team.id == 141  # Blue Jays
        assert len(box.teams.away.players) > 0
        assert len(box.teams.away.batting_order) == 9

    def test_linescore(self, client):
        ls = client.linescore(game_pk=744914)
        assert len(ls.innings) == 9
        assert ls.teams.away.runs == 3
        assert ls.teams.home.runs == 1

    def test_live_feed(self, client):
        feed = client.game(game_pk=744914)
        assert feed.game_pk == 744914
        assert feed.game_data.status.abstract_game_state == "Final"
        # Verify plays are fully parsed
        plays = feed.live_data.plays
        assert len(plays.all_plays) > 0
        assert len(plays.scoring_plays) > 0
        # Verify a pitch has data
        first_play = plays.all_plays[0]
        pitches = [e for e in first_play.play_events if e.is_pitch]
        assert len(pitches) > 0
        assert pitches[0].pitch_data.start_speed > 0

    def test_live_feed_decisions(self, client):
        feed = client.game(game_pk=744914)
        d = feed.live_data.decisions
        assert d.winner.full_name == "Hunter Brown"
        assert d.loser is not None
        assert d.save is not None


class TestLeagueLeadersE2E:
    def test_hr_leaders_2024(self, client):
        result = client.league_leaders(
            leader_categories="homeRuns", season=2024, limit=5
        )
        assert len(result.league_leaders) > 0
        leaders = result.league_leaders[0].leaders
        assert len(leaders) >= 5  # Ties can expand beyond limit
        assert leaders[0].rank == 1
        assert leaders[0].person.full_name == "Aaron Judge"
        assert int(leaders[0].value) >= 50


class TestFullGameWorkflow:
    """Simulate a real usage workflow: find a game, then drill into it."""

    def test_find_game_and_get_details(self, client):
        # 1. Find games on a date
        schedule = client.schedule(date="07/01/2024")
        games = schedule.dates[0].games
        game = games[0]

        # 2. Get boxscore for that game
        box = client.boxscore(game_pk=game.game_pk)
        assert box.teams.away.team.id == game.teams.away.team.id
        assert box.teams.home.team.id == game.teams.home.team.id

        # 3. Get linescore
        ls = client.linescore(game_pk=game.game_pk)
        assert ls.teams.away.runs is not None

        # 4. Get full live feed with plays
        feed = client.game(game_pk=game.game_pk)
        assert len(feed.live_data.plays.all_plays) > 0
