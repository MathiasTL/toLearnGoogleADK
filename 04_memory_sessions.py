import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

#In this archive, NOT import utils/runner.py because our goal is to understand the difference between remember and forget.

import os
from dotenv import load_dotenv
import vertexai


"""
+-----------------------------------------------------+
|         Adaptive Multi-Day Trip Agent 🗺️           |
|-----------------------------------------------------|
|  Model: gemini-2.5-flash                            |
|  Description:                                       |
|   Builds multi-day travel itineraries step-by-step, |
|   remembers previous days, adapts to feedback       |
|-----------------------------------------------------|
|  🔧 Tools:                                          |
|   - Google Search                                   |
|-----------------------------------------------------|
|  🧠 Capabilities:                                   |
|   - Memory of past conversation & preferences       |
|   - Progressive planning (1 day at a time)          |
|   - Adapts to user feedback                         |
|   - Ensures activity variety across days            |
+-----------------------------------------------------+

            ▲
            |
    +---------------------------+
    |     User Interaction      |
    |---------------------------|
    | - Destination             |
    | - Trip duration           |
    | - Interests & feedback    |
    +---------------------------+

            |
            ▼

+-----------------------------------------------------+
|        Day-by-Day Itinerary Generation              |
|-----------------------------------------------------|
|  🗓️ Day N Output (Markdown format):                 |
|   - Morning / Afternoon / Evening activities        |
|   - Personalized & context-aware                    |
|   - Changes accepted, feedback acknowledged         |
+-----------------------------------------------------+

            |
            ▼

+-----------------------------------------------------+
|        Next Day Planning Triggered 🚀               |
|-----------------------------------------------------|
| - Builds on prior days                              |
| - Avoids repetition                                 |
| - Asks user for confirmation before proceeding      |
+-----------------------------------------------------+

"""

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION   = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Define agent for the two sessions
travel_memory_agent = Agent(
    name="travel_memory_agent",
    model="gemini-2.5-flash",
    description="A travel assistant that remembers user preferences within a session.",
    instruction="""You are a helpful travel assistant.
    Remember everything the user tells you during the conversation.
    When asked about previous preferences or information, 
    refer back to what was discussed earlier in this session.""",
    tools=[]
)

#Simplified runner for the chat
async def chat(runner: Runner, user_id: str, session_id: str, message: str):
    """Sends a message and prints the agent's response."""
    print(f"\n👤 User: {message}")
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=Content(parts=[Part(text=message)], role="user")
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text

    print(f"🤖 Agent: {response_text}")
    return response_text

# First session: User provides preferences, agent should remember them
async def scenario_same_session():
    print("\n" + "=" * 60)
    print("ESCENARIO 3a: Misma sesión → El agente RECUERDA")
    print("=" * 60)
    
    session_service = InMemorySessionService()
    user_id = "traveler 001"
    APP_NAME = travel_memory_agent.name
    
    #one session for all interactions
    session = await session_service.create_session(
        user_id=user_id,
        app_name=APP_NAME
    )
    
    print(f"Session ID: {session.id}")
    
    runner = Runner(
        agent=travel_memory_agent,
        session_service=session_service,
        app_name=APP_NAME
    )
    
    # Turn 1 - User provides preferences
    await chat(runner, user_id, session.id,
               "Hi! My name is Mathias and I love hiking and local food.")

    # Turn 2 - User asks for travel recommendation based on preferences
    await chat(runner, user_id, session.id,
               "Based on my interests, where should I travel in South America?")

    # Turn 3 - Direct reference to something said before
    await chat(runner, user_id, session.id,
               "Do you remember what my name is and what I told you I enjoy?")

    print("\n✅ Resultado: El agente recuerda todo porque usamos la MISMA sesión.")
    
# Second session: User provides preferences, but agent should NOT remember them
async def scenario_different_sessions():
    print("\n" + "=" * 60)
    print("ESCENARIO 3b: Diferentes sesiones → El agente NO recuerda")
    print("="*60)
    
    session_service = InMemorySessionService()
    user_id         = "traveler_001"
    APP_NAME        = travel_memory_agent.name

    runner = Runner(
        agent=travel_memory_agent,
        session_service=session_service,
        app_name=APP_NAME
    )
    
    # Session 1: User provides preferences
    session1 = await session_service.create_session(
        user_id=user_id,
        app_name=APP_NAME
    )
    print(f"Session 1 ID: {session1.id}")
    
    await chat(runner, user_id, session1.id,
               "Hi! My name is Mathias and my dream destination is Patagonia.")

    await chat(runner, user_id, session1.id,
               "What's a good month to visit Patagonia?")
    
    # Session 2: User asks about preferences, but it's a new session
    session2 = await session_service.create_session(
        user_id=user_id,
        app_name=APP_NAME
    )
    print(f"Session 2 ID: {session2.id}")
    
    await chat(runner, user_id, session2.id,
               "Do you remember what my name is and where I wanted to travel?")

    print("\n❌ Resultado: El agente no recuerda nada porque es una SESIÓN NUEVA.")
    
async def main():
    await scenario_same_session()
    await scenario_different_sessions()

    print("\n" + "=" * 60)
    print("💡 CONCLUSIÓN:")
    print("   InMemorySessionService guarda el historial POR sesión.")
    print("   Misma session_id  → el agente recuerda.")
    print("   Nueva session_id  → el agente empieza desde cero.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())