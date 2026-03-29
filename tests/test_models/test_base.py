"""Tests for base models: MlbBaseModel, BaseResponse, IdNameLink, CodeDescription."""

from __future__ import annotations

import pytest


class TestMlbBaseModel:
    """Test MlbBaseModel configuration."""

    def test_camel_case_alias(self):
        """Model accepts camelCase input and exposes snake_case attributes."""
        from mlb_statsapi.models._base import MlbBaseModel

        class Sample(MlbBaseModel):
            first_name: str
            last_name: str

        obj = Sample.model_validate({"firstName": "Shohei", "lastName": "Ohtani"})
        assert obj.first_name == "Shohei"
        assert obj.last_name == "Ohtani"

    def test_populate_by_name(self):
        """Model also accepts snake_case input directly."""
        from mlb_statsapi.models._base import MlbBaseModel

        class Sample(MlbBaseModel):
            first_name: str

        obj = Sample.model_validate({"first_name": "Shohei"})
        assert obj.first_name == "Shohei"

    def test_extra_fields_allowed(self):
        """Unknown fields are stored, not rejected."""
        from mlb_statsapi.models._base import MlbBaseModel

        class Sample(MlbBaseModel):
            id: int

        obj = Sample.model_validate({"id": 1, "unknownField": "value"})
        assert obj.id == 1
        assert obj.model_extra is not None
        assert obj.model_extra["unknownField"] == "value"

    def test_dump_by_alias(self):
        """model_dump(by_alias=True) produces camelCase keys."""
        from mlb_statsapi.models._base import MlbBaseModel

        class Sample(MlbBaseModel):
            sort_order: int

        obj = Sample(sort_order=11)
        dumped = obj.model_dump(by_alias=True)
        assert "sortOrder" in dumped


class TestBaseResponse:
    """Test BaseResponse with copyright field."""

    def test_parse_copyright(self, sports_json):
        from mlb_statsapi.models._base import BaseResponse

        resp = BaseResponse.model_validate(sports_json)
        assert resp.copyright.startswith("Copyright")

    def test_requires_copyright(self):
        from mlb_statsapi.models._base import BaseResponse

        with pytest.raises(Exception):
            BaseResponse.model_validate({})


class TestIdNameLink:
    """Test the ubiquitous {id, name, link} reference pattern."""

    def test_full_reference(self):
        from mlb_statsapi.models._base import IdNameLink

        obj = IdNameLink.model_validate(
            {"id": 1, "name": "Major League Baseball", "link": "/api/v1/sports/1"}
        )
        assert obj.id == 1
        assert obj.name == "Major League Baseball"
        assert obj.link == "/api/v1/sports/1"

    def test_name_optional(self):
        """Some API refs omit name (e.g. springVenue)."""
        from mlb_statsapi.models._base import IdNameLink

        obj = IdNameLink.model_validate({"id": 4249, "link": "/api/v1/venues/4249"})
        assert obj.id == 4249
        assert obj.name is None

    def test_extra_fields_preserved(self):
        """Extended refs like springLeague include abbreviation."""
        from mlb_statsapi.models._base import IdNameLink

        obj = IdNameLink.model_validate(
            {
                "id": 114,
                "name": "Cactus League",
                "link": "/api/v1/league/114",
                "abbreviation": "CL",
            }
        )
        assert obj.model_extra["abbreviation"] == "CL"


class TestRef:
    """Test the generic Ref[IdT] pattern with typed IDs."""

    def test_ref_with_team_id(self):
        from mlb_statsapi.models._base import Ref, TeamId

        team = Ref[TeamId].model_validate(
            {"id": 147, "name": "New York Yankees", "link": "/api/v1/teams/147"}
        )
        assert team.id == 147
        assert team.name == "New York Yankees"

    def test_ref_with_venue_id(self):
        from mlb_statsapi.models._base import Ref, VenueId

        venue = Ref[VenueId].model_validate(
            {"id": 3313, "name": "Yankee Stadium", "link": "/api/v1/venues/3313"}
        )
        assert venue.id == 3313

    def test_ref_with_league_id(self):
        from mlb_statsapi.models._base import LeagueId, Ref

        league = Ref[LeagueId].model_validate(
            {"id": 103, "name": "American League", "link": "/api/v1/league/103"}
        )
        assert league.id == 103

    def test_ref_name_optional(self):
        from mlb_statsapi.models._base import Ref, VenueId

        venue = Ref[VenueId].model_validate({"id": 4249, "link": "/api/v1/venues/4249"})
        assert venue.name is None

    def test_ref_extra_fields_preserved(self):
        from mlb_statsapi.models._base import LeagueId, Ref

        obj = Ref[LeagueId].model_validate(
            {
                "id": 114,
                "name": "Cactus League",
                "link": "/api/v1/league/114",
                "abbreviation": "CL",
            }
        )
        assert obj.model_extra["abbreviation"] == "CL"

    def test_idnamelink_alias_works(self):
        """IdNameLink = Ref[int] should remain backwards compatible."""
        from mlb_statsapi.models._base import IdNameLink

        obj = IdNameLink.model_validate({"id": 1, "name": "Test", "link": "/test"})
        assert obj.id == 1


class TestListResponse:
    """Test the generic ListResponse[T] base class."""

    def test_items_property(self):
        from mlb_statsapi.models.sports import SportsResponse

        data = {
            "copyright": "Copyright MLB",
            "sports": [
                {
                    "id": 1,
                    "code": "mlb",
                    "link": "/api/v1/sports/1",
                    "name": "Major League Baseball",
                    "abbreviation": "MLB",
                    "sortOrder": 11,
                    "activeStatus": True,
                }
            ],
        }
        resp = SportsResponse.model_validate(data)
        assert resp.items == resp.sports
        assert len(resp.items) == 1
        assert resp.items[0].name == "Major League Baseball"

    def test_items_on_teams_response(self):
        from mlb_statsapi.models.teams import TeamsResponse
        from tests.conftest import load_fixture

        data = load_fixture("teams")
        resp = TeamsResponse.model_validate(data)
        assert resp.items == resp.teams
        assert len(resp.items) > 0

    def test_items_empty_list(self):
        from mlb_statsapi.models.venues import VenuesResponse

        data = {"copyright": "Copyright MLB", "venues": []}
        resp = VenuesResponse.model_validate(data)
        assert resp.items == []


class TestCodeDescription:
    """Test the {code, description} pattern used by batSide, pitchHand, etc."""

    def test_parse(self):
        from mlb_statsapi.models._base import CodeDescription

        obj = CodeDescription.model_validate({"code": "L", "description": "Left"})
        assert obj.code == "L"
        assert obj.description == "Left"

    def test_requires_both_fields(self):
        from mlb_statsapi.models._base import CodeDescription

        with pytest.raises(Exception):
            CodeDescription.model_validate({"code": "R"})


class TestRefInheritance:
    """Test that domain models inherit from Ref/PersonRef."""

    def test_team_is_ref(self):
        from mlb_statsapi.models._base import Ref
        from mlb_statsapi.models.teams import Team

        team = Team(id=147, name="New York Yankees", link="/api/v1/teams/147")
        assert isinstance(team, Ref)

    def test_venue_is_ref(self):
        from mlb_statsapi.models._base import Ref
        from mlb_statsapi.models.venues import Venue

        venue = Venue(id=3313, name="Yankee Stadium", link="/api/v1/venues/3313")
        assert isinstance(venue, Ref)

    def test_league_is_ref(self):
        from mlb_statsapi.models._base import Ref
        from mlb_statsapi.models.leagues import League

        league = League(id=103, name="American League", link="/api/v1/league/103")
        assert isinstance(league, Ref)

    def test_division_is_ref(self):
        from mlb_statsapi.models._base import Ref
        from mlb_statsapi.models.divisions import Division

        division = Division(id=200, name="AL West", link="/api/v1/divisions/200")
        assert isinstance(division, Ref)

    def test_sport_is_ref(self):
        from mlb_statsapi.models._base import Ref
        from mlb_statsapi.models.sports import Sport

        sport = Sport(id=1, name="MLB", link="/api/v1/sports/1")
        assert isinstance(sport, Ref)

    def test_person_is_person_ref(self):
        from mlb_statsapi.models._base import PersonRef
        from mlb_statsapi.models.people import Person

        person = Person(id=660271, full_name="Shohei Ohtani")
        assert isinstance(person, PersonRef)


class TestIsHydrated:
    """Test the is_hydrated property on Ref and PersonRef."""

    def test_bare_ref_not_hydrated(self):
        from mlb_statsapi.models._base import Ref, TeamId

        ref = Ref[TeamId](id=147, name="New York Yankees", link="/api/v1/teams/147")
        assert not ref.is_hydrated

    def test_team_without_extra_not_hydrated(self):
        from mlb_statsapi.models.teams import Team

        team = Team(id=147, name="New York Yankees", link="/api/v1/teams/147")
        assert not team.is_hydrated

    def test_team_with_data_is_hydrated(self):
        from mlb_statsapi.models.teams import Team

        team = Team(
            id=147,
            name="New York Yankees",
            link="/api/v1/teams/147",
            abbreviation="NYY",
        )
        assert team.is_hydrated

    def test_person_ref_not_hydrated(self):
        from mlb_statsapi.models._base import PersonRef

        ref = PersonRef(id=660271, full_name="Shohei Ohtani")
        assert not ref.is_hydrated

    def test_person_with_data_is_hydrated(self):
        from mlb_statsapi.models.people import Person

        person = Person(
            id=660271,
            full_name="Shohei Ohtani",
            first_name="Shohei",
            last_name="Ohtani",
        )
        assert person.is_hydrated
