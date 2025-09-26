from typing import List
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import select

from app.deps import DB
from app.models import Mission, Target, Cat
from app.schemas import MissionCreate, MissionOut, AssignCatIn, TargetUpdate, TargetOut


router = APIRouter(prefix="/missions", tags=["missions"])


def mission_complete_if_needed(mission: Mission):
    if not mission.completed and mission.targets and all(t.completed for t in mission.targets):
        mission.completed = True


def assert_target_mutable(mission: Mission, target: Target):
    if mission.completed or target.completed:
        raise HTTPException(status_code=409, detail="Target notes are frozen (completed target or mission).")


@router.post("", response_model=MissionOut, status_code=201)
def create_mission(db: DB, payload: MissionCreate):
    if not (1 <= len(payload.targets) <= 3):
        raise HTTPException(422, "A mission must have between 1 and 3 targets.")
    mission = Mission(completed=False)
    for t in payload.targets:
        mission.targets.append(Target(name=t.name, country=t.country, notes=t.notes or ""))
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


@router.get("", response_model=List[MissionOut])
def list_missions(db: DB):
    return db.execute(select(Mission)).scalars().all()


@router.get("/{mission_id}", response_model=MissionOut)
def get_mission(db: DB, mission_id: int = Path(..., ge=1)):
    m = db.get(Mission, mission_id)
    if not m:
        raise HTTPException(404, "Mission not found")
    return m


@router.delete("/{mission_id}", status_code=204)
def delete_mission(db: DB, mission_id: int = Path(..., ge=1)):
    m = db.get(Mission, mission_id)
    if not m:
        raise HTTPException(404, "Mission not found")
    if m.cat_id is not None:
        raise HTTPException(409, "Mission already assigned to a cat")
    db.delete(m)
    db.commit()
    return


@router.patch("/{mission_id}/assign_cat", response_model=MissionOut)
def assign_cat(db: DB, mission_id: int = Path(..., ge=1), payload: AssignCatIn = ...):
    m = db.get(Mission, mission_id)
    if not m:
        raise HTTPException(404, "Mission not found")
    if m.cat_id is not None:
        raise HTTPException(409, "Mission already has a cat")

    cat = db.get(Cat, payload.cat_id)
    if not cat:
        raise HTTPException(404, "Cat not found")

    active = db.execute(
        select(Mission).where(Mission.cat_id == cat.id, Mission.completed == False)
    ).scalars().first()
    if active:
        raise HTTPException(409, "Cat already has an active mission")

    m.cat_id = cat.id
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.patch("/{mission_id}/targets/{target_id}", response_model=TargetOut)
def update_target(db: DB, mission_id: int = Path(..., ge=1), target_id: int = Path(..., ge=1), payload: TargetUpdate = ...):
    m = db.get(Mission, mission_id)
    if not m:
        raise HTTPException(404, "Mission not found")

    t = db.get(Target, target_id)
    if not t or t.mission_id != m.id:
        raise HTTPException(404, "Target not found")

    if payload.notes is not None:
        assert_target_mutable(m, t)
        t.notes = payload.notes

    if payload.completed is not None:
        if payload.completed and not t.completed:
            t.completed = True
        elif not payload.completed and t.completed:
            raise HTTPException(409, "Cannot reopen a completed target")

    mission_complete_if_needed(m)
    db.commit()
    db.refresh(t)
    return t
