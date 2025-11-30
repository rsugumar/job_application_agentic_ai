from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

# from google.adk.sessions import DatabaseSessionService
# from google.adk.sessions import InMemorySessionService

from config import retry_config
from form_agent.config import AGENT_MODEL, FILLER_AGENT_NAME, FILLER_AGENT_OUTPUT_KEY, EXTRACTOR_AGENT_NAME, EXTRACTOR_AGENT_OUTPUT_KEY


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
    
    Steps:
    1. Extract the URL from the user's request.
    2. Navigate to the URL using playwright_mcp tool.
    3. Snapshot the form fully and note down the form fields as a list.
    
    Return the final response with the dictionary format that has the keys "status", "response", and "url".
    If the operation is successful, the "status" should be "success", "response" should contain the list of form fields, and "url" should contain the form URL.
    Example: {"status": "success", "response": ["Full Name", "Email", "Phone", "Resume"], "url": "https://example.com/apply"}
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
    You are a helpful assistant that fills out forms using playwright_mcp tool by using the available information.

    Steps:
    1. Extract the URL from the previous agent's response (look for "url" field).
    2. Navigate to that URL using playwright_mcp tool.
    3. Fill out the form using the information provided from the RAG agent (from the previous response).
    4. Don't fill out the field particularly when the information is not available for the field.
    5. Don't close the browser after filling out the form.
    
    Return the final response with the dictionary format that has the key "status" and "response".
    If the operation is successful, the "status" should be "success" and "response" should contain the result. The result should contain the fields that were filled out in dictionary format.
    If the operation fails, the "status" should be "error" and "response" should contain the error message.
    """,
)
