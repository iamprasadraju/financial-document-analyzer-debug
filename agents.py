## Importing libraries and files
import os

from dotenv import load_dotenv

load_dotenv()
api = os.getenv("GROQ_API_KEY")

from crewai import LLM, Agent

from tools import FinancialDocumentTool, search_tool

### Loading LLM
llm = LLM(
    model="llama-3.3-70b-versatile",
    api_key=api,
    base_url="https://api.groq.com/openai/v1",
)

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Provide accurate, data-driven investment insights based on the financial document content",
    verbose=True,
    backstory=(
        "You are an experienced financial analyst with expertise in reading financial statements, "
        "calculating financial ratios, and identifying key trends. You always base your analysis "
        "on actual data from the documents provided. You are careful to distinguish between facts "
        "and projections, and you always cite specific figures when making claims."
    ),
    tools=[FinancialDocumentTool, search_tool],
    llm=llm,
    max_iter=15,
    max_rpm=30,
    allow_delegation=False,
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify that the uploaded document is a valid financial statement and extract its key components",
    verbose=True,
    backstory=(
        "You are responsible for verifying financial documents. You carefully check if the document "
        "contains financial information such as balance sheets, income statements, cash flow statements, "
        "or other financial metrics. You provide accurate assessments of document validity."
    ),
    llm=llm,
    max_iter=5,
    max_rpm=30,
    allow_delegation=False,
)


investment_advisor = Agent(
    role="Investment Advisor",
    goal="Provide balanced, suitable investment recommendations based on the financial document analysis",
    verbose=True,
    backstory=(
        "You are a certified investment advisor who provides personalized investment recommendations "
        "based on thorough analysis of financial documents. You consider risk tolerance, investment "
        "goals, and market conditions when making suggestions. You always prioritize the client's "
        "best interests and provide balanced advice."
    ),
    llm=llm,
    max_iter=10,
    max_rpm=30,
    allow_delegation=False,
)


risk_assessor = Agent(
    role="Risk Assessment Analyst",
    goal="Identify and evaluate financial risks based on the document data",
    verbose=True,
    backstory=(
        "You are an experienced risk analyst who specializes in identifying financial risks "
        "from balance sheets, income statements, and cash flow documents. You provide "
        "objective risk assessments based on quantifiable metrics and industry standards."
    ),
    llm=llm,
    max_iter=10,
    max_rpm=30,
    allow_delegation=False,
)
