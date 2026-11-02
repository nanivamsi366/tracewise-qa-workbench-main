import pytest

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session


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
