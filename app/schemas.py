from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


# ==============================
# REQUIREMENT SCHEMAS
# ==============================

class RequirementBase(SQLModel):
    title: str
    description: str
    priority: str = "Medium"
    status: str = "Draft"


class RequirementCreate(RequirementBase):
    pass


class RequirementRead(RequirementBase):
    id: int
    requirement_key: str
    created_at: datetime
    updated_at: datetime


class RequirementUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


# ==============================
# TEST CASE SCHEMAS
# ==============================

class TestCaseBase(SQLModel):
    requirement_id: int
    title: str
    description: str
    preconditions: Optional[str] = None
    test_steps: str
    expected_result: str
    priority: str = "Medium"
    status: str = "Draft"


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseRead(TestCaseBase):
    id: int
    test_case_key: str
    created_at: datetime
    updated_at: datetime


class TestCaseUpdate(SQLModel):
    requirement_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    preconditions: Optional[str] = None
    test_steps: Optional[str] = None
    expected_result: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class DefectBase(SQLModel):
    test_case_id: int
    title: str
    description: str
    severity: str = "Medium"
    priority: str = "Medium"
    status: str = "Open"
    assigned_to: str = "Unassigned"


class DefectCreate(DefectBase):
    pass


class DefectRead(DefectBase):
    id: int
    defect_key: str
    created_at: datetime
    updated_at: datetime


class DefectUpdate(SQLModel):
    test_case_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None