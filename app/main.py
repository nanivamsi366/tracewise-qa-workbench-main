from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.database import create_db_and_tables
from app.routers.requirements import router as requirements_router
from app.routers.test_cases import router as test_cases_router
from app.routers.rtm import router as rtm_router
from app.routers.execution import router as execution_router
from app.models import TestExecution
from app.routers.defects import router as defects_router

app = FastAPI(
    title="TraceWise QA Workbench",
    description="A practical workspace for software quality assurance.",
    version="0.1.0",
)

@app.on_event("startup")
def startup():
    create_db_and_tables()


app.include_router(requirements_router)
app.include_router(test_cases_router)
app.include_router(rtm_router)
app.include_router(execution_router)
app.include_router(defects_router)

for route in app.routes:
    print(
        getattr(route, "methods", None),
        getattr(route, "path", "Router object"),
    )

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TraceWise | QA Workbench</title>
    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            background: #0b1020;
            color: #e8ecf8;
            font-family: Arial, sans-serif;
        }

        header {
            padding: 22px 7%;
            border-bottom: 1px solid #273047;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
        }

        .brand { font-size: 22px; font-weight: bold; }
        .brand span { color: #7c9cff; }

        .badge {
            color: #9ee6bd;
            background: #17372f;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
        }

        main {
            max-width: 1100px;
            margin: 45px auto;
            padding: 0 22px;
        }

        .eyebrow {
            color: #93aaff;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 12px;
        }

        h1 { font-size: clamp(30px, 5vw, 48px); margin-bottom: 12px; }
        .intro { color: #a8b1c9; line-height: 1.7; max-width: 650px; }

        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 16px;
            margin-top: 32px;
        }

        .card {
            background: #131b30;
            border: 1px solid #28334d;
            border-radius: 14px;
            padding: 22px;
        }

        .card h3 { color: #a8b1c9; font-size: 14px; font-weight: normal; }
        .number { font-size: 32px; font-weight: bold; margin: 18px 0 8px; }
        .hint { font-size: 12px; color: #8794b2; }

        .panel {
            margin-top: 25px;
            padding: 24px;
            border-radius: 14px;
            border: 1px solid #28334d;
            background: #131b30;
        }

        .panel h2 { margin-top: 0; font-size: 19px; }

        .status {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 6px;
            background: #203b35;
            color: #9ee6bd;
            font-size: 12px;
        }

        button {
            margin-top: 15px;
            padding: 11px 16px;
            border: 0;
            border-radius: 8px;
            background: #7897ff;
            color: #0b1020;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover { background: #a0b4ff; }

        #result { color: #9ee6bd; margin-left: 10px; font-size: 13px; }

        footer {
            padding: 25px;
            text-align: center;
            color: #8794b2;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">Trace<span>Wise</span></div>
        <div class="badge">● QA WORKSPACE</div>
    </header>

    <main>
        <div class="eyebrow">Software quality, made traceable</div>
        <h1>Know what you've tested.<br>Know what you've missed.</h1>
        <p class="intro">
            TraceWise is a requirements-driven QA workbench designed to connect
            software requirements, test cases, and defects in one place.
        </p>

<section class="cards">
    <article class="card">
        <h3>Requirements</h3>
        <div class="number" id="requirements-count">0</div>
        <div class="hint">Total requirements documented</div>
    </article>

    <article class="card">
        <h3>Test cases</h3>
        <div class="number" id="test-cases-count">0</div>
        <div class="hint">Total test cases created</div>
    </article>

    <article class="card">
        <h3>Execution status</h3>
        <div class="number" id="execution-status">—</div>
        <div class="hint">Latest test execution</div>
    </article>

    <article class="card">
        <h3>Open defects</h3>
        <div class="number" id="open-defects-count">0</div>
        <div class="hint">Defects awaiting resolution</div>
    </article>
</section>

        <section class="panel">
            <h2>Your workspace is ready</h2>
            <p class="intro">
    Your QA workspace is connected to the database.
    Manage requirements, test cases, executions, and defects
    through your API endpoints.
            </p>
            <span class="status">Prototype initialized</span><br>
            <button onclick="checkStatus()">Check application status</button>
            <span id="result"></span>
        </section>
    </main>

    <footer>TraceWise QA Workbench · Built as a learning project</footer>

<script>
    async function loadDashboard() {
        try {
            const endpoints = [
                "/api/requirements/",
                "/api/test-cases/",
                "/api/executions/",
                "/api/defects/"
            ];

            const responses = await Promise.all(
                endpoints.map(url => fetch(url))
            );

            if (responses.some(response => !response.ok)) {
                throw new Error("Failed to fetch dashboard data");
            }

            const [requirements, testCases, executions, defects] =
                await Promise.all(
                    responses.map(response => response.json())
                );

            document.getElementById("requirements-count").textContent =
                requirements.length;

            document.getElementById("test-cases-count").textContent =
                testCases.length;

            const latestExecution = executions.length
                ? executions[executions.length - 1].status
                : "None";

            document.getElementById("execution-status").textContent =
                latestExecution;

            const openDefects = defects.filter(
                defect => (defect.status || "").toLowerCase() === "open"
            ).length;

            document.getElementById("open-defects-count").textContent =
                openDefects;

            const result = document.getElementById("result");
            if (result) {
                result.textContent = "Dashboard data loaded successfully.";
            }

        } catch (error) {
            console.error("Dashboard loading failed:", error);

            const result = document.getElementById("result");
            if (result) {
                result.textContent = "Could not load dashboard data. Check the API endpoints.";
            }
        }
    }

    async function checkStatus() {
        const result = document.getElementById("result");
        result.textContent = "Checking...";

        try {
            const response = await fetch("/api/health");
            if (!response.ok) {
                throw new Error("Request failed");
            }

            const data = await response.json();
            result.textContent = data.message;
        } catch (error) {
            result.textContent = "Could not reach the server.";
        }
    }

    document.addEventListener("DOMContentLoaded", loadDashboard);
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "TraceWise server is running!",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }