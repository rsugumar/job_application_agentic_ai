from google.adk.agents import LlmAgent

from rag.agent import rag_agent
from form_agent.agent import form_coordinator_agent


job_application_coordinator_agent = LlmAgent(
    name="JobApplicationCoordinator",
    model="gemini-2.0-flash",
    description="Main job application coordinator agent.",
    instruction="""
    Route user requests: Use RAG agent for RAG operations, Form coordinator agent for form details extraction and form filling operations.
    1. Use Form coordinator agent to extract the form details first.
    2. Use RAG agent to retrieve the relevant information for the extracted form.
    3. Use Form coordinator agent to fill out the form using the retrieved information.
    """,
    # allow_transfer=True is often implicit with sub_agents in AutoFlow
    sub_agents=[rag_agent, form_coordinator_agent]
)
