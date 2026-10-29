from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import Requirement, TestCase

router = APIRouter(prefix="/api/rtm", tags=["Requirement Traceability Matrix"])


@router.get("/")
def get_traceability_matrix(session: Session = Depends(get_session)):
    requirements = session.exec(
        select(Requirement).order_by(Requirement.id)
    ).all()

    test_cases = session.exec(
        select(TestCase).order_by(TestCase.id)
    ).all()

    matrix = []

    for requirement in requirements:
        linked_test_cases = [
            {
                "id": test_case.id,
                "test_case_key": test_case.test_case_key,
                "title": test_case.title,
                "priority": test_case.priority,
                "status": test_case.status,
            }
            for test_case in test_cases
            if test_case.requirement_id == requirement.id
        ]

        matrix.append(
            {
                "requirement_id": requirement.id,
                "requirement_key": requirement.requirement_key,
                "requirement_title": requirement.title,
                "requirement_status": requirement.status,
                "test_cases": linked_test_cases,
                "test_case_count": len(linked_test_cases),
                "coverage_status": (
                    "Covered" if linked_test_cases else "Not Covered"
                ),
            }
        )

    total_requirements = len(requirements)
    covered_requirements = sum(
        1 for item in matrix if item["test_case_count"] > 0
    )

    coverage_percentage = (
        round((covered_requirements / total_requirements) * 100, 2)
        if total_requirements
        else 0.0
    )

    return {
        "total_requirements": total_requirements,
        "covered_requirements": covered_requirements,
        "uncovered_requirements": total_requirements - covered_requirements,
        "coverage_percentage": coverage_percentage,
        "traceability_matrix": matrix,
    }