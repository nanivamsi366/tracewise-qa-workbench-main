from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


def utc_now():
    return datetime.now(timezone.utc)


class Requirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    requirement_key: str = Field(
        index=True,
        unique=True,
        max_length=30,
    )

    title: str = Field(max_length=200)
    description: str

    priority: str = Field(default="Medium", max_length=20)
    status: str = Field(default="Draft", max_length=20)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class TestCase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    test_case_key: str = Field(
        index=True,
        unique=True,
        max_length=30,
    )

    requirement_id: int = Field(
        foreign_key="requirement.id",
        index=True,
    )

    title: str = Field(max_length=200)
    description: str

    preconditions: Optional[str] = None
    test_steps: str
    expected_result: str

    priority: str = Field(default="Medium", max_length=20)
    status: str = Field(default="Draft", max_length=20)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class TestExecution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    test_case_id: int = Field(foreign_key="testcase.id", index=True)

    status: str = Field(default="Not Run", max_length=20)
    actual_result: Optional[str] = None
    execution_notes: Optional[str] = None
    executed_by: str = Field(default="QA Tester", max_length=100)

    executed_at: datetime = Field(default_factory=utc_now)


class Defect(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    defect_key: str = Field(index=True, unique=True, max_length=30)

    test_case_id: int = Field(foreign_key="testcase.id", index=True)

    title: str = Field(max_length=200)
    description: str

    severity: str = Field(default="Medium", max_length=20)
    priority: str = Field(default="Medium", max_length=20)
    status: str = Field(default="Open", max_length=20)

    assigned_to: str = Field(default="Unassigned", max_length=100)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)