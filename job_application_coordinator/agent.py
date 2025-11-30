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
    You coordinate a job application workflow by calling sub-agents in sequence.
    
    Steps:
    1. Call form_extractor_agent with the URL to get form fields
       - Extract the list of fields from its response["response"]
       - If status is "error", stop and return the error
       - Close the browser after extracting the form fields.
    
    2. Call rag_agent to retrieve user information
       - Pass through the user name.
       - Construct a query like: "Retrieve the following information about the user: [comma-separated field names]"
       - Extract the retrieved data from its response["response"]
       - If no data found, proceed with empty data
    
    3. Call form_filler_agent to fill the form
       - Pass the URL and the RAG data
       - Request format: "Fill out the form at [URL] with this data: [RAG results]"
    
    Return format: {"status": "success/error", "response": {"filled_fields": [...], "errors": [...]}}
    """,
)

# job_application_coordinator_agent = SequentialAgent(
#     name="job_application_pipeline",
#     sub_agents=[form_extractor_agent, rag_agent, form_filler_agent],
#     description="Agent for coordinating job application operations",
# )
