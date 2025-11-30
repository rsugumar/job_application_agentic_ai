import asyncio
from dotenv import load_dotenv

from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner

from job_application_coordinator.agent import job_application_coordinator_agent
from config import APP_NAME, USER_ID, SESSION_ID

load_dotenv()

async def main():
    job_application_app_compacting = App(
        name=APP_NAME,
        root_agent=job_application_coordinator_agent,
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=3,  # Trigger compaction every 3 invocations
            overlap_size=1,  # Keep 1 previous turn for context
        ),
    )

    db_url = "sqlite+aiosqlite:///my_agent_data.db"
    session_service = DatabaseSessionService(db_url=db_url)

    job_application_runner_compacting = Runner(
        app=job_application_app_compacting, session_service=session_service
    )

    try:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
    except Exception:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )

    try:
        response = await job_application_runner_compacting.run_debug(
            "Apply to this job for sukumar: https://joinstellar.ai/apply/senior-software-engineer/register/",
            user_id=USER_ID,
            session_id=SESSION_ID,
            verbose=True
        )
        print("Response:", response)
    except Exception as e:
        print(f"Execution failed (expected if tools need real environment): {e}")

if __name__ == "__main__":
    asyncio.run(main())
