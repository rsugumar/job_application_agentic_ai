from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from config import retry_config
from .config import AGENT_MODEL, AGENT_NAME, AGENT_OUTPUT_KEY
from rag.agent import rag_agent
from form_agent.agent import form_extractor_agent, form_filler_agent


job_application_coordinator_agent = LlmAgent(
    model=Gemini(model=AGENT_MODEL, retry_options=retry_config),
    name=AGENT_NAME,
    sub_agents=[form_extractor_agent, rag_agent, form_filler_agent],
    output_key=AGENT_OUTPUT_KEY,
    description="Agent for coordinating job application operations",
    instruction="""
    Route user requests: Use form_extractor_agent to extract all form fields in the form, use rag_corpus_manager to retrieve the relevant information for the required fields and fill out the form using form_filler_agent.
    
    - Use emojis to make responses more friendly and readable:
      - ✅ for success
      - ❌ for errors
      - ℹ️ for info
      - 🗂️ for lists
    
    Steps:
    1. Use form_extractor_agent to extract all form fields in the form.
    2. Use rag_agent to retrieve the relevant information for the extracted form fields.
    3. Use form_filler_agent to fill out the form using the retrieved information.
    
    Return the final response with the dictionary format that has the key "status" and "response".
    If the operation is successful, the "status" should be "success" and "response" should contain the result. The result should contain the list of form fields.
    If the operation fails, the "status" should be "error" and "response" should contain the error message.
    """,
)
