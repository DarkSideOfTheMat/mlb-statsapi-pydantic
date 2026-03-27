# mlb-statsapi-pydantic

Pydantic v2 typed client for the [MLB Stats API](https://statsapi.mlb.com/api/).

## Install

```bash
pip install mlb-statsapi-pydantic
```

## Usage

```python
from mlb_statsapi import MlbClient

client = MlbClient()
schedule = client.schedule(date="07/01/2024")
for date in schedule.dates:
    for game in date.games:
        print(f"{game.teams.away.team.name} @ {game.teams.home.team.name}")
```
