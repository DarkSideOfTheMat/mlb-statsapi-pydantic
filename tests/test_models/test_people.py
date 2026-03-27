"""Tests for people models."""

from __future__ import annotations

import datetime

from tests.conftest import load_fixture


class TestPerson:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.people import Person

        data = load_fixture("people_660271")
        person = Person.model_validate(data["people"][0])
        assert person.id == 660271
        assert person.full_name == "Shohei Ohtani"
        assert person.first_name == "Shohei"
        assert person.last_name == "Ohtani"
        assert person.primary_number == "17"
        assert person.active is True

    def test_birth_info(self):
        from mlb_statsapi.models.people import Person

        data = load_fixture("people_660271")
        person = Person.model_validate(data["people"][0])
        assert person.birth_date == datetime.date(1994, 7, 5)
        assert person.current_age == 31
        assert person.birth_city == "Oshu"
        assert person.birth_country == "Japan"

    def test_physical_attributes(self):
        from mlb_statsapi.models.people import Person

        data = load_fixture("people_660271")
        person = Person.model_validate(data["people"][0])
        assert person.height == '6\' 4"'
        assert person.weight == 210

    def test_primary_position(self):
        from mlb_statsapi.models.people import Person

        data = load_fixture("people_660271")
        person = Person.model_validate(data["people"][0])
        assert person.primary_position.code == "Y"
        assert person.primary_position.name == "Two-Way Player"
        assert person.primary_position.abbreviation == "TWP"

    def test_bat_side_pitch_hand(self):
        from mlb_statsapi.models.people import Person

        data = load_fixture("people_660271")
        person = Person.model_validate(data["people"][0])
        assert person.bat_side.code == "L"
        assert person.bat_side.description == "Left"
        assert person.pitch_hand.code == "R"
        assert person.pitch_hand.description == "Right"

    def test_mlb_debut(self):
        from mlb_statsapi.models.people import Person

        data = load_fixture("people_660271")
        person = Person.model_validate(data["people"][0])
        assert person.mlb_debut_date == datetime.date(2018, 3, 29)

    def test_nickname(self):
        from mlb_statsapi.models.people import Person

        data = load_fixture("people_660271")
        person = Person.model_validate(data["people"][0])
        assert person.nick_name == "Showtime"

    def test_strike_zone(self):
        from mlb_statsapi.models.people import Person

        data = load_fixture("people_660271")
        person = Person.model_validate(data["people"][0])
        assert person.strike_zone_top == 3.369
        assert person.strike_zone_bottom == 1.7


class TestPeopleResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.people import PeopleResponse

        data = load_fixture("people_660271")
        resp = PeopleResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.people) == 1
        assert resp.people[0].full_name == "Shohei Ohtani"
