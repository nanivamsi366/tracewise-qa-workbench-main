from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Requirement, TestCase
from app.schemas import TestCaseCreate, TestCaseRead, TestCaseUpdate

router = APIRouter(
    prefix="/api/test-cases",
    tags=["Test Cases"],
)


def generate_test_case_key(session: Session) -> str:
    """Generate a unique test case key."""
    statement = select(TestCase.id).order_by(TestCase.id.desc())
    latest_id = session.exec(statement).first()

    next_id = (latest_id or 0) + 1
    candidate = f"TC-{next_id:04d}"

    # Avoid collisions if IDs or keys have been manually changed.
    while session.exec(
        select(TestCase.id).where(TestCase.test_case_key == candidate)
    ).first() is not None:
        next_id += 1
        candidate = f"TC-{next_id:04d}"

    return candidate


@router.post("/", response_model=TestCaseRead, status_code=201)
def create_test_case(
    payload: TestCaseCreate,
    session: Session = Depends(get_session),
):
    requirement = session.get(Requirement, payload.requirement_id)

    if requirement is None:
        raise HTTPException(
            status_code=404,
            detail="Requirement not found",
        )

    test_case = TestCase(
        test_case_key=generate_test_case_key(session),
        **payload.model_dump(),
    )

    session.add(test_case)
    session.commit()
    session.refresh(test_case)

    return test_case


@router.get("/", response_model=list[TestCaseRead])
def list_test_cases(
    session: Session = Depends(get_session),
):
    statement = select(TestCase).order_by(TestCase.id)
    return session.exec(statement).all()


@router.get("/{test_case_id}", response_model=TestCaseRead)
def get_test_case(
    test_case_id: int,
    session: Session = Depends(get_session),
):
    test_case = session.get(TestCase, test_case_id)

    if test_case is None:
        raise HTTPException(
            status_code=404,
            detail="Test case not found",
        )

    return test_case


@router.patch("/{test_case_id}", response_model=TestCaseRead)
def update_test_case(
    test_case_id: int,
    payload: TestCaseUpdate,
    session: Session = Depends(get_session),
):
    test_case = session.get(TestCase, test_case_id)

    if test_case is None:
        raise HTTPException(
            status_code=404,
            detail="Test case not found",
        )

    updates = payload.model_dump(exclude_unset=True)

    if "requirement_id" in updates:
        requirement = session.get(
            Requirement,
            updates["requirement_id"],
        )

        if requirement is None:
            raise HTTPException(
                status_code=404,
                detail="Requirement not found",
            )

    for field, value in updates.items():
        setattr(test_case, field, value)

    test_case.updated_at = datetime.now(timezone.utc)

    session.add(test_case)
    session.commit()
    session.refresh(test_case)

    return test_case


@router.delete("/{test_case_id}", status_code=204)
def delete_test_case(
    test_case_id: int,
    session: Session = Depends(get_session),
):
    test_case = session.get(TestCase, test_case_id)

    if test_case is None:
        raise HTTPException(
            status_code=404,
            detail="Test case not found",
        )

    session.delete(test_case)
    session.commit()

    return None