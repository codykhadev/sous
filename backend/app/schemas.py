from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthOut(BaseModel):
    status: str
    database: str


class RecipeIn(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    source_type: Literal["manual", "url", "video"] = "manual"
    source_url: str | None = None
    image_url: str | None = None
    servings: int | None = Field(default=None, ge=1, le=1000)
    total_minutes: int | None = Field(default=None, ge=0, le=100_000)
    tags: list[str] = []
    ingredients: list[str] = []
    steps: list[str] = []

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title can't be empty")
        return value

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str]) -> list[str]:
        cleaned = [t.strip().lower()[:50] for t in value if t.strip()]
        return list(dict.fromkeys(cleaned))

    @field_validator("ingredients", "steps")
    @classmethod
    def drop_blank_lines(cls, value: list[str]) -> list[str]:
        return [line.strip() for line in value if line.strip()]


class ParsedIngredientOut(BaseModel):
    raw: str
    quantity: float | None
    quantity_max: float | None
    unit: str | None
    name: str | None
    note: str | None


class IngredientOut(ParsedIngredientOut):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int


class StepOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    text: str


class RecipeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    image_url: str | None
    servings: int | None
    total_minutes: int | None
    tags: list[str]


class RecipeOut(RecipeSummary):
    source_type: str
    source_url: str | None
    created_at: datetime
    updated_at: datetime
    ingredients: list[IngredientOut]
    steps: list[StepOut]


class ImportUrlIn(BaseModel):
    url: str


class ParseIngredientsIn(BaseModel):
    lines: list[str]
