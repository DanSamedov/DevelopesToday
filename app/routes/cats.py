from typing import List
import httpx
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import select

from app.deps import DB
from app.models import Cat, Mission
from app.schemas import CatCreate, CatOut, CatUpdate


router = APIRouter(prefix="/cats", tags=["cats"])


def validate_breed_with_catapi(breed_name: str) -> None:
    try:
        with httpx.Client(timeout=10) as client:
            r = client.get("https://api.thecatapi.com/v1/breeds")
            r.raise_for_status()
            names = {b.get("name", "").strip().lower() for b in r.json()}
        if breed_name.strip().lower() not in names:
            raise HTTPException(status_code=422, detail="Unknown cat breed per TheCatAPI")
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="TheCatAPI unavailable. Try again later.")


@router.post("", response_model=CatOut, status_code=201)
async def create_cat(db: DB, payload: CatCreate):
    validate_breed_with_catapi(payload.breed)
    cat = Cat(
        name=payload.name,
        years_experience=payload.years_experience,
        breed=payload.breed,
        salary=payload.salary,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("", response_model=List[CatOut])
def list_cats(db: DB):
    return db.execute(select(Cat)).scalars().all()


@router.get("/{cat_id}", response_model=CatOut)
def get_cat(db: DB, cat_id: int = Path(..., ge=1)):
    cat = db.get(Cat, cat_id)
    if not cat:
        raise HTTPException(404, "Cat not found")
    return cat


@router.patch("/{cat_id}", response_model=CatOut)
def update_cat_salary(db: DB, cat_id: int = Path(..., ge=1), payload: CatUpdate = ...):
    cat = db.get(Cat, cat_id)
    if not cat:
        raise HTTPException(404, "Cat not found")
    cat.salary = payload.salary
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{cat_id}", status_code=204)
def delete_cat(db: DB, cat_id: int = Path(..., ge=1)):
    cat = db.get(Cat, cat_id)
    if not cat:
        raise HTTPException(404, "Cat not found")
    assigned = db.execute(
        select(Mission).where(Mission.cat_id == cat_id, Mission.completed == False)
    ).scalars().first()
    if assigned:
        raise HTTPException(409, "Cat has an active mission")
    db.delete(cat)
    db.commit()
    return
