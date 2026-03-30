from zoneinfo import ZoneInfo

from rich import print

from mlb_statsapi.client.sync_client import MlbClient
from mlb_statsapi.enums import GAME_TYPES, MLB_TEAM
from mlb_statsapi.models import Person

EST = ZoneInfo("America/New_York")

# API works with context managers to exit gracefully
with MlbClient() as client:
    # get schedule for a single day
    opening_day = client.schedule(date="2026-03-25")
    print("Opening Day Schedule:\n", opening_day)

    # get schedule for a range
    opening_week = client.schedule(start_date="2026-03-25", end_date="2026-03-27")

    print("\n\n-----------------\nSchedule for Opening Week:")
    for day in opening_week.dates:
        print(f"\tGames on {day.date}:")
        for game in day.games:
            matchup = f"{game.teams.away.team.name} @ {game.teams.home.team.name}"
            game_time = None
            if game.game_date:
                # Since we have formatted dates we can easily
                # adjust the timezone
                game_time = game.game_date.astimezone(EST).time()
            print(f"\t\t {game_time} {matchup}")

    # get schedule for a specific team, note you need to provide
    # gameType to filter out spring training / post-season games
    giants_schedule = client.schedule(
        team_id=MLB_TEAM.SF,
        season=2026,
        gameTypes=GAME_TYPES.REGULAR_SEASON,
        # optionally filter to a range (e.g. regular season games through end of april)
        start_date="2026-01-01",
        end_date="2026-04-30",
    )
    print(
        "\n\n-----------------\nGiants Schedule",
    )
    for giants_gameday in giants_schedule.dates:
        for game in giants_gameday.games:
            home = game.teams.home
            away = game.teams.away

            venue = game.venue.name

            # when we don't hydrate we only have access to fields from the Ref[TeamId]
            # so fields like team.abbreviations will be null
            print(
                f"{giants_gameday.date} - {away.team.name} @ {home.team.name} ({venue})"
            )

    # hydrate schedule with additional team info
    print("\n\n-----------------\n2014 World Series Pitcher Decisions")
    world_series_schedule = client.schedule(
        season=2014,
        gameTypes=GAME_TYPES.WORLD_SERIES,
        # decisions will add game.model_extra["decisions"]
        #   person will provide extra data instead of
        # team will expand the team obj so team.abbreviations
        #   will be available
        hydrate="decisions,person,team",
    )
    for date in world_series_schedule.dates:
        for game in date.games:
            home = game.teams.home
            away = game.teams.away

            # Since we hydrated team we have access to
            # fields which would normally be null
            home_shortname = home.team.club_name
            away_shortname = away.team.club_name

            _date = game.game_date.astimezone(EST).date()

            # We know there will be model_extra since we
            # hydrate decision, which returns more fields
            # for the game obj
            assert game.model_extra is not None

            # We can validate the hydrated info into
            # one of our models
            winning_pitcher = Person.model_validate(
                game.model_extra["decisions"]["winner"]
            )
            losing_pitcher = Person.model_validate(
                game.model_extra["decisions"]["loser"]
            )

            # we have last_init_name from hydrating person
            winning_pitcher_name = winning_pitcher.last_init_name
            losing_pitcher_name = losing_pitcher.last_init_name

            # Saves are optional
            save = game.model_extra["decisions"].get("save")
            if save is not None:
                save_pitcher = Person.model_validate(save)
                save_str = f" / S: {save_pitcher.last_init_name}"
            else:
                save_str = ""

            away_win = "(W) " if away.is_winner else ""
            home_win = "(W) " if home.is_winner else ""

            print(f"{game.description} - ({_date}) |", end=" ")
            print(f"{away_win}{away_shortname} @ {home_win}{home_shortname}")

            print(f"\tW: {winning_pitcher_name} / L:{losing_pitcher_name}{save_str}\n")
