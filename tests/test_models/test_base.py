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
