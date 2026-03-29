"""Available hydration options by endpoint.

Hydrations expand inline references into full objects via the
``?hydrate=`` query parameter. Pass these constants to the client's
``hydrate`` parameter for type-safe hydration requests.

Usage::

    from mlb_statsapi.models.hydrations import ScheduleHydrations

    client.schedule(sport_id=1, hydrate=ScheduleHydrations.TEAM)
    client.schedule(hydrate=[ScheduleHydrations.TEAM, ScheduleHydrations.VENUE])
"""


class ScheduleHydrations:
    """Hydrations for ``/api/v1/schedule``."""

    TEAM = "team"
    VENUE = "venue"
    PROBABLE_PITCHER = "probablePitcher"
    LINESCORE = "linescore"
    DECISIONS = "decisions"
    OFFICIALS = "officials"
    WEATHER = "weather"
    SERIES_STATUS = "seriesStatus"
    BROADCASTS = "broadcasts"


class TeamsHydrations:
    """Hydrations for ``/api/v1/teams``."""

    VENUE = "venue"
    LEAGUE = "league"
    DIVISION = "division"
    SPORT = "sport"
    STANDINGS = "standings"
    PERSON = "person"


class PeopleHydrations:
    """Hydrations for ``/api/v1/people``."""

    CURRENT_TEAM = "currentTeam"
    STATS = "stats"
    AWARDS = "awards"
    TRANSACTIONS = "transactions"
    DRAFT = "draft"


class StandingsHydrations:
    """Hydrations for ``/api/v1/standings``."""

    TEAM = "team"
    LEAGUE = "league"
    DIVISION = "division"
    CONFERENCE = "conference"


class VenueHydrations:
    """Hydrations for ``/api/v1/venues``."""

    LOCATION = "location"
    TIMEZONE = "timezone"
    METADATA = "metadata"
