from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

# from google.adk.sessions import DatabaseSessionService
# from google.adk.sessions import InMemorySessionService

from config import retry_config
from form_agent.config import AGENT_MODEL, FILLER_AGENT_NAME, FILLER_AGENT_OUTPUT_KEY, EXTRACTOR_AGENT_NAME, EXTRACTOR_AGENT_OUTPUT_KEY, COORDINATOR_AGENT_NAME, COORDINATOR_AGENT_OUTPUT_KEY

# Playwright MCP integration
playwright_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",  # Run MCP server via npx
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@playwright/mcp@latest",
            ],
        ),
        timeout=60,
    )
)
print("✅ Playwright MCP Tool created")


# Create form extractor agent that uses playwright mcp tool to extract form details
form_extractor_agent = LlmAgent(
    model=Gemini(model=AGENT_MODEL, retry_options=retry_config),
    name=EXTRACTOR_AGENT_NAME,
    tools=[playwright_mcp],
    output_key=EXTRACTOR_AGENT_OUTPUT_KEY,
    description="Agent for extracting form details using Playwright MCP Tool",
    instruction="""
    You are a helpful assistant that parses and extracts form details and outputs in dictionary format.
    Your primary goal is to open the given url using Playwright MCP Tool to extract form details.
    
    - Use emojis to make responses more friendly and readable:
      - ✅ for success
      - ❌ for errors
      - ℹ️ for info
      - 🗂️ for lists
    
    Steps:
    1. Open the given URL using Playwright MCP Tool.
    2. Parse the form fully and understand the form fields.
    3. Extract the form fields and return it in dictionary format.
    
    Return the final response with the dictionary format that has the key "status" and "response".
    If the operation is successful, the "status" should be "success" and "response" should contain the result. The result should contain the list of form fields.
    If the operation fails, the "status" should be "error" and "response" should contain the error message.
    """,
)

# Create form filling agent that uses playwright mcp tool to fill out forms
form_filler_agent = LlmAgent(
    model=Gemini(model=AGENT_MODEL, retry_options=retry_config),
    name=FILLER_AGENT_NAME,
    tools=[playwright_mcp],
    output_key=FILLER_AGENT_OUTPUT_KEY,
    description="Agent for filling out forms using Playwright MCP Tool",
    instruction="""
    You are a helpful assistant that fills out forms using Playwright MCP Tool by using information from {rag_response}.
    Your primary goal is to open the given url using Playwright MCP Tool to fill out the form using the information {rag_response} if available.
    
    - Use emojis to make responses more friendly and readable:
      - ✅ for success
      - ❌ for errors
      - ℹ️ for info
      - 🗂️ for lists
    
    Steps:
    1. Open the given URL using Playwright MCP Tool.
    2. Fill out the form using the information {rag_response} if available.
    3. Don't fill out the form if the information is not available.
    4. Don't close the browser after filling out the form.
    
    Return the final response with the dictionary format that has the key "status" and "response".
    If the operation is successful, the "status" should be "success" and "response" should contain the result. The result should contain the fields that were filled out in dictionary format.
    If the operation fails, the "status" should be "error" and "response" should contain the error message.
    """,
)

# form coordinator agent
form_coordinator_agent = LlmAgent(
    model=Gemini(model=AGENT_MODEL, retry_options=retry_config),
    name=COORDINATOR_AGENT_NAME,
    tools=[AgentTool(agent=form_extractor_agent), AgentTool(agent=form_filler_agent)],
    output_key=COORDINATOR_AGENT_OUTPUT_KEY,
    description="Agent for coordinating form operations",
    instruction="""
    Route user requests: Use form_extractor_agent to extract form details and form_filler_agent to fill out the form.
    
    First use form_extractor_agent to extract form details and then use form_filler_agent to fill out the form when {rag_response} is available.
    
    - Use emojis to make responses more friendly and readable:
      - ✅ for success
      - ❌ for errors
      - ℹ️ for info
      - 🗂️ for lists
    
    Return the final response with the dictionary format that has the key "status" and "response".
    """,
)
