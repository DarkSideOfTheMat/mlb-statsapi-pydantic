# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Pydantic v2 models for all major MLB Stats API endpoints
- Sync and async HTTP clients (`MlbClient`, `AsyncMlbClient`)
- Full enum coverage for API codes and types
- Endpoint registry with URL building and parameter validation
- Comprehensive test suite with fixture-based model validation
- PEP 561 `py.typed` marker for downstream type checking
- CI/CD with GitHub Actions (lint, type check, test, publish)
