"""Watch a live MLB game using the LiveGameClient.

Demonstrates async callback registration, granularity configuration,
and the sync client wrapper.

Usage:
    python examples/live_game.py 824782
    python examples/live_game.py 824782 --scoring-only
    python examples/live_game.py --today
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date

from mlb_statsapi import (
    FetchGranularity,
    GameEvent,
    GameEventData,
    LiveGameClient,
    LiveGameConfig,
    MlbClient,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)


async def watch_game(game_pk: int, granularity: FetchGranularity) -> None:
    """Watch a game and print events as they happen."""
    config = LiveGameConfig(granularity=granularity)

    async with LiveGameClient(game_pk=game_pk, config=config) as client:

        @client.on(GameEvent.GAME_START)
        async def on_start(event: GameEventData) -> None:
            gd = event.feed.game_data if event.feed else None
            if gd and gd.teams and gd.teams.away and gd.teams.home:
                away = gd.teams.away.name
                home = gd.teams.home.name
                print(f"\n{'=' * 50}")
                print(f"  Game started: {away} @ {home}")
                print(f"{'=' * 50}\n")

        @client.on(GameEvent.PITCH)
        async def on_pitch(event: GameEventData) -> None:
            pe = event.play_event
            if pe and pe.details:
                desc = pe.details.description or "Pitch"
                count = pe.count
                count_str = f" ({count.balls}-{count.strikes})" if count else ""
                print(f"  {desc}{count_str}")

        @client.on(GameEvent.PLAY_COMPLETE)
        async def on_play(event: GameEventData) -> None:
            play = event.play
            if play and play.result:
                desc = play.result.description or play.result.event
                print(f"  >> {desc}")

        @client.on(GameEvent.RUN)
        async def on_run(event: GameEventData) -> None:
            ls = (
                event.feed.live_data.linescore
                if event.feed and event.feed.live_data
                else None
            )
            if ls and ls.teams:
                away = ls.teams.away.runs or 0
                home = ls.teams.home.runs or 0
                print(f"  *** Score: {away} - {home} ***")

        @client.on(GameEvent.INNING_CHANGE)
        async def on_inning(event: GameEventData) -> None:
            ls = (
                event.feed.live_data.linescore
                if event.feed and event.feed.live_data
                else None
            )
            if ls:
                half = ls.inning_half or "Top"
                inning = ls.current_inning or "?"
                print(f"\n--- {half} {inning} ---")

        @client.on(GameEvent.GAME_END)
        async def on_end(event: GameEventData) -> None:
            ls = (
                event.feed.live_data.linescore
                if event.feed and event.feed.live_data
                else None
            )
            if ls and ls.teams:
                away = ls.teams.away.runs or 0
                home = ls.teams.home.runs or 0
                print(f"\n{'=' * 50}")
                print(f"  Final: {away} - {home}")
                print(f"{'=' * 50}")

        print(f"Watching game {game_pk} ({granularity}) ...")
        await client.watch()


def show_todays_games() -> None:
    """List today's games with game PKs."""
    today = date.today().strftime("%m/%d/%Y")
    with MlbClient() as client:
        schedule = client.schedule(date=today)

    if not schedule.dates:
        print("No games scheduled today.", file=sys.stderr)
        return

    print(f"Games for {schedule.dates[0].date}:\n", file=sys.stderr)
    for game in schedule.dates[0].games:
        status = game.status.detailed_state if game.status else "?"
        away = game.teams.away.team.name
        home = game.teams.home.team.name
        print(f"  {game.game_pk}  {away} @ {home}  [{status}]", file=sys.stderr)

    print("\nUsage: python examples/live_game.py <game_pk>", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch a live MLB game")
    parser.add_argument("game_pk", nargs="?", type=int, help="Game primary key")
    parser.add_argument("--today", action="store_true", help="Show today's games")
    parser.add_argument(
        "--scoring-only",
        action="store_true",
        help="Only fetch on scoring events (less bandwidth)",
    )
    args = parser.parse_args()

    if args.today or args.game_pk is None:
        show_todays_games()
    else:
        gran = (
            FetchGranularity.SCORING_ONLY
            if args.scoring_only
            else FetchGranularity.EVERY_PITCH
        )
        asyncio.run(watch_game(args.game_pk, gran))
