from google.genai import types

APP_NAME = "job_application_app"
USER_ID = "test_user"
SESSION_ID = "my_session_name"

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)
