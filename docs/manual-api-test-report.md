TraceWise QA Workbench

Manual API Testing Report

Project: TraceWise QA Workbench
Tested By: Taraka Venkata Sai Vamsi Sanaboina
Testing Date: 02 November 2026
Environment: Local Development
Base URL: http://127.0.0.1:8000
API Documentation: /docs
Testing Type: Manual API Testing, CRUD Testing, Integration Verification

1. Testing Objective

The objective of this testing activity was to validate the functionality, reliability and correctness of the TraceWise QA Workbench REST APIs.

The testing covered:

Requirements management

Test case management

Requirements Traceability Matrix (RTM)

Test execution management

Defect management

Dashboard data verification

Both positive API scenarios and CRUD operations were performed using Swagger UI.

2. Testing Environment

Component

Configuration

Operating System

Windows 11

Python

3.15.1

Backend Framework

FastAPI

API Testing Tool

Swagger UI

API Server

Uvicorn

Database

SQLite (local testing)

Automated Testing

Pytest 9.1.1

3. Manual API Test Results

3.1 Requirements API

Endpoint: /api/requirements/

Test ID

Test Scenario

Expected Status

Actual Status

Result

REQ-01

Retrieve all requirements

200

200

PASS

REQ-02

Retrieve requirement by ID

200

200

PASS

REQ-03

Retrieve nonexistent requirement (ID 99999)

404

404

PASS

REQ-04

Create a new requirement

201

201

PASS

REQ-05

Update requirement details

200

200

PASS

REQ-06

Delete the created requirement

204

204

PASS

Observation: Requirement creation, retrieval, updating and deletion worked as expected. The negative test also returned the expected 404 response.

3.2 Test Cases API

Endpoint: /api/test-cases/

Test ID

Test Scenario

Expected Status

Actual Status

Result

TC-01

Retrieve all test cases

200

200

PASS

TC-02

Retrieve test case by ID

200

200

PASS

TC-03

Create a test case linked to a requirement

201

201

PASS

TC-04

Verify newly created test case in list

200

200

PASS

TC-05

Update test case priority and status

200

200

PASS

TC-06

Delete the created test case

204

204

PASS

Observation: Test cases were successfully linked to Requirement ID 2. The application generated the test case key TC-0002. Updating and deleting the temporary record also worked correctly.

3.3 Requirements Traceability Matrix (RTM)

Endpoint: /api/rtm/

Test ID

Test Scenario

Expected Status

Actual Status

Result

RTM-01

Retrieve requirements traceability matrix

200

200

PASS

Observed RTM Results:

Metric

Actual Value

Total Requirements

9

Covered Requirements

1

Uncovered Requirements

8

Coverage Percentage

11.11%

Observation: The RTM correctly identified the requirement linked to an existing test case and identified the remaining uncovered requirements.

3.4 Test Execution API

Endpoint: /api/executions/

Test ID

Test Scenario

Expected Status

Actual Status

Result

EXE-01

Retrieve all executions

200

200

PASS

EXE-02

Retrieve execution by ID

200

200

PASS

EXE-03

Create a new execution record

201

201

PASS

EXE-04

Verify execution history

200

200

PASS

EXE-05

Update execution result

200

200

PASS

EXE-06

Delete the created execution

204

204

PASS

Observation: The application successfully recorded Passed and Failed execution statuses. The temporary Failed execution was updated to Passed and subsequently deleted without affecting the original execution.

3.5 Defects API

Endpoint: /api/defects/

Test ID

Test Scenario

Expected Status

Actual Status

Result

DEF-01

Retrieve all defects

200

200

PASS

DEF-02

Retrieve defect by ID

200

200

PASS

DEF-03

Create a new defect

201

201

PASS

DEF-04

Verify newly created defect in list

200

200

PASS

DEF-05

Update defect severity and status

200

200

PASS

DEF-06

Delete the created defect

204

204

PASS

Observation: Defect creation generated the key BUG-0002. Updating severity and status worked correctly, and deleting the temporary defect preserved the original defect record.

4. Automated Testing Results

Command Executed:

python -m pytest -v --cov=app --cov-report=term-missing --html=reports/automated-test-report.html --self-contained-html

Test Execution Summary:

Metric

Result

Total Automated Tests

22

Passed

22

Failed

0

Pass Percentage

100%

Overall Code Coverage

100%

Total Statements

386

Uncovered Statements

0

Execution Time

1.92 seconds

Automated Test Coverage

Module

Coverage

Database

100%

Main Application

100%

Models

100%

Defects Router

100%

Execution Router

100%

Requirements Router

100%

RTM Router

100%

Test Cases Router

100%

Schemas

100%

Overall

100%

Automated Test Scenarios

The automated suite covers:

Swagger/OpenAPI availability

Requirements API listing, creation and lifecycle

Test case CRUD and negative scenarios

Execution lifecycle and invalid resource handling

Defect lifecycle and negative scenarios

Defect key generation and collision handling

Test case key generation and collision handling

RTM summary with empty, covered and uncovered requirements

Database session creation and cleanup

PostgreSQL database URL normalization

Dashboard HTML response

Health-check endpoint

Overall Result: All 22 automated tests passed successfully, achieving 100% statement coverage across all application modules.

The self-contained HTML test report was generated at reports/automated-test-report.html.

5. Dashboard Verification

The dashboard was verified after completing the manual API tests.

Dashboard Metric

Expected Value

Actual Value

Result

Total Requirements

9

9

PASS

Test Cases

1

1

PASS

Latest Execution

Passed

Passed

PASS

Open Defects

1

1

PASS

RTM Coverage

11.1%

11.1%

PASS

The dashboard displayed the expected data from the local API backend.

6. HTTP Status Codes Verified

HTTP Status

Meaning

Usage

200

OK

Successful retrieval and updates

201

Created

Successful resource creation

204

No Content

Successful resource deletion

404

Not Found

Nonexistent resource lookup

7. Testing Conclusion

The TraceWise QA Workbench successfully passed all documented manual API test scenarios and all 22 automated tests, achieving 100% code coverage across the application.

The testing confirmed that the application's core API modules support the expected CRUD operations, maintain relationships between requirements and test cases, return traceability information, record execution results and manage defects.

The dashboard also displayed the expected local application metrics after testing.

Final Assessment: All executed manual test scenarios and automated test cases passed.

8. Scope and Limitations

Testing was performed against the local development API.

RTM was tested through its GET endpoint.

Automated testing included 22 pytest test cases, achieving 100% statement coverage across 386 application statements.

Performance, load, security and cross-browser testing were not included in this testing activity.

The documented results represent the observed test execution on 02 November 2026.

9. Author

Taraka Venkata Sai Vamsi Sanaboina

QA Engineer | Manual Testing | API Testing | Python | FastAPI

Project: TraceWise QA Workbench
GitHub: https://github.com/nanivamsi366/tracewise-qa-workbench-main
Live Application: https://tracewise-qa-workbench-main.onrender.com/