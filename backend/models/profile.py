from __future__ import annotations

from pydantic import BaseModel, Field, NonNegativeFloat


class EntrepreneurProfile(BaseModel):
    geo_id: str
    available_capital: NonNegativeFloat
    business_category: str
    skills: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    experience_years: NonNegativeFloat = 0
    operating_hours_per_week: NonNegativeFloat | None = None
    minimum_monthly_income: NonNegativeFloat = 0
    acceptable_debt: NonNegativeFloat | None = None
    mobility_km: NonNegativeFloat | None = None
    risk_tolerance: str = "MEDIUM"
