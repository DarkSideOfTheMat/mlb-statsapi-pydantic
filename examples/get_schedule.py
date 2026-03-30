from zoneinfo import ZoneInfo

from rich import print

from mlb_statsapi.client.sync_client import MlbClient
from mlb_statsapi.enums import GAME_TYPES, MLB_TEAM

EST = ZoneInfo("America/New_York")

# API works with context managers to exit gracefully
with MlbClient() as client:
    # get schedule for a single day
    opening_day = client.schedule(date="2026-03-25")
    print("Opening Day Schedule:\n", opening_day)

    # get schedule for a range
    opening_week = client.schedule(start_date="2026-03-25", end_date="2026-03-27")

    print("Schedule for Opening Week:")
    for day in opening_week.dates:
        print(f"\tGames on {day.date}:")
        for game in day.games:
            matchup = f"{game.teams.away.team.name} @ {game.teams.home.team.name}"
            game_time = None
            if game.game_date:
                game_time = game.game_date.astimezone(EST).time()
            print(f"\t\t {game_time} {matchup}")

    # get schedule for a specific team, note you need to provide
    # gameType to filter out spring training / post-season games
    print(client._resolve_endpoint("schedule"))
    giants_schedule = client.schedule(
        team_id=MLB_TEAM.SF,
        season=2026,
        gameTypes=GAME_TYPES.REGULAR_SEASON,
    )
    print("Giants Schedule")
    for giants_gameday in giants_schedule.dates:
        for game in giants_gameday.games:
            home = game.teams.home
            away = game.teams.away
            print(f"{giants_gameday.date} - {away.team.name} @ {home.team.name}")

    # hydrate schedule with additional team info
    ...
