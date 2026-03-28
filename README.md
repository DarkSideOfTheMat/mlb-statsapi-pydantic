# mlb-statsapi-pydantic

[![CI](https://github.com/DarkSideOfTheMat/mlb-statsapi-pydantic/actions/workflows/ci.yml/badge.svg)](https://github.com/DarkSideOfTheMat/mlb-statsapi-pydantic/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mlb-statsapi-pydantic)](https://pypi.org/project/mlb-statsapi-pydantic/)
[![Python](https://img.shields.io/pypi/pyversions/mlb-statsapi-pydantic)](https://pypi.org/project/mlb-statsapi-pydantic/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pydantic v2 typed client for the [MLB Stats API](https://statsapi.mlb.com/api/).

Every response is parsed into fully-typed Pydantic models with `extra="allow"` for forward compatibility. Includes both sync and async clients.

## Install

```bash
pip install mlb-statsapi-pydantic
```

## Quick start

```python
from mlb_statsapi import MlbClient

client = MlbClient()

# Today's schedule
schedule = client.schedule(date="07/01/2024")
for date in schedule.dates:
    for game in date.games:
        print(f"{game.teams.away.team.name} @ {game.teams.home.team.name}")

# Team roster
roster = client.roster(team_id=147)  # Yankees
for entry in roster.roster:
    print(f"{entry.person.full_name} — {entry.position.abbreviation}")

# Player stats
stats = client.player_stats(person_id=660271, group="hitting", type="season")
for split in stats.stats[0].splits:
    print(f"{split.season}: {split.stat}")

# Live game feed
feed = client.live_feed(game_pk=745570)
for play in feed.live_data.plays.all_plays:
    if play.result and play.result.description:
        print(play.result.description)
```

### Async

```python
import asyncio
from mlb_statsapi import AsyncMlbClient

async def main():
    async with AsyncMlbClient() as client:
        schedule = await client.schedule(date="07/01/2024")
        print(schedule.dates[0].games[0].teams.home.team.name)

asyncio.run(main())
```

## Features

- Fully-typed Pydantic v2 models for all major endpoints
- Sync (`MlbClient`) and async (`AsyncMlbClient`) HTTP clients
- 25+ enum types for API codes (game type, pitch type, events, etc.)
- Endpoint registry with URL building and parameter validation
- `extra="allow"` on all models — new API fields won't break your code
- PEP 561 compatible (`py.typed`)

## Development

```bash
git clone https://github.com/DarkSideOfTheMat/mlb-statsapi-pydantic.git
cd mlb-statsapi-pydantic
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

### Run checks

```bash
ruff check src/ tests/       # lint
ruff format --check src/     # format check
mypy                         # type check
pytest -q                    # tests
pytest --cov -q              # tests with coverage
```

## License

[MIT](LICENSE)
