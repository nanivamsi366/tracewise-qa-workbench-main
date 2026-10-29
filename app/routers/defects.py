from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Defect, TestCase
from app.schemas import DefectCreate, DefectRead, DefectUpdate

router = APIRouter(prefix="/api/defects", tags=["Defects"])


def generate_defect_key(session: Session) -> str:
    statement = select(Defect.id).order_by(Defect.id.desc())
    latest_id = session.exec(statement).first()
    next_id = (latest_id or 0) + 1

    candidate = f"BUG-{next_id:04d}"

    while session.exec(
        select(Defect.id).where(Defect.defect_key == candidate)
    ).first() is not None:
        next_id += 1
        candidate = f"BUG-{next_id:04d}"

    return candidate


@router.post("/", response_model=DefectRead, status_code=201)
def create_defect(
    payload: DefectCreate,
    session: Session = Depends(get_session),
):
    test_case = session.get(TestCase, payload.test_case_id)

    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    defect = Defect(
        defect_key=generate_defect_key(session),
        **payload.model_dump(),
    )

    session.add(defect)
    session.commit()
    session.refresh(defect)
    return defect


@router.get("/", response_model=list[DefectRead])
def list_defects(session: Session = Depends(get_session)):
    statement = select(Defect).order_by(Defect.id)
    return session.exec(statement).all()


@router.get("/{defect_id}", response_model=DefectRead)
def get_defect(
    defect_id: int,
    session: Session = Depends(get_session),
):
    defect = session.get(Defect, defect_id)

    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")

    return defect


@router.patch("/{defect_id}", response_model=DefectRead)
def update_defect(
    defect_id: int,
    payload: DefectUpdate,
    session: Session = Depends(get_session),
):
    defect = session.get(Defect, defect_id)

    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")

    updates = payload.model_dump(exclude_unset=True)

    if "test_case_id" in updates:
        test_case = session.get(TestCase, updates["test_case_id"])

        if test_case is None:
            raise HTTPException(status_code=404, detail="Test case not found")

    for field, value in updates.items():
        setattr(defect, field, value)

    defect.updated_at = datetime.now(timezone.utc)

    session.add(defect)
    session.commit()
    session.refresh(defect)

    return defect


@router.delete("/{defect_id}", status_code=204)
def delete_defect(
    defect_id: int,
    session: Session = Depends(get_session),
):
    defect = session.get(Defect, defect_id)

    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")

    session.delete(defect)
    session.commit()

    return None