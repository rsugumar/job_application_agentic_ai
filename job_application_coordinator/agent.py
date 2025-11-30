from typing import Any, Dict

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import FunctionTool

from config import retry_config
from rag.agent import rag_agent
from form_agent.agent import form_extractor_agent, form_filler_agent

from job_application_coordinator.config import AGENT_NAME, AGENT_MODEL, AGENT_OUTPUT_KEY

def save_user_name(tool_context: ToolContext, user_name: str) -> Dict[str, Any]:
    """
    Tool to record and save user name in session state.

    This should be called at the start of the job application process to ensure
    the username is available for RAG retrieval and form filling.

    Args:
        user_name: The username to store in session state
    """
    if not user_name or not user_name.strip():
        return {"status": "error", "message": "Username cannot be empty"}

    # Write to session state using the 'user:' prefix for user data
    tool_context.state["user:name"] = user_name.strip()
    return {"status": "success", "user_name": user_name.strip()}


def retrieve_user_name(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Tool to retrieve user name from session state.
    """
    # Read from session state
    user_name = tool_context.state.get("user:name", "Username not found")
    return {"status": "success", "user_name": user_name}

def save_url(tool_context: ToolContext, url: str) -> Dict[str, Any]:
    """Save job application URL in session state."""
    if not url or not url.strip():
        return {"status": "error", "message": "URL cannot be empty"}

    tool_context.state["job:url"] = url.strip()
    return {"status": "success", "url": url.strip()}

job_application_coordinator_agent = LlmAgent(
    model=Gemini(model=AGENT_MODEL, retry_options=retry_config),
    name=AGENT_NAME,
    sub_agents=[form_extractor_agent, rag_agent, form_filler_agent],
    tools=[
        FunctionTool(save_user_name),
        FunctionTool(retrieve_user_name),
        FunctionTool(save_url),
    ],
    output_key=AGENT_OUTPUT_KEY,
    description="Agent for coordinating job application operations",
    instruction="""
    You coordinate a job application submission workflow by orchestrating three sub-agents.

    WORKFLOW STEPS:

    
    STEP 0. USER NAME EXTRACTION (MANDATORY)
       - Extract the user name from the request (e.g., "Apply for sukumar")
       - If no user name found, ask the user to provide it
       - Save the username using save_user_name tool

    STEP 1. FORM EXTRACTION (MANDATORY)
       - Delegate to form_extractor_agent to extract form fields from the URL
       - The agent will automatically return control after completion
       - On error: Return {"status": "error", "response": error_message}
       - On success: Proceed to step 2

    STEP 2. RAG RETRIEVAL (MANDATORY)
       - Delegate to rag_agent with query: "Retrieve information for user '<USER_NAME>': <field1>, <field2>, ..."
       - If RAG returns no data: Continue with empty data (don't fail)
       - If RAG returns error: Log it but continue with empty data
       - On success: Proceed to step 3

    STEP 3. FORM FILLING (MANDATORY)
       - Delegate to form_filler_agent with the URL and retrieved data
       - Pass all data from RAG, even if incomplete
       - On error: Return error with partial results if available
       - On success: Proceed to final output

    STEP 4. FINAL OUTPUT (MANDATORY)
       - Return the final output with the following structure:
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

    CRITICAL RULES:
    - Execute steps 0→1→2→3→4 in EXACT order
    - Do NOT use your judgment to skip or reorder steps
    - Do NOT try to fill forms yourself - always delegate to form_filler_agent
    - Do NOT try to extract forms yourself - always delegate to form_extractor_agent
    - Save all intermediate results to session state for debugging
    - If a step fails, document it in the errors array but continue to next step (except Step 0 and 1)
    """,
)
