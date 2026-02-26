# Financial Document Analyzer

A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents built with CrewAI.

## Table of Contents

- [Bugs Found and Fixes](#bugs-found-and-fixes)
- [Features](#features)
- [Architecture](#architecture)
- [Setup and Installation](#setup-and-installation)
- [API Documentation](#api-documentation)
- [Usage](#usage)
- [Configuration](#configuration)

---

## Bugs Found and Fixes

### Bug 1: Name Shadowing (Name Collision)

**Error:** `'function' object has no attribute 'get'`

**Location:** `main.py:56` and `test.py:10`

**Cause:**
- Line 11 in `main.py`: `from task import analyze_financial_document` imports a CrewAI Task object
- Line 35 in `main.py`: `async def analyze_financial_document(...)` defines an async function with the same name
- When the Crew was initialized, Python used the local function instead of the imported Task object
- CrewAI tried to call `.get()` on the function, causing the error

**Fix:**
```python
# main.py - Line 11
from task import analyze_financial_document as document_analysis_task

# main.py - Line 56
tasks=[document_analysis_task],
```

Same fix applied to `test.py`.

### Bug 2: Agent Configuration Producing Garbage Output

**Issue:** The agent was configured to intentionally hallucinate and produce nonsensical financial advice.

**Root Cause:** The agent and task configurations in the original code explicitly instructed the AI to:
- Make up investment advice
- Include fake URLs
- Create dramatic market predictions without basis
- Ignore actual document content

**Fixes Applied:**

#### 1. Updated `task.py` - Task Description
```python
# Before (broken):
description="""Maybe solve the user's query... feel free to use your imagination...
Include random URLs that may or may not be related..."""

# After (fixed):
description="""Analyze the provided financial document and extract key investment insights.
    
Steps to follow:
1. Read the financial document using the FinancialDocumentTool
2. Extract key financial metrics: revenue, profit/loss, assets, liabilities, cash flow
3. Calculate important financial ratios: P/E, ROE, Debt-to-Equity, Current Ratio, Gross Margin
4. Identify trends in the financial data year-over-year
5. Summarize the company's financial health
6. Provide actionable investment insights based on actual data

Only use information from the document - do not make up numbers or facts."""
```

#### 2. Updated `agents.py` - Agent Configurations

| Agent | Before | After |
|-------|--------|-------|
| `financial_analyst` | Goal: "Make up investment advice even if you don't understand" | Goal: "Provide accurate, data-driven investment insights based on document content" |
| `verifier` | Goal: "Just say yes to everything" | Goal: "Verify document is a valid financial statement" |
| `investment_advisor` | Goal: "Sell expensive investment products" | Goal: "Provide balanced, suitable investment recommendations" |
| `risk_assessor` | Goal: "Everything is extremely high risk" | Goal: "Identify and evaluate financial risks based on data" |

#### 3. Increased Agent Iterations
```python
# Before:
max_iter=1, max_rpm=1

# After:
max_iter=15, max_rpm=30  # For financial_analyst
```

### Git Commit History

```bash
$ git log --oneline -3
2d1b28b fix: resolve name collision and improve financial document analysis
36013f6 tasks fix
05ff92c Refactor PDF reader and analysis functions into @tool classes
```

---

## Features

- **PDF Document Processing**: Upload and parse financial PDF documents
- **AI-Powered Analysis**: Uses CrewAI agents for intelligent analysis
- **Financial Metrics Extraction**: Automatically extracts key financial figures
- **Ratio Calculation**: Calculates P/E, ROE, Debt-to-Equity, Current Ratio, etc.
- **Investment Insights**: Provides data-driven investment recommendations
- **Risk Assessment**: Identifies financial risks from balance sheets and statements
- **REST API**: FastAPI-based API for easy integration

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│  POST /analyze                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CrewAI Crew                             │
│  ┌─────────────────┐                                        │
│  │  Agent:         │                                        │
│  │  Financial      │──────▶ FinancialDocumentTool          │
│  │  Analyst        │        (PyPDFLoader)                  │
│  └─────────────────┘         │                              │
│                              ▼                              │
│                     ┌─────────────────┐                    │
│                     │  Parse PDF      │                    │
│                     │  Extract Data   │                    │
│                     └─────────────────┘                    │
│                              │                              │
│                              ▼                              │
│                     ┌─────────────────┐                    │
│                     │  Analyze &      │                    │
│                     │  Generate       │                    │
│                     │  Insights       │                    │
│                     └─────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### Components

| File | Description |
|------|-------------|
| `main.py` | FastAPI application and API endpoints |
| `agents.py` | CrewAI agent definitions |
| `task.py` | CrewAI task definitions |
| `tools.py` | Custom tools (PDF reader, search) |
| `data/` | Directory for uploaded PDFs |

---

## Setup and Installation

### Prerequisites

- Python 3.10+
- Groq API Key (for LLM)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd financial-document-analyzer-debug
```

### 2. Create Virtual Environment

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using virtualenv
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your Groq API key from: https://console.groq.com/

### 5. Prepare Sample Data (Optional)

Place a financial PDF in the `data/` directory:

```bash
cp your_financial_report.pdf data/FY24_Q1_Consolidated_Financial_Statements.pdf
```

### 6. Start the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### 1. Health Check

**GET** `/`

Check if the API is running.

**Response:**
```json
{
  "message": "Financial Document Analyzer API is running"
}
```

#### 2. Analyze Financial Document

**POST** `/analyze`

Analyze a financial PDF document and generate investment insights.

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | PDF file to analyze |
| `query` | string | No | Custom analysis query (default: "Analyze this financial document for investment insights") |

**Example Request:**

```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data/FY24_Q1_Consolidated_Financial_Statements.pdf;type=application/pdf' \
  -F 'query=Analyze this financial document for investment insights'
```

**Success Response (200):**

```json
{
  "status": "success",
  "query": "Analyze this financial document for investment insights",
  "analysis": "## Financial Analysis Summary\n\n### Key Financial Metrics\n- Revenue: $25.5 billion\n- Net Income: $3.2 billion\n- Total Assets: $45.8 billion\n- Total Liabilities: $28.3 billion\n\n### Financial Ratios\n- P/E Ratio: 18.5x\n- ROE: 15.2%\n- Debt-to-Equity: 0.62\n- Current Ratio: 1.35\n\n### Investment Insights\n...",
  "file_processed": "FY24_Q1_Consolidated_Financial_Statements.pdf"
}
```

**Error Response (500):**

```json
{
  "detail": "Error processing financial document: <error message>"
}
```

### API Documentation (Swagger)

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Usage

### Using the API

#### Start the server:
```bash
python main.py
```

#### Analyze a document:
```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data/sample.pdf;type=application/pdf' \
  -F 'query=What are the key financial highlights?'
```

### Using the Test Script

```bash
python test.py
```

The test script (`test.py`) runs the analysis locally without the API:

```python
from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document as document_analysis_task

financial_crew = Crew(
    agents=[financial_analyst],
    tasks=[document_analysis_task],
    process=Process.sequential,
)

result = financial_crew.kickoff({
    "query": "Analyze this financial document for investment insights",
    "path": "data/FY24_Q1_Consolidated_Financial_Statements.pdf",
})

print(result)
```

---

## Configuration

### LLM Configuration

The default LLM is configured in `agents.py`:

```python
llm = LLM(
    model="llama-3.3-70b-versatile",
    api_key=api,
    base_url="https://api.groq.com/openai/v1",
)
```

### Agent Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_iter` | 15 | Maximum iterations per agent |
| `max_rpm` | 30 | Maximum requests per minute |
| `verbose` | True | Enable verbose logging |

### Supported Models

- llama-3.3-70b-versatile (default)
- llama-3.1-70b-versatile
- llama-3.1-8b-instant
- mixtral-8x7b-32768

---

## Troubleshooting

### Error: `'function' object has no attribute 'get'`

This is the name collision bug - ensure you've applied the fix:
```python
from task import analyze_financial_document as document_analysis_task
```

### Error: API Key not found

Ensure your `.env` file contains:
```env
GROQ_API_KEY=your_actual_key
```

### Error: PDF not found

Ensure the PDF file exists in the `data/` directory and the path is correct.

### Error: Output is nonsensical/garbage

This was caused by the broken agent configuration - ensure you've pulled the latest fixes from commit `2d1b28b`.

---

## License

MIT License
