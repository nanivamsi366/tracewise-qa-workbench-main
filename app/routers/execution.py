from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import TestCase, TestExecution
from pydantic import BaseModel
from typing import Optional


router = APIRouter(
    prefix="/api/executions",
    tags=["Test Executions"],
)


class ExecutionCreate(BaseModel):
    test_case_id: int
    status: str = "Not Run"
    actual_result: Optional[str] = None
    execution_notes: Optional[str] = None
    executed_by: str = "QA Tester"


class ExecutionUpdate(BaseModel):
    status: Optional[str] = None
    actual_result: Optional[str] = None
    execution_notes: Optional[str] = None
    executed_by: Optional[str] = None


class ExecutionRead(ExecutionCreate):
    id: int
    executed_at: datetime


@router.post("/", response_model=ExecutionRead, status_code=201)
def create_execution(
    payload: ExecutionCreate,
    session: Session = Depends(get_session),
):
    test_case = session.get(TestCase, payload.test_case_id)

    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    execution = TestExecution(
        **payload.model_dump(),
        executed_at=datetime.now(timezone.utc),
    )

    session.add(execution)
    session.commit()
    session.refresh(execution)

    return execution


@router.get("/", response_model=list[ExecutionRead])
def list_executions(session: Session = Depends(get_session)):
    statement = select(TestExecution).order_by(TestExecution.id)
    return session.exec(statement).all()


@router.get("/{execution_id}", response_model=ExecutionRead)
def get_execution(
    execution_id: int,
    session: Session = Depends(get_session),
):
    execution = session.get(TestExecution, execution_id)

    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution


@router.patch("/{execution_id}", response_model=ExecutionRead)
def update_execution(
    execution_id: int,
    payload: ExecutionUpdate,
    session: Session = Depends(get_session),
):
    execution = session.get(TestExecution, execution_id)

    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(execution, field, value)

    execution.executed_at = datetime.now(timezone.utc)

    session.add(execution)
    session.commit()
    session.refresh(execution)

    return execution


@router.delete("/{execution_id}", status_code=204)
def delete_execution(
    execution_id: int,
    session: Session = Depends(get_session),
):
    execution = session.get(TestExecution, execution_id)

    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    session.delete(execution)
    session.commit()

    return None