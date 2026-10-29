# TraceWise QA Workbench

A requirements-driven QA workbench for test management, requirements traceability, API validation, defect tracking, and regression testing.

## 📌 Project Overview

TraceWise QA Workbench is a Quality Assurance project designed to organize software testing activities in one place. It helps QA engineers manage requirements, create and execute test cases, track defects, and monitor requirements coverage through a Requirements Traceability Matrix (RTM).

## 🎯 Key Features

- **Requirements Management:** Create, retrieve, update, and delete requirements.
- **Test Case Management:** Maintain test cases linked to requirements.
- **Test Execution:** Record execution status, actual results, notes, and tester details.
- **Defect Management:** Track defects with severity, priority, status, and assignment details.
- **Requirements Traceability Matrix (RTM):** Identify covered and uncovered requirements.
- **REST API:** Access project functionality through FastAPI endpoints.
- **Automated API Testing:** Validate API functionality using pytest and FastAPI TestClient.
- **HTML Test Reports:** Generate readable reports containing automated test results.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| FastAPI | REST API development |
| SQLModel | Database models and ORM |
| SQLite | Database storage |
| Pytest | Automated testing |
| HTTPX | HTTP client and testing support |
| Pytest-HTML | HTML test reporting |
| Swagger UI | API exploration and validation |

## 📂 Project Structure

```text
tracewise-qa-workbench/
├── app/
│   ├── routers/
│   │   ├── requirements.py
│   │   ├── test_cases.py
│   │   ├── execution.py
│   │   ├── defects.py
│   │   └── rtm.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   └── test_api.py
├── reports/
│   └── test-report.html
├── requirements.txt
├── README.md
└── tracewise.db