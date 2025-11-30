import logging
import re
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from config import retry_config
from rag.agent import rag_agent
from form_agent.agent import form_extractor_agent, form_filler_agent

from job_application_coordinator.config import AGENT_NAME, AGENT_MODEL, AGENT_OUTPUT_KEY


job_application_coordinator_agent = LlmAgent(
    model=Gemini(model=AGENT_MODEL, retry_options=retry_config),
    name=AGENT_NAME,
    sub_agents=[form_extractor_agent, rag_agent, form_filler_agent],
    output_key=AGENT_OUTPUT_KEY,
    description="Agent for coordinating job application operations",
    instruction="""
    You coordinate a job application submission workflow by orchestrating three sub-agents.

    WORKFLOW STEPS:

    1. FORM EXTRACTION
       - Extract the URL from the user request
       - Call form_extractor_agent to get form field names
       - On error: Return {"status": "error", "response": error_message}
       - On success: Proceed to step 2

    2. RAG RETRIEVAL
       - Extract the user name from the request (e.g., "Apply for sukumar")
       - If no user name found, ask the user to provide it
       - Call rag_agent with query: "Retrieve information for user '<USER_NAME>': <field1>, <field2>, ..."
       - If RAG returns no data: Continue with empty data (don't fail)
       - If RAG returns error: Log it but continue with empty data
       - On success: Proceed to step 3

    3. FORM FILLING
       - Call form_filler_agent with the URL and retrieved data
       - Pass all data from RAG, even if incomplete
       - On error: Return error with partial results if available
       - On success: Proceed to final output

    FINAL OUTPUT (always return this structure):
    {
        "status": "success" | "error" | "partial",
        "response": {
            "filled_fields": [{"field": "name", "value": "value"}],
            "unfilled_fields": ["field_name"],
            "errors": ["error_message"]
        },
        "metadata": {
            "user": "user_name",
            "url": "form_url",
            "total_fields": N,
            "filled_count": M
        }
    }
    """,
)

logger.info(f"✅ {AGENT_NAME} initialized successfully")
