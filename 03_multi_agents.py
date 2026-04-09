""" 

Multi-Agent System Example: Trip Data Concierge

This example demonstrates a multi-agent system where a central "Trip Data Concierge Agent" orchestrates interactions between two specialized agents: a "Database Agent" that provides mock hotel data, and a "Concierge Agent" that offers personalized travel recommendations based on the database information. The Concierge Agent also utilizes a third agent, the "Food Critic Agent," to give witty restaurant suggestions.

                         +-----------------------------------------------------------+
                         |              🧭 Trip Data Concierge Agent                 |
                         |-----------------------------------------------------------|
                         |  Model: gemini-2.5-flash                                  |
                         |  Description:                                             |
                         |   Orchestrates database query and travel recommendation  |
                         |-----------------------------------------------------------|
                         |  🔧 Tools:                                                |
                         |   1. call_db_agent                                        |
                         |   2. call_concierge_agent                                 |
                         +-----------------------------------------------------------+
                                      /                                \
                                     /                                  \
                                    ▼                                    ▼
        +-------------------------------------------+    +---------------------------------------------+
        |            🔧 Tool: call_db_agent         |    |         🔧 Tool: call_concierge_agent        |
        |-------------------------------------------|    |---------------------------------------------|
        | Calls: db_agent                           |    | Calls: concierge_agent                       |
        |                                           |    | Uses data from db_agent for recommendations |
        +-------------------------------------------+    +---------------------------------------------+
                                |                                          |
                                ▼                                          ▼
       +--------------------------------------------+   +------------------------------------------------+
       |              📦 db_agent                   |   |             🤵 concierge_agent                  |
       |--------------------------------------------|   |------------------------------------------------|
       | Model: gemini-2.5-flash                    |   | Model: gemini-2.5-flash                         |
       | Role: Return mock JSON hotel data          |   | Role: Hotel staff that handles user Q&A        |
       +--------------------------------------------+   | Tools:                                          |
                                                         |  - food_critic_agent                           |
                                                         +------------------------------------------------+
                                                                                 |
                                                                                 ▼
                                                       +------------------------------------------------+
                                                       |          🍽️ food_critic_agent                  |
                                                       |------------------------------------------------|
                                                       | Model: gemini-2.5-flash                         |
                                                       | Role: Gives a witty restaurant recommendation   |
                                                       +------------------------------------------------+

"""

import asyncio
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.tools.tool_context import ToolContext
from utils.runner import run_agent_query, session_service, my_user_id

# Define the Database Agent
db_agent = Agent(
    name="db_agent",
    model="gemini-2.5-flash",
    description="Returns mock JSON hotel data for a requested destination.",
    instruction="""You are a hotel database system.
    When asked about a destination, return a structured JSON with mock hotel data.
    Always respond ONLY with a valid JSON like this example:

    {
        "destination": "Paris",
        "hotels": [
            {
                "name": "Hotel Le Marais",
                "stars": 4,
                "price_per_night_usd": 210,
                "highlights": ["Central location", "Free breakfast", "Rooftop bar"]
            },
            {
                "name": "Montmartre Boutique Inn",
                "stars": 3,
                "price_per_night_usd": 130,
                "highlights": ["Artistic neighborhood", "Cozy rooms", "Near Sacré-Cœur"]
            }
        ]
    }

    Adapt the hotel names, prices, and highlights to fit the actual destination.""",
    tools=[]
)

# Define the Food Critic Agent
food_critic_agent = Agent(
    name="food_critic_agent",
    model="gemini-2.5-flash",
    description="Gives a witty restaurant recommendation based on the destination.",
    instruction="""You are a witty and opinionated food critic.
    When given a destination, recommend ONE iconic local restaurant with:
    - The restaurant name
    - The must-order dish
    - A witty one-liner about why it's unmissable.
    Keep it short, punchy, and memorable.""",
    tools=[]
)

# Define the Concierge Agent
concierge_agent = Agent(
    name="concierge_agent",
    model="gemini-2.5-flash",
    description="Hotel staff that handles user Q&A and gives personalized travel recommendations.",
    instruction="""You are a luxury hotel concierge. Your job is to:
    1. Review the hotel data provided by the database
    2. Give personalized recommendations based on the user's needs
    3. ALWAYS call the food_critic_agent tool for a restaurant suggestion
    4. Present a warm, professional concierge-style response that includes:
       - Which hotel you recommend and why
       - The restaurant suggestion from the food critic
       - 2-3 local activity tips
    Speak like real hotel staff — polished but approachable.""",
    tools=[AgentTool(agent=food_critic_agent)]
)

# Define tools for the Trip Data Concierge Agent to call the other agents
call_db_agent_tool = AgentTool(agent=db_agent)
call_concierge_agent_tool = AgentTool(agent=concierge_agent)

# Define the Trip Data Concierge Agent (Orchestrator)
trip_data_concierge_agent = Agent(
    name="trip_data_concierge_agent",
    model="gemini-2.5-flash",
    description="Orchestrates database query and travel recommendation for trip planning.",
    instruction="""You are the central Trip Data Concierge. Follow this exact workflow:
    1. Use call_db_agent to retrieve hotel data for the requested destination
    2. Pass that hotel data to call_concierge_agent so it can give personalized recommendations
    3. Present the final combined response to the user in a clean, organized format

    Always complete BOTH steps before responding to the user.
    Never skip the database query.""",
    tools=[call_db_agent_tool, call_concierge_agent_tool]
)

# Main function to run the agent query
async def main():
    session = await session_service.create_session(
        app_name=trip_data_concierge_agent.name,
        user_id=my_user_id
    )
    print(f"✅ Sesión creada: {session.id}\n")

    await run_agent_query(
        agent=trip_data_concierge_agent,
        query="I'm planning a trip to Tokyo. Can you help me find a good hotel and things to do?",
        session=session,
        user_id=my_user_id
    )

if __name__ == "__main__":
    asyncio.run(main())