from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from config import retry_config
from form_agent.config import (
    AGENT_MODEL, 
    FILLER_AGENT_NAME, 
    FILLER_AGENT_OUTPUT_KEY, 
    EXTRACTOR_AGENT_NAME, 
    EXTRACTOR_AGENT_OUTPUT_KEY,
    MCP_CONNECTION_TIMEOUT,
    BROWSER_TIMEOUT,
    PAGE_LOAD_TIMEOUT,
    ELEMENT_WAIT_TIMEOUT
)



# Playwright MCP integration with timeout configuration
# NOTE: By sharing the same McpToolset instance across agents, we maintain browser state
playwright_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",  # Run MCP server via npx
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@playwright/mcp@latest",
            ],
            env={
                "PLAYWRIGHT_TIMEOUT": str(BROWSER_TIMEOUT),
                "PLAYWRIGHT_NAVIGATION_TIMEOUT": str(PAGE_LOAD_TIMEOUT),
            }
        ),
        timeout=MCP_CONNECTION_TIMEOUT,
    )
)
print("✅ Playwright MCP Tool created with shared session for browser state persistence")



# Create form extractor agent that uses playwright mcp tool to extract form details
form_extractor_agent = LlmAgent(
    model=Gemini(model=AGENT_MODEL, retry_options=retry_config),
    name=EXTRACTOR_AGENT_NAME,
    tools=[playwright_mcp],
    output_key=EXTRACTOR_AGENT_OUTPUT_KEY,
    description="Agent for extracting form details using Playwright MCP Tool",
    instruction=f"""
    You are a helpful assistant that parses and extracts form details and outputs in dictionary format.
    Your primary goal is to open the given url using Playwright MCP Tool to extract form details.
    
    Steps:
    1. Extract the URL from the user's request.
    2. Navigate to the URL using playwright_mcp tool (timeout: {PAGE_LOAD_TIMEOUT/1000}s).
       - If navigation times out, return error status immediately.
    3. Wait for the page to fully load (max {PAGE_LOAD_TIMEOUT/1000}s).
    4. Snapshot the form fully and note down ALL form fields as a list.
       - Include field labels, input types, and any required/optional indicators.
    5. **CRITICAL: DO NOT CLOSE THE BROWSER** - The browser session must remain open for the form_filler_agent.
    
    Return the final response with the dictionary format that has the keys "status", "response", and "url".
    If the operation is successful, the "status" should be "success", "response" should contain the list of form fields, and "url" should contain the form URL.
    Example: {{"status": "success", "response": ["Full Name", "Email", "Phone", "Resume"], "url": "https://example.com/apply"}}
    If the operation fails (timeout, navigation error, etc.), the "status" should be "error" and "response" should contain the error message.
    """,
)

# Create form filling agent that uses playwright mcp tool to fill out forms
form_filler_agent = LlmAgent(
    model=Gemini(model=AGENT_MODEL, retry_options=retry_config),
    name=FILLER_AGENT_NAME,
    tools=[playwright_mcp],
    output_key=FILLER_AGENT_OUTPUT_KEY,
    description="Agent for filling out forms using Playwright MCP Tool",
    instruction=f"""
    You are a helpful assistant that fills out forms using playwright_mcp tool by using the available information.

    Steps:
    1. **REUSE THE EXISTING BROWSER SESSION** - The browser is already open from form_extractor_agent.
       - Extract the URL from the previous agent's response (look for "url" field).
       - Check if you're already on the correct page. If not, navigate to the URL.
    2. Fill out the form using the information provided from the RAG agent (from the previous response).
       - Use element wait timeout of {ELEMENT_WAIT_TIMEOUT/1000}s for each field.
       - If an element is not found within timeout, add it to unfilled_fields.
    3. **IMPORTANT**: Only fill fields where you have corresponding data from the RAG agent.
       - Don't fill out the field when the information is not available.
       - Track which fields were filled and which were skipped.
    4. Don't close the browser after filling out the form (user may want to review).
    
    Return the final response with the dictionary format that has the key "status" and "response".
    If the operation is successful, the "status" should be "success" and "response" should contain:
    - "filled_fields": List of fields that were successfully filled with their values
    - "unfilled_fields": List of fields that could not be filled (missing data or element not found)
    Example: {{\"status\": \"success\", \"response\": {{\"filled_fields\": [{{\"field\": \"Full Name\", \"value\": \"John Doe\"}}], \"unfilled_fields\": [\"Resume\"]}}}}
    If the operation fails, the "status" should be "error" and "response" should contain the error message.
    """,
)
