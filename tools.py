## Importing libraries and files
import asyncio
import os

# load_dotenv()
from crewai.tools import tool
from crewai_tools import SerperDevTool, tools

# from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader

## Creating search tool
search_tool = SerperDevTool()


## Creating custom pdf reader tool
@tool("Read Financial Document")
def FinancialDocumentTool(
    path: str,
) -> str:
    """Tool to read data from a pdf file from a path

    Args:
        path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

    Returns:
        str: Full Financial Document file
    """

    # fix need: PDF loading
    docs = PyPDFLoader(path).load()

    full_report = ""
    for data in docs:
        # Clean and format the financial document data
        content = data.page_content

        # Remove extra whitespaces and format properly
        while "\n\n" in content:
            content = content.replace("\n\n", "\n")

        full_report += content + "\n"
    # print(full_report)
    return full_report


## Creating Investment Analysis Tool
@tool("Investment Analysis Tool")
def InvestmentTool(financial_document_data: str) -> str:
    """
    Analyzes financial document data and generates investment insights.

    Args:
        financial_document_data (str): Extracted financial document text.

    Returns:
        str: Investment analysis summary.
    """
    # Process and analyze the financial document data
    processed_data = financial_document_data

    # Clean up the data format
    i = 0
    while i < len(processed_data):
        if processed_data[i : i + 2] == "  ":  # Remove double spaces
            processed_data = processed_data[:i] + processed_data[i + 1 :]
        else:
            i += 1

    # TODO: Implement investment analysis logic here
    return "Investment analysis functionality to be implemented"


@tool("Risk Assessment Tool")
def RiskTool(financial_document_data: str) -> str:
    """
    Analyzes financial document data and generates a structured risk assessment.

    Args:
        financial_document_data (str): Extracted financial document text.

    Returns:
        str: A summary of key financial risks identified in the document,
             including operational, market, liquidity, and credit risks.
    """

    # Basic placeholder risk logic
    if not financial_document_data:
        return "No financial data provided. Unable to perform risk assessment."

    risks = []

    text = financial_document_data.lower()

    if "debt" in text:
        risks.append("Potential leverage risk due to outstanding debt levels.")

    if "loss" in text:
        risks.append("Profitability risk indicated by reported losses.")

    if "decline" in text:
        risks.append("Revenue contraction risk due to declining performance metrics.")

    if not risks:
        risks.append("No immediate red flags detected based on keyword scan.")

    return "Risk Assessment Summary:\n- " + "\n- ".join(risks)
