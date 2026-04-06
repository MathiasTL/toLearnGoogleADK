import os
import asyncio
from dotenv import load_dotenv
import vertexai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

load_dotenv()

#Vertex AI initialization
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"]      = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"]     = LOCATION

vertexai.init(project=PROJECT_ID, location=LOCATION)
session_service = InMemorySessionService()
my_user_id = "mathias_001"

# Runner function to execute an agent query and print the response
async def run_agent_query(
    agent: Agent,
    query:str,
    session,
    user_id: str,
    is_router: bool = False
):
    print(f"\n🚀 Agente: '{agent.name}' | Sesión: '{session.id}'")
    print(f"📝 Query: {query}")
    print("-" * 50)
    
    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=agent.name
    )
    
    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=Content(parts=[Part(text=query)], role="user")
        ):
            if not is_router:
                print(f"📨 Evento: {event}")
                if event.is_final_response:
                    final_response = event.content.parts[0].text
    except Exception as e:
        final_response = f"❌ Error: {str(e)}"
    if not is_router:
        print(f"✅ Respuesta final: {final_response}")
        print("-" * 50)
    
    return final_response