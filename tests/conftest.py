from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a JSON fixture file by name (without extension)."""
    path = FIXTURES_DIR / f"{name}.json"
    return json.loads(path.read_text())


@pytest.fixture()
def sports_json() -> dict:
    return load_fixture("sports")


@pytest.fixture()
def teams_json() -> dict:
    return load_fixture("teams")


@pytest.fixture()
def schedule_json() -> dict:
    return load_fixture("schedule")


@pytest.fixture()
def people_json() -> dict:
    return load_fixture("people_660271")


@pytest.fixture()
def standings_json() -> dict:
    return load_fixture("standings")
