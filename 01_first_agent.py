"""
My First Agent

The day_trip_agent is a simple but powerful assistant. We're making it a little smarter by teaching it to understand budget constraints.

    Agent: The brain of the operation, defined by its instructions, tools, and the AI model it uses.
    Session: The conversation history. For this simple agent, it's just a container for a single request-response.
    Runner: The engine that connects the Agent and the Session to process your request and get a response.
    

+--------------------------------------------------+
|         Spontaneous Day Trip Agent 🤖            |
|--------------------------------------------------|
|  Model: gemini-2.5-flash                         |
|  Description:                                    |
|   Generates full-day trip itineraries based on   |
|   mood, interests, and budget                    |
|--------------------------------------------------|
|  🔧 Tools:                                       |
|   - Google Search                                |
|--------------------------------------------------|
|  🧠 Capabilities:                                |
|   - Budget Awareness (cheap / splurge)           |
|   - Mood Matching (adventurous, relaxing, etc.)  |
|   - Real-Time Info (hours, events)               |
|   - Morning / Afternoon / Evening plan           |
+--------------------------------------------------+

            ▲
            |
    +------------------+
    |   User Input     |
    |------------------|
    |  Mood            |
    |  Interests       |
    |  Budget          |
    +------------------+

            |
            ▼

+--------------------------------------------------+
|             Output: Markdown Itinerary           |
|--------------------------------------------------|
| - Time blocks (Morning / Afternoon / Evening)    |
| - Venue names with links and hours               |
| - Budget-matching activities                     |
+--------------------------------------------------+

"""

import asyncio
from google.adk.agents import Agent
from google.adk.tools import google_search
from utils.runner import run_agent_query, session_service, my_user_id

# Define the agent with instructions and tools
day_trip_agent = Agent(
    name="day_trip_agent",
    model="gemini-2.5-flash",
    instruction="""
        You are the "Spontaneous Day Trip" Generator 🚗 - a specialized AI assistant that creates engaging full-day itineraries.

        Your Mission:
        Transform a simple mood or interest into a complete day-trip adventure with real-time details, while respecting a budget.

        Guidelines:
        1. **Budget-Aware**: Pay close attention to budget hints like 'cheap', 'affordable', or 'splurge'. Use Google Search to find activities (free museums, parks, paid attractions) that match the user's budget.
        2. **Full-Day Structure**: Create morning, afternoon, and evening activities.
        3. **Real-Time Focus**: Search for current operating hours and special events.
        4. **Mood Matching**: Align suggestions with the requested mood (adventurous, relaxing, artsy, etc.).

        RETURN itinerary in MARKDOWN FORMAT with clear time blocks and specific venue names.
        """,
    tools=[google_search]
)

# Create a session for the agent
async def main():
    session = await session_service.create_session(
        user_id=my_user_id,
        app_name=day_trip_agent.name
    )
    print(f"✅ Sesión creada → ID: {session.id} | Usuario: {my_user_id}")
    
    # Example query to the agent
    await run_agent_query(
        agent=day_trip_agent,
        query="Plan a day trip to Cusco, Peru for someone on a budget who loves history and culture.",
        session=session,
        user_id=my_user_id
    )
    
if __name__ == "__main__":
    asyncio.run(main())