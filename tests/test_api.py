import pytest

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session
from unittest.mock import Mock
from app.routers.defects import generate_defect_key
from app.routers.test_cases import generate_test_case_key
import app.database as database
from unittest.mock import patch


# --------------------------------------------------
# TEST DATABASE SETUP
# --------------------------------------------------

@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()


# --------------------------------------------------
# BASIC API TESTS
# --------------------------------------------------

def test_swagger_openapi_is_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200


def test_list_requirements(client):
    response = client.get("/api/requirements/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_test_cases(client):
    response = client.get("/api/test-cases/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_executions(client):
    response = client.get("/api/executions/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_defects(client):
    response = client.get("/api/defects/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# --------------------------------------------------
# REQUIREMENT CREATION TEST
# --------------------------------------------------

def test_create_requirement(client):
    payload = {
        "title": "Automated Test Requirement",
        "description": "Requirement created by an automated API test",
        "priority": "High",
        "status": "Open",
    }

    response = client.post(
        "/api/requirements/",
        json=payload,
    )

    assert response.status_code in (200, 201), response.text

    data = response.json()

    assert data["title"] == payload["title"]
    assert "id" in data


# --------------------------------------------------
# REQUIREMENT TRACEABILITY MATRIX TEST
# --------------------------------------------------

def test_rtm_summary(client):
    response = client.get("/api/rtm/")

    assert response.status_code == 200, response.text

    data = response.json()

    assert "total_requirements" in data
    assert "covered_requirements" in data
    assert "uncovered_requirements" in data
    assert "coverage_percentage" in data
    assert "traceability_matrix" in data


# --------------------------------------------------
# TEST CASE CRUD TEST
# --------------------------------------------------

def test_test_case_crud(client):

    # 1. Create a requirement first
    requirement_payload = {
        "title": "Requirement for Automated Test Case",
        "description": "Created for CRUD testing",
        "priority": "High",
        "status": "Open",
    }

    requirement_response = client.post(
        "/api/requirements/",
        json=requirement_payload,
    )

    assert requirement_response.status_code in (200, 201), (
        requirement_response.text
    )

    requirement_id = requirement_response.json()["id"]

    # 2. Create a test case linked to the requirement
    test_case_payload = {
        "title": "Verify Login with Valid Credentials",
        "description": "Check that a valid user can log in",
        "test_steps": (
            "1. Open login page\n"
            "2. Enter valid credentials\n"
            "3. Click Login"
        ),
        "expected_result": "User logs in successfully",
        "requirement_id": requirement_id,
    }

    create_response = client.post(
        "/api/test-cases/",
        json=test_case_payload,
    )

    assert create_response.status_code in (200, 201), (
        create_response.text
    )

    test_case = create_response.json()
    test_case_id = test_case["id"]

    assert test_case["title"] == test_case_payload["title"]

    # 3. Retrieve the test case
    get_response = client.get(
        f"/api/test-cases/{test_case_id}"
    )

    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["id"] == test_case_id

    # 4. Update the test case title
    updated_title = "Verify Login - Updated"

    update_response = client.patch(
        f"/api/test-cases/{test_case_id}",
        json={"title": updated_title},
    )

    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["title"] == updated_title

    # 5. Delete the test case
    delete_response = client.delete(
        f"/api/test-cases/{test_case_id}"
    )

    assert delete_response.status_code in (200, 204), (
        delete_response.text
    )

    # 6. Confirm that the test case no longer exists
    final_response = client.get(
        f"/api/test-cases/{test_case_id}"
    )

    assert final_response.status_code == 404, final_response.text


# --------------------------------------------------
# DEFECT LIFECYCLE TEST
# --------------------------------------------------

def test_defect_lifecycle(client):

    # 1. Create a requirement
    requirement_payload = {
        "title": "Login Requirement for Defect Testing",
        "description": "Requirement for testing the defect lifecycle",
        "priority": "High",
        "status": "Open",
    }

    requirement_response = client.post(
        "/api/requirements/",
        json=requirement_payload,
    )

    assert requirement_response.status_code in (200, 201), (
        requirement_response.text
    )

    requirement_id = requirement_response.json()["id"]

    # 2. Create a test case
    test_case_payload = {
        "title": "Verify Login Error Handling",
        "description": "Verify the application handles login errors",
        "test_steps": (
            "1. Open the login page\n"
            "2. Enter invalid credentials\n"
            "3. Click Login"
        ),
        "expected_result": "An appropriate error message is displayed",
        "requirement_id": requirement_id,
    }

    test_case_response = client.post(
        "/api/test-cases/",
        json=test_case_payload,
    )

    assert test_case_response.status_code in (200, 201), (
        test_case_response.text
    )

    test_case_id = test_case_response.json()["id"]

    # 3. Report a defect
    defect_payload = {
        "test_case_id": test_case_id,
        "title": "Incorrect login error message",
        "description": (
            "The application displays an incorrect message "
            "when invalid credentials are entered."
        ),
        "severity": "Medium",
        "priority": "High",
        "status": "Open",
        "assigned_to": "QA Tester",
    }

    defect_response = client.post(
        "/api/defects/",
        json=defect_payload,
    )

    assert defect_response.status_code in (200, 201), (
        defect_response.text
    )

    defect = defect_response.json()
    defect_id = defect["id"]

    assert defect["title"] == defect_payload["title"]
    assert defect["status"] == "Open"
    assert defect["test_case_id"] == test_case_id

    # 4. Retrieve the defect
    get_response = client.get(
        f"/api/defects/{defect_id}"
    )

    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["id"] == defect_id

    # 5. Update the defect status
    update_response = client.patch(
        f"/api/defects/{defect_id}",
        json={"status": "Closed"},
    )

    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["status"] == "Closed"

    # 6. Verify the updated defect
    final_response = client.get(
        f"/api/defects/{defect_id}"
    )

    assert final_response.status_code == 200, final_response.text
    assert final_response.json()["status"] == "Closed"


# --------------------------------------------------
# TEST EXECUTION LIFECYCLE TEST
# --------------------------------------------------

def test_execution_lifecycle(client):

    # 1. Verify invalid test case ID returns 404
    invalid_create = client.post(
        "/api/executions/",
        json={"test_case_id": 9999}
    )
    assert invalid_create.status_code == 404

    # 2. Create a requirement
    requirement_response = client.post(
        "/api/requirements/",
        json={
            "title": "Execution Test Requirement",
            "description": "Requirement for execution testing",
            "priority": "High",
            "status": "Open",
        }
    )
    assert requirement_response.status_code in (200, 201)
    requirement_id = requirement_response.json()["id"]

    # 3. Create a test case
    test_case_response = client.post(
        "/api/test-cases/",
        json={
            "title": "Verify Login Execution",
            "description": "Test case for execution lifecycle",
            "test_steps": "1. Open login page\n2. Enter credentials",
            "expected_result": "User logs in successfully",
            "requirement_id": requirement_id,
        }
    )
    assert test_case_response.status_code in (200, 201)
    test_case_id = test_case_response.json()["id"]

    # 4. Create an execution
    create_response = client.post(
        "/api/executions/",
        json={
            "test_case_id": test_case_id,
            "status": "Passed",
            "actual_result": "Login successful",
            "execution_notes": "Executed successfully",
            "executed_by": "QA Tester",
        }
    )
    assert create_response.status_code == 201, create_response.text

    execution_id = create_response.json()["id"]
    assert create_response.json()["status"] == "Passed"

    # 5. Retrieve the execution
    get_response = client.get(
        f"/api/executions/{execution_id}"
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == execution_id

    # 6. Verify invalid execution ID returns 404
    invalid_get = client.get("/api/executions/9999")
    assert invalid_get.status_code == 404

    # 7. Partially update the execution
    update_response = client.patch(
        f"/api/executions/{execution_id}",
        json={"status": "Failed"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Failed"

    # 8. Verify invalid update returns 404
    invalid_update = client.patch(
        "/api/executions/9999",
        json={"status": "Passed"}
    )
    assert invalid_update.status_code == 404

    # 9. Delete the execution
    delete_response = client.delete(
        f"/api/executions/{execution_id}"
    )
    assert delete_response.status_code == 204

    # 10. Verify deleted execution returns 404
    final_response = client.get(
        f"/api/executions/{execution_id}"
    )
    assert final_response.status_code == 404

    # 11. Verify deleting invalid execution returns 404
    invalid_delete = client.delete("/api/executions/9999")
    assert invalid_delete.status_code == 404

def test_requirement_lifecycle(client):
    # 1. Create a requirement
    create_response = client.post(
        "/api/requirements/",
        json={
            "title": "Verify User Profile Update",
            "description": "Verify that users can update their profile details.",
            "priority": "High",
            "status": "Draft",
        },
    )

    assert create_response.status_code == 201
    requirement_id = create_response.json()["id"]

    # 2. List requirements
    list_response = client.get("/api/requirements/")
    assert list_response.status_code == 200
    assert any(
        item["id"] == requirement_id
        for item in list_response.json()
    )

    # 3. Retrieve the created requirement
    get_response = client.get(
        f"/api/requirements/{requirement_id}"
    )
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Verify User Profile Update"

    # 4. Retrieve a nonexistent requirement
    missing_get = client.get("/api/requirements/99999")
    assert missing_get.status_code == 404

    # 5. Update the requirement
    update_response = client.patch(
        f"/api/requirements/{requirement_id}",
        json={
            "status": "Open",
            "priority": "Medium",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Open"
    assert update_response.json()["priority"] == "Medium"

    # 6. Update a nonexistent requirement
    missing_update = client.patch(
        "/api/requirements/99999",
        json={"status": "Open"},
    )
    assert missing_update.status_code == 404

    # 7. Delete the created requirement
    delete_response = client.delete(
        f"/api/requirements/{requirement_id}"
    )
    assert delete_response.status_code == 204

    # 8. Verify the deleted requirement cannot be retrieved
    deleted_get = client.get(
        f"/api/requirements/{requirement_id}"
    )
    assert deleted_get.status_code == 404

    # 9. Delete a nonexistent requirement
    missing_delete = client.delete("/api/requirements/99999")
    assert missing_delete.status_code == 404

def test_defect_negative_scenarios(client):
    # 1. Create defect with nonexistent test case
    invalid_create = client.post(
        "/api/defects/",
        json={
            "test_case_id": 99999,
            "title": "Invalid test case defect",
            "description": "This should not be created.",
        },
    )
    assert invalid_create.status_code == 404

    # 2. Create a requirement
    requirement_response = client.post(
        "/api/requirements/",
        json={
            "title": "Defect Test Requirement",
            "description": "Requirement for defect testing.",
        },
    )
    assert requirement_response.status_code == 201
    requirement_id = requirement_response.json()["id"]

    # 3. Create a test case
    test_case_response = client.post(
        "/api/test-cases/",
        json={
            "requirement_id": requirement_id,
            "title": "Defect Test Case",
            "description": "Test case for defect lifecycle.",
            "test_steps": "Perform the test.",
            "expected_result": "Test passes.",
        },
    )
    assert test_case_response.status_code == 201
    test_case_id = test_case_response.json()["id"]

    # 4. Create a valid defect
    defect_response = client.post(
        "/api/defects/",
        json={
            "test_case_id": test_case_id,
            "title": "Profile update failure",
            "description": "Profile changes are not saved.",
        },
    )
    assert defect_response.status_code == 201
    defect_id = defect_response.json()["id"]

    # 5. Update defect using invalid test case ID
    invalid_update = client.patch(
        f"/api/defects/{defect_id}",
        json={"test_case_id": 99999},
    )
    assert invalid_update.status_code == 404
    assert invalid_update.json()["detail"] == "Test case not found"

    # 6. Update nonexistent defect
    missing_update = client.patch(
        "/api/defects/99999",
        json={"status": "Closed"},
    )
    assert missing_update.status_code == 404

    # 7. Retrieve nonexistent defect
    missing_get = client.get("/api/defects/99999")
    assert missing_get.status_code == 404

    # 8. Delete the valid defect
    delete_response = client.delete(
        f"/api/defects/{defect_id}"
    )
    assert delete_response.status_code == 204

    # 9. Delete nonexistent defect
    missing_delete = client.delete("/api/defects/99999")
    assert missing_delete.status_code == 404

def test_defect_key_generation_handles_existing_key(client):
    # Create requirement
    requirement = client.post(
        "/api/requirements/",
        json={
            "title": "Defect Key Test",
            "description": "Testing unique defect key generation.",
        },
    )
    requirement_id = requirement.json()["id"]

    # Create test case
    test_case = client.post(
        "/api/test-cases/",
        json={
            "requirement_id": requirement_id,
            "title": "Defect Key Test Case",
            "description": "Verify defect key generation.",
            "test_steps": "Execute test.",
            "expected_result": "Test passes.",
        },
    )
    test_case_id = test_case.json()["id"]

    # Create first defect
    first = client.post(
        "/api/defects/",
        json={
            "test_case_id": test_case_id,
            "title": "First defect",
            "description": "First defect description.",
        },
    )
    assert first.status_code == 201

    # Create second defect and verify unique key
    second = client.post(
        "/api/defects/",
        json={
            "test_case_id": test_case_id,
            "title": "Second defect",
            "description": "Second defect description.",
        },
    )
    assert second.status_code == 201
    assert second.json()["defect_key"] != first.json()["defect_key"]

def test_generate_defect_key_handles_collision():
    mock_session = Mock()

    # First query: latest defect ID is 1
    # Second query: BUG-0002 already exists
    # Third query: BUG-0003 does not exist
    mock_session.exec.side_effect = [
        Mock(first=Mock(return_value=1)),
        Mock(first=Mock(return_value=2)),
        Mock(first=Mock(return_value=None)),
    ]

    generated_key = generate_defect_key(mock_session)

    assert generated_key == "BUG-0003"
    assert mock_session.exec.call_count == 3

def test_test_case_negative_scenarios(client):
    # 1. Create test case with invalid requirement ID
    invalid_create = client.post(
        "/api/test-cases/",
        json={
            "requirement_id": 99999,
            "title": "Invalid Test Case",
            "description": "This should not be created.",
            "test_steps": "Execute test.",
            "expected_result": "Test passes.",
        },
    )
    assert invalid_create.status_code == 404

    # 2. Create a valid requirement
    requirement = client.post(
        "/api/requirements/",
        json={
            "title": "Test Case Validation",
            "description": "Requirement for test case validation.",
        },
    )
    assert requirement.status_code == 201
    requirement_id = requirement.json()["id"]

    # 3. Create a valid test case
    test_case = client.post(
        "/api/test-cases/",
        json={
            "requirement_id": requirement_id,
            "title": "Verify Login Validation",
            "description": "Verify login error handling.",
            "test_steps": "Enter invalid credentials.",
            "expected_result": "An error message is displayed.",
        },
    )
    assert test_case.status_code == 201
    test_case_id = test_case.json()["id"]

    # 4. Retrieve nonexistent test case
    missing_get = client.get("/api/test-cases/99999")
    assert missing_get.status_code == 404

    # 5. Update test case with invalid requirement ID
    invalid_update = client.patch(
        f"/api/test-cases/{test_case_id}",
        json={"requirement_id": 99999},
    )
    assert invalid_update.status_code == 404

    # 6. Update nonexistent test case
    missing_update = client.patch(
        "/api/test-cases/99999",
        json={"status": "Ready"},
    )
    assert missing_update.status_code == 404

    # 7. Delete valid test case
    delete_response = client.delete(
        f"/api/test-cases/{test_case_id}"
    )
    assert delete_response.status_code == 204

    # 8. Delete nonexistent test case
    missing_delete = client.delete("/api/test-cases/99999")
    assert missing_delete.status_code == 404

def test_generate_test_case_key_handles_collision():
    mock_session = Mock()

    # Latest test case ID is 1
    # TC-0002 already exists, but TC-0003 does not
    mock_session.exec.side_effect = [
        Mock(first=Mock(return_value=1)),
        Mock(first=Mock(return_value=2)),
        Mock(first=Mock(return_value=None)),
    ]

    generated_key = generate_test_case_key(mock_session)

    assert generated_key == "TC-0003"
    assert mock_session.exec.call_count == 3

def test_rtm_summary_with_no_requirements(client):
    response = client.get("/api/rtm/")

    assert response.status_code == 200

    data = response.json()

    assert data["total_requirements"] == 0
    assert data["covered_requirements"] == 0
    assert data["uncovered_requirements"] == 0
    assert data["coverage_percentage"] == 0.0
    assert data["traceability_matrix"] == []

def test_rtm_covered_and_uncovered_requirements(client):
    # Create a covered requirement
    covered_requirement = client.post(
        "/api/requirements/",
        json={
            "title": "Covered Requirement",
            "description": "This requirement has a linked test case.",
        },
    )
    assert covered_requirement.status_code == 201
    covered_id = covered_requirement.json()["id"]

    # Create an uncovered requirement
    uncovered_requirement = client.post(
        "/api/requirements/",
        json={
            "title": "Uncovered Requirement",
            "description": "This requirement has no linked test case.",
        },
    )
    assert uncovered_requirement.status_code == 201

    # Link a test case to the first requirement
    test_case = client.post(
        "/api/test-cases/",
        json={
            "requirement_id": covered_id,
            "title": "Verify Covered Requirement",
            "description": "Test coverage validation.",
            "test_steps": "Execute the test.",
            "expected_result": "The requirement is satisfied.",
            "priority": "High",
            "status": "Ready",
        },
    )
    assert test_case.status_code == 201

    # Verify RTM
    response = client.get("/api/rtm/")
    assert response.status_code == 200

    data = response.json()

    assert data["total_requirements"] == 2
    assert data["covered_requirements"] == 1
    assert data["uncovered_requirements"] == 1
    assert data["coverage_percentage"] == 50.0

    matrix = data["traceability_matrix"]

    covered = next(
        item for item in matrix
        if item["requirement_id"] == covered_id
    )

    assert covered["coverage_status"] == "Covered"
    assert covered["test_case_count"] == 1
    assert covered["test_cases"][0]["priority"] == "High"
    assert covered["test_cases"][0]["status"] == "Ready"

    uncovered = next(
        item for item in matrix
        if item["requirement_title"] == "Uncovered Requirement"
    )

    assert uncovered["coverage_status"] == "Not Covered"
    assert uncovered["test_case_count"] == 0
    assert uncovered["test_cases"] == []

def test_get_session_yields_and_closes_session(monkeypatch):
    class FakeSession:
        def __init__(self, engine):
            self.engine = engine
            self.closed = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.closed = True

    fake_session = FakeSession("test-engine")

    monkeypatch.setattr(
        database,
        "Session",
        lambda engine: fake_session,
    )

    generator = database.get_session()

    yielded_session = next(generator)

    assert yielded_session is fake_session
    assert yielded_session.engine == "test-engine"

    generator.close()

    assert fake_session.closed is True

def test_database_postgres_url_normalization(monkeypatch):
    import importlib
    import sqlmodel
    import app.database as database_module

    original_create_engine = sqlmodel.create_engine
    original_engine = database_module.engine
    captured = {}

    def fake_create_engine(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return "fake-engine"

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgres://user:password@localhost:5432/tracewise",
    )

    try:
        monkeypatch.setattr(
            sqlmodel,
            "create_engine",
            fake_create_engine,
        )

        importlib.reload(database_module)

        assert captured["url"] == (
            "postgresql://user:password@localhost:5432/tracewise"
        )
        assert captured["kwargs"]["connect_args"] == {}
        assert database_module.engine == "fake-engine"

    finally:
        monkeypatch.setattr(
            sqlmodel,
            "create_engine",
            original_create_engine,
        )
        monkeypatch.delenv("DATABASE_URL", raising=False)
        
        original_engine.dispose()
        importlib.reload(database_module)

def test_home_dashboard_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert len(response.text) > 0

def test_health_check_returns_success(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["message"] == "TraceWise server is running!"
    assert "checked_at" in data
