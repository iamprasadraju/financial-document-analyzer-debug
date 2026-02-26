#!/usr/bin/env python3

import asyncio
import os
import uuid

from crewai import Crew, Process
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from agents import financial_analyst
from task import analyze_financial_document

app = FastAPI(title="Financial Document Analyzer")


def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """To run the whole crew"""
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document],
        process=Process.sequential,
    )

    result = financial_crew.kickoff({"path": file_path, "query": query})
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(
        default="Analyze this financial document for investment insights"
    ),
):
    """Analyze financial document and provide investment insights"""

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        # Save uploaded PDF
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Run CrewAI
        financial_crew = Crew(
            agents=[financial_analyst],
            tasks=[analyze_financial_document],  # your task object
            process=Process.sequential,
        )

        # Pass the correct key matching the tool argument
        response = financial_crew.kickoff(
            {
                "path": file_path,  # <-- must match FinancialDocumentTool(path)
                "query": query.strip(),
            }
        )

        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing financial document: {str(e)}"
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
