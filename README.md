# mlb-statsapi-pydantic

[![CI](https://github.com/DarkSideOfTheMat/mlb-statsapi-pydantic/actions/workflows/ci.yml/badge.svg)](https://github.com/DarkSideOfTheMat/mlb-statsapi-pydantic/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mlb-statsapi-pydantic)](https://pypi.org/project/mlb-statsapi-pydantic/)
[![Python](https://img.shields.io/pypi/pyversions/mlb-statsapi-pydantic)](https://pypi.org/project/mlb-statsapi-pydantic/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pydantic v2 typed client for the [MLB Stats API](https://statsapi.mlb.com/api/).

> **Note:** This project is in early pre-release. The API surface may change between versions.

Every response is parsed into fully-typed Pydantic models with `extra="allow"` for forward compatibility. Includes both sync and async clients.

## Install

```bash
pip install mlb-statsapi-pydantic
```

## Quick start

```python
from mlb_statsapi import MlbClient

with MlbClient() as client:
    # Today's schedule
    schedule = client.schedule(date="07/01/2024")
    for date in schedule.dates:
        for game in date.games:
            print(f"{game.teams.away.team.name} @ {game.teams.home.team.name}")

    # Team info
    teams = client.teams(sport_id=1)
    for team in teams.teams:
        print(f"{team.name} ({team.abbreviation})")

    # Standings
    standings = client.standings(season=2024)
    for record in standings.records:
        for entry in record.team_records:
            print(f"{entry.team.name}: {entry.wins}-{entry.losses}")

    # Live game data
    game = client.game(game_pk=745570)
    print(game.game_data.teams.home.name)
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

See `examples/` for more details

## Features

- Fully-typed Pydantic v2 models for all major endpoints
- Sync (`MlbClient`) and async (`AsyncMlbClient`) HTTP clients
- Enum helpers for game types and team IDs
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

## Copyright Notice

This package and its author are not affiliated with MLB or any MLB team. This API wrapper interfaces with MLB's Stats API. Use of MLB data is subject to the notice posted at <http://gdx.mlb.com/components/copyright.txt>.

This project is inspired by [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI) by Todd Roberts, licensed under GPL-3.0.

## License

[MIT](LICENSE)
