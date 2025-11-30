from dotenv import load_dotenv

import asyncio
from google.adk.runners import InMemoryRunner


from job_application_coordinator.agent import job_application_coordinator_agent

load_dotenv()

async def main():
    runner = InMemoryRunner(agent=job_application_coordinator_agent)   
    print("Running coordinator agent verification...")

    try:
        response = await runner.run_debug("Apply to this job for sukumar: https://joinstellar.ai/apply/senior-software-engineer/register/", verbose=True)
        print("Response:", response)
    except Exception as e:
        print(f"Execution failed (expected if tools need real environment): {e}")

if __name__ == "__main__":
    asyncio.run(main())
