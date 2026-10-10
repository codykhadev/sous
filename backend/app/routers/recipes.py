from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Ingredient, Recipe, Step
from ..schemas import RecipeIn, RecipeOut, RecipeSummary
from ..services.ingredients import parse_ingredient

router = APIRouter(prefix="/recipes", tags=["recipes"])


def _get_recipe(db: Session, recipe_id: int) -> Recipe:
    recipe = db.scalar(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(selectinload(Recipe.ingredients), selectinload(Recipe.steps))
    )
    if recipe is None:
        raise HTTPException(404, "Recipe not found")
    return recipe


def _apply(recipe: Recipe, data: RecipeIn) -> None:
    for field in ("title", "source_type", "source_url", "image_url", "servings", "total_minutes", "tags"):
        setattr(recipe, field, getattr(data, field))
    recipe.ingredients = [
        Ingredient(position=i, raw=line, **vars(parse_ingredient(line)))
        for i, line in enumerate(data.ingredients)
    ]
    recipe.steps = [Step(position=i, text=text) for i, text in enumerate(data.steps)]


@router.get("", response_model=list[RecipeSummary])
def list_recipes(q: str | None = None, tag: str | None = None, db: Session = Depends(get_db)) -> list[Recipe]:
    query = select(Recipe).order_by(Recipe.created_at.desc(), Recipe.id.desc())
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        in_ingredients = (
            select(Ingredient.id)
            .where(Ingredient.recipe_id == Recipe.id, Ingredient.raw.ilike(pattern))
            .exists()
        )
        query = query.where(or_(Recipe.title.ilike(pattern), in_ingredients))
    if tag:
        query = query.where(Recipe.tags.contains([tag.lower()]))
    return list(db.scalars(query))


@router.get("/tags", response_model=list[str])
def list_tags(db: Session = Depends(get_db)) -> list[str]:
    tag = func.unnest(Recipe.tags).label("tag")
    return list(db.scalars(select(tag).distinct().order_by(tag)))


@router.post("", response_model=RecipeOut, status_code=201)
def create_recipe(data: RecipeIn, db: Session = Depends(get_db)) -> Recipe:
    recipe = Recipe()
    _apply(recipe, data)
    db.add(recipe)
    db.commit()
    return _get_recipe(db, recipe.id)


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> Recipe:
    return _get_recipe(db, recipe_id)


@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, data: RecipeIn, db: Session = Depends(get_db)) -> Recipe:
    recipe = _get_recipe(db, recipe_id)
    _apply(recipe, data)
    db.commit()
    db.expire_all()
    return _get_recipe(db, recipe_id)


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)) -> Response:
    db.delete(_get_recipe(db, recipe_id))
    db.commit()
    return Response(status_code=204)
