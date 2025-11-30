from google.adk.agents import SequentialAgent, LlmAgent
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

    WORKFLOW:
    1. FORM EXTRACTION: Call form_extractor_agent with the URL to get form fields.
    Input: {"url": "https://..."}
    Expected Output: {"status": "success", "response": ["field1", "field2", ...], "url": "..."}
    Error Handling: If status=="error", immediately return {"status": "error", "response": <error_message>}
    
    2. RAG RETRIEVAL: Call rag_agent to retrieve user information.
    Input: Construct query from extracted fields
    Query Format: "Retrieve information for: <field1>, <field2>, ..."
    Expected Output: {"status": "success", "response": {<field_data>}, "url": "..."}
    Error Handling: If no data found, proceed with empty dict {}
    
    3. FORM FILLING: Call form_filler_agent to fill the form.
    Input: {"url": <from_step1>, "data": <from_step2>}
    Expected Output: {"status": "success", "response": {"filled_fields": [...], "unfilled_fields": [...]}}
    
    FINAL OUTPUT FORMAT:
    {
        "status": "success" | "error",
        "response": {
            "filled_fields": [{"field": "name", "value": "..."}],
            "unfilled_fields": ["field_name"],
            "errors": []
        },
        "metadata": {
            "url": "...",
            "total_fields": N,
            "filled_count": M
        }
    }
    """,
)

# job_application_coordinator_agent = SequentialAgent(
#     name="job_application_pipeline",
#     sub_agents=[form_extractor_agent, rag_agent, form_filler_agent],
#     description="Agent for coordinating job application operations",
# )
