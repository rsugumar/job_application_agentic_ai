# Agent Settings
AGENT_MODEL = "gemini-2.5-flash-lite"

EXTRACTOR_AGENT_NAME = "form_extractor_agent"
EXTRACTOR_AGENT_OUTPUT_KEY = "form_extractor_agent_response"

FILLER_AGENT_NAME = "form_filler_agent"
FILLER_AGENT_OUTPUT_KEY = "form_filler_agent_response"

COORDINATOR_AGENT_NAME = "form_coordinator_agent"
COORDINATOR_AGENT_OUTPUT_KEY = "form_coordinator_agent_response"

# Timeout configurations (in milliseconds)
BROWSER_TIMEOUT = 30000  # 30 seconds for browser operations
PAGE_LOAD_TIMEOUT = 60000  # 60 seconds for page loads
ELEMENT_WAIT_TIMEOUT = 10000  # 10 seconds for element waits
MCP_CONNECTION_TIMEOUT = 90  # 90 seconds for MCP connection
