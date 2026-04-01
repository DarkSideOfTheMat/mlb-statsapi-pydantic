# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.0.1] - 2026-03-31

Initial pre-release.

### Added

- Pydantic v2 models for all major MLB Stats API endpoints
- Sync and async HTTP clients (`MlbClient`, `AsyncMlbClient`)
- Convenience methods: `schedule`, `teams`, `team`, `person`, `standings`, `game`, `boxscore`, `linescore`, `league_leaders`
- Generic `get()` method for querying any registered endpoint
- Enum helpers for game types (`GAME_TYPES`) and team IDs (`MLB_TEAM`)
- Endpoint registry with URL building and parameter validation
- `extra="allow"` on all models for forward compatibility with API changes
- Comprehensive test suite with fixture-based model validation
- PEP 561 `py.typed` marker for downstream type checking
- CI/CD with GitHub Actions (lint, type check, test, publish)
- Trusted publishing workflow for PyPI releases

[Unreleased]: https://github.com/DarkSideOfTheMat/mlb-statsapi-pydantic/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/DarkSideOfTheMat/mlb-statsapi-pydantic/releases/tag/v0.0.1
