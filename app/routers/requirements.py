from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from app.database import get_session
from app.models import Requirement
from app.schemas import RequirementCreate, RequirementRead, RequirementUpdate

router = APIRouter(prefix="/api/requirements", tags=["Requirements"])


@router.post("/", response_model=RequirementRead, status_code=201)
def create_requirement(
    payload: RequirementCreate,
    session: Session = Depends(get_session),
):
    requirement = Requirement(
        requirement_key=f"REQ-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        **payload.model_dump(),
    )

    session.add(requirement)
    session.commit()
    session.refresh(requirement)

    return requirement


@router.get("/", response_model=list[RequirementRead])
def list_requirements(
    session: Session = Depends(get_session),
):
    statement = select(Requirement).order_by(Requirement.id)
    return session.exec(statement).all()


@router.get("/{requirement_id}", response_model=RequirementRead)
def get_requirement(
    requirement_id: int,
    session: Session = Depends(get_session),
):
    requirement = session.get(Requirement, requirement_id)

    if requirement is None:
        raise HTTPException(
            status_code=404,
            detail="Requirement not found",
        )

    return requirement


@router.patch("/{requirement_id}", response_model=RequirementRead)
def update_requirement(
    requirement_id: int,
    payload: RequirementUpdate,
    session: Session = Depends(get_session),
):
    requirement = session.get(Requirement, requirement_id)

    if requirement is None:
        raise HTTPException(
            status_code=404,
            detail="Requirement not found",
        )

    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(requirement, field, value)

    requirement.updated_at = datetime.now(timezone.utc)

    session.add(requirement)
    session.commit()
    session.refresh(requirement)

    return requirement


@router.delete("/{requirement_id}", status_code=204)
def delete_requirement(
    requirement_id: int,
    session: Session = Depends(get_session),
):
    requirement = session.get(Requirement, requirement_id)

    if requirement is None:
        raise HTTPException(
            status_code=404,
            detail="Requirement not found",
        )

    session.delete(requirement)
    session.commit()

    return Response(status_code=204)