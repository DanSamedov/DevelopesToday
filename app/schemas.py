from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CatBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    years_experience: int = Field(ge=0, le=60)
    breed: str = Field(min_length=1, max_length=100)
    salary: int = Field(ge=0, le=1_000_000)


class CatCreate(CatBase): pass


class CatUpdate(BaseModel):
    salary: int = Field(ge=0, le=1_000_000)


class CatOut(CatBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TargetIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    country: str = Field(min_length=1, max_length=80)
    notes: str = Field(default="", max_length=10_000)


class TargetOut(BaseModel):
    id: int
    name: str
    country: str
    notes: str
    completed: bool
    model_config = ConfigDict(from_attributes=True)


class MissionCreate(BaseModel):
    targets: List[TargetIn] = Field(min_length=1, max_length=3)


class MissionOut(BaseModel):
    id: int
    completed: bool
    cat_id: Optional[int]
    targets: List[TargetOut]
    model_config = ConfigDict(from_attributes=True)


class AssignCatIn(BaseModel):
    cat_id: int


class TargetUpdate(BaseModel):
    notes: Optional[str] = Field(default=None, max_length=10_000)
    completed: Optional[bool] = None
