from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Recipe
from ..schemas import ImportUrlIn, ParsedIngredientOut, ParseIngredientsIn, RecipeIn
from ..services import scrape
from ..services.ingredients import parse_ingredient

router = APIRouter(tags=["import"])


@router.post("/import/url", response_model=RecipeIn)
def import_url(data: ImportUrlIn, db: Session = Depends(get_db)) -> RecipeIn:
    try:
        url = scrape.normalize_url(data.url)
        existing = db.scalar(select(Recipe.id).where(Recipe.source_url == url))
        if existing is not None:
            raise HTTPException(
                409, {"message": "You've already imported this recipe.", "recipe_id": existing}
            )
        return scrape.scrape_recipe(url)
    except scrape.ScrapeError as exc:
        raise HTTPException(422, {"message": str(exc)}) from exc


@router.post("/ingredients/parse", response_model=list[ParsedIngredientOut])
def parse_ingredients(data: ParseIngredientsIn) -> list[ParsedIngredientOut]:
    return [ParsedIngredientOut(raw=line, **vars(parse_ingredient(line))) for line in data.lines]
