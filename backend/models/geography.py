from __future__ import annotations

from pydantic import BaseModel, Field


class GeographicIdentity(BaseModel):
    geo_id: str
    state: str = "West Bengal"
    district: str
    locality: str
    locality_type: str
    census_code: str | None = None
    lgd_code: str | None = None
    block: str | None = None
    gram_panchayat: str | None = None
    municipality: str | None = None
    ward: str | None = None
    pin_codes: list[str] = Field(default_factory=list)
    latitude: float | None = None
    longitude: float | None = None
    aliases: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)
